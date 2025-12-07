# regex_parser.py
import os
import re
import json
from datetime import datetime
import time

# Import paths from config
from config import EXTRACTED_TEXT_DIR, REGEX_PARSED_RESULTS_DIR, CV_FILES_DIR  
from logger import performance_logger, time_function
# Import preprocessing function
from preprocess_cv import preprocess_cvs

# Import ALL LLM parsing functions from llm_parser.py
from llm_parser import (
    get_embedding,
    _call_ollama, 
    extract_name_with_llm,
    extract_skills_with_llm,
    extract_experience_with_llm,
    extract_education_with_llm,
    extract_projects_with_llm,
    extract_certifications_with_llm,
    extract_languages_with_llm
)




def clean_text_for_parsing(text):
    """
    Performs final, light cleaning and normalization within the parser,
    after preprocess_cv.py has done its main work.
    This mostly ensures consistent line endings and space compression,
    and removes any residual non-ASCII that might have slipped through
    or been re-introduced (though unlikely with the aggressive first pass).
    """
    
    text = re.sub(r'\r\n|\r', '\n', text) # Normalize all line endings to \n
    text = re.sub(r'[ \t]+', ' ', text) 
    text = re.sub(r'\n{3,}', '\n\n', text) 
    text = re.sub(r'[^\x00-\x7F\n]+', ' ', text) # Keep basic ASCII and newlines
    return text.strip()


def extract_contact_info(text):
    contact_info = {"email": None, "phone_numbers": [], "urls": []}

    # Email
    email_matches = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    if email_matches:
        unique_emails_ordered = sorted(list(set(email_matches)), key=text.find)
        if unique_emails_ordered:
            contact_info["email"] = unique_emails_ordered[0]

    # Phone Numbers
    phone_matches = re.findall(
        r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{4,6}\b',
        text
    )

    valid_phones = []
    for phone in set(phone_matches):
        normalized_phone = re.sub(r'[()\s.-]', '', phone)
        if len(normalized_phone) >= 10 and len(normalized_phone) <= 15 and normalized_phone.replace('+', '').isdigit():
            if len(normalized_phone) == 10 and not normalized_phone.startswith(('+', '0')):
                normalized_phone = '+' + normalized_phone
            elif len(normalized_phone) == 11 and normalized_phone.startswith('0'):
                normalized_phone = '+91' + normalized_phone[1:]
            valid_phones.append(normalized_phone)
    contact_info["phone_numbers"] = list(set(valid_phones))

    # ✅ Correct URL Extraction
    url_matches = re.findall(r'https?://[^\s)>\]"]+', text)
    contact_info["urls"] = list(set(url_matches))

    return contact_info

def chunk_text(text, max_chunk_size=1500, overlap=80):
    """
    Chunks text into smaller pieces with overlap for RAG.
    Prioritizes splitting at natural boundaries (e.g., double newlines).
    """
    chunks = []
    paragraphs = text.split('\n\n') # Split by double newlines (paragraphs)
    current_chunk = ""

    for para in paragraphs:
        # Check if adding the current paragraph exceeds max_chunk_size
        # +2 for potential \n\n if this isn't the last paragraph
        if len(current_chunk) + len(para) + 2 <= max_chunk_size:
            current_chunk += (para + '\n\n')
        else:
            if current_chunk: # If current_chunk is not empty, add it
                chunks.append(current_chunk.strip())
            current_chunk = para + '\n\n' # Start a new chunk with the current paragraph

            # If a single paragraph is too large, split it further
            while len(current_chunk) > max_chunk_size:
                # Find a good split point (last space before max_chunk_size)
                split_point = current_chunk.rfind(' ', 0, max_chunk_size)
                if split_point == -1: # No space found, force split at max_chunk_size
                    split_point = max_chunk_size
                chunks.append(current_chunk[:split_point].strip())
                current_chunk = current_chunk[split_point:].strip()

    if current_chunk: # Add any remaining text as a chunk
        chunks.append(current_chunk.strip())

    # Add overlap if desired (simplified for this context, can be more sophisticated)
    final_chunks = []
    for i, chunk in enumerate(chunks):
        if i > 0:
            overlap_text = chunks[i-1][-overlap:] if len(chunks[i-1]) > overlap else chunks[i-1]
            final_chunks.append(overlap_text + '\n' + chunk)
        else:
            final_chunks.append(chunk)

    return [c for c in final_chunks if c] # Filter out any empty chunks
@time_function
def retrieve_relevant_chunks(full_text_content, query, chunk_embeddings, chunk_texts, top_k=3):
    """
    Retrieves top_k most relevant chunks based on a query.
    """
    query_embedding = get_embedding(query)
    if not query_embedding:
        print("DEBUG: Failed to get embedding for query. Skipping RAG for this query.")
        return []

    similarities = []
    for i, chunk_embed in enumerate(chunk_embeddings):
        
        if chunk_embed:
            similarity = sum(qe * ce for qe, ce in zip(query_embedding, chunk_embed))
            similarities.append((similarity, i,))

    # Sort by similarity in descending order
    similarities.sort(key=lambda x: x[0],reverse=True)

    # Retrieve top_k chunks
    relevant_chunks = []
    for _, index in similarities[:top_k]:
        relevant_chunks.append(chunk_texts[index])
    performance_logger.info(f"Retrieved {len(relevant_chunks)} relevant chunks for query: {query[:50]}...")
    return relevant_chunks

def extract_section(text, section_name):
    """
    Extracts text content for a specific section based on typical CV headings.
    Improved to handle variations and potential trailing text.
    It looks for the section name (case-insensitive, optionally with spaces around)
    followed by content, up until another common CV section header or end of document.
    """
     
    # the target section (e.g., "EDUCATION" followed by "EXPERIENCE", not "SKILLS")
    common_headers_regex = r"(?:EXPERIENCE|WORK HISTORY|Academics|PROFESSIONAL EXPERIENCE|PROJECTS|PUBLICATIONS|AWARDS|LANGUAGES|CERTIFICATIONS|TRAINING|REFERENCES|SUMMARY|PROFILE|SKILLS|EDUCATION|QUALIFICATIONS)\s*:"
    
    # Regex to capture content between section_name and the next section header or end of document
    # It tries to be flexible with leading/trailing whitespace around headers
    pattern = re.compile(
        rf"(?:^|\n\s*){re.escape(section_name)}\s*(?:\n+|:)?\s*(.*?)(?=\n\s*{common_headers_regex}|\Z)",
        re.DOTALL | re.IGNORECASE
    )
    match = pattern.search(text)
    if match:
        return match.group(1).strip()
    return None

def post_process_experience(experience_list, education_list):
    """
    Removes education-like entries from the experience list if they overlap with education.
    """
    filtered_experience = []
    # Keywords often found in education titles/descriptions
    education_keywords = ["m.tech", "iit", "university", "bachelor", "degree", "ph.d", "master", "college", "institute", "diploma", "honours", "hons"]

    for exp_entry in experience_list:
        # --- NEW CHECK ADDED HERE ---
        if not isinstance(exp_entry, dict):
            print(f"WARNING: Skipping non-dictionary entry found in experience list: {exp_entry}")
            continue # Skip this entry if it's not a valid dictionary

        is_education_entry = False
        exp_title = exp_entry.get("title", "").lower()
        exp_description = exp_entry.get("description", "").lower()
        exp_company = exp_entry.get("company", "").lower()

        # Check if title or description contains education-related keywords
        if any(keyword in exp_title for keyword in education_keywords) or \
           any(keyword in exp_description for keyword in education_keywords):
            
            # Further check for overlap with actual education entries for higher confidence
            for edu_entry in education_list:
                edu_institution = edu_entry.get("institution", "").lower()
                edu_degree = edu_entry.get("degree", "").lower()
                edu_year_str = edu_entry.get("year", "") # Year is usually just a number, might be string

                # Convert education year to int if possible for comparison
                edu_num_year = None
                if edu_year_str and edu_year_str.isdigit():
                    edu_num_year = int(edu_year_str)

                # Check for institution match or degree match
                # Using 'in' for partial matches as names might vary slightly
                institution_match = (edu_institution and (edu_institution in exp_company or edu_institution in exp_description or edu_institution in exp_title))
                degree_match = (edu_degree and (edu_degree in exp_title or edu_degree in exp_description))

                if institution_match or degree_match:
                    # Attempt a simple date overlap check if dates are available
                    exp_start_year = None
                    exp_end_year = None
                    try:
                        if exp_entry.get("start_date"):
                            exp_start_year = int(exp_entry["start_date"].split('-')[0])
                        if exp_entry.get("end_date"):
                            # Handle "Present" or "till date" for end_date by using current year
                            if exp_entry["end_date"].lower() in ["present", "till date"]:
                                exp_end_year = datetime.now().year
                            else:
                                exp_end_year = int(exp_entry["end_date"].split('-')[0])
                    except ValueError:
                        pass # Date format might be irregular, skip date check

                    if edu_num_year and exp_start_year and exp_end_year:
                        # Check if education year falls within experience period
                        if exp_start_year <= edu_num_year <= exp_end_year:
                            is_education_entry = True
                            break
                    elif edu_num_year and (edu_num_year == exp_start_year or edu_num_year == exp_end_year):
                         # If only start or end year matches education year exactly
                         is_education_entry = True
                         break
                    elif not exp_start_year and not exp_end_year and (institution_match or degree_match):
                        # If experience has no dates, rely purely on keyword/institution/degree match
                        is_education_entry = True
                        break

        if not is_education_entry:
            filtered_experience.append(exp_entry)
            
    return filtered_experience


# --- Main Parsing Pipeline ---

@time_function # Apply the decorator here
def parse_cv_with_pipeline(file_path):
    performance_logger.info(f"Processing: {os.path.basename(file_path)}")
    parsed_data = {
        "file_name": os.path.basename(file_path),
        "name": None,
        "contact_info": {"email": None, "phone_numbers": [], "urls": []}, # Initialize to ensure keys exist
        "skills": [],
        "experience": [],
        "education": [],
        "projects": [],
        "certifications": [],
        "languages": []
    }

    with open(file_path, 'r', encoding='utf-8') as f:
        raw_text_content = f.read()

    clean_text_content = clean_text_for_parsing(raw_text_content) # Assuming text is already preprocessed

    # --- Step 1: Initial Regex Extraction (Name, Contact Info) ---
    # Name - Try LLM first for better accuracy
    name_query = "What is the full name of the candidate in this resume?"
    # Pass a reasonable portion of the text where the name is likely found
    name_llm = extract_name_with_llm(clean_text_content[:2000]) # Increased context for name
    if name_llm and name_llm.strip() != "N/A":
        parsed_data["name"] = name_llm.strip()
        performance_logger.info(f"    Name (LLM): {parsed_data['name']}")
    else:
        # Fallback regex if LLM fails (less accurate, but a backup)
        # Tries to find capitalized words at the beginning, usually a name
        name_match = re.search(r'^[A-Z][a-z]+(?:\s[A-Z][a-z]+){1,3}', clean_text_content[:500])
        if name_match:
            parsed_data["name"] = name_match.group(0).strip()
            performance_logger.info(f"    Name (Regex Fallback): {parsed_data['name']}")
        else:
            parsed_data["name"] = "N/A"
            performance_logger.info(f"    Name (Regex Fallback): {parsed_data['name']} (Not Found)")

    # Contact Info (Email, Phone, URLs) - Best handled by regex
    contact_info = extract_contact_info(clean_text_content)
    parsed_data["contact_info"] = contact_info
    performance_logger.info(f"    Email: {parsed_data['contact_info']['email']}")
    performance_logger.info(f"    Phone: {', '.join(parsed_data['contact_info']['phone_numbers'])}")
    performance_logger.info(f"    URLs: {', '.join(parsed_data['contact_info']['urls'])}")

    # --- Step 2: RAG Pipeline for other sections ---
    # Generate chunks and embeddings for the entire document once
    chunk_texts = chunk_text(clean_text_content)
    # Filter out any None embeddings
    # chunk_embeddings_start_time = time.time()
    # chunk_embeddings = [get_embedding(chunk) for chunk in chunk_texts]
    # chunk_embeddings_filtered = [embed for embed in chunk_embeddings if embed is not None]
    # chunk_texts_filtered = [chunk_texts[i] for i, embed in enumerate(chunk_embeddings) if embed is not None]
    # chunk_enbedding_end_time = time.time()
    # total_time = chunk_enbedding_end_time - chunk_embeddings_start_time
    # performance_logger.info(f"Total get_embedding execution time: {total_time:.4f} seconds")
    # performance_logger.info(f"Generating embeddings for {len(chunk_texts_filtered)} usable chunks...")


    # Skills
    skills_query = "List of distinct technical skills, programming languages, software, tools, and methodologies from this resume."
    # Corrected call: removed redundant clean_text_content argument
    # skills_chunks = retrieve_relevant_chunks(clean_text_content,skills_query, chunk_embeddings_filtered, chunk_texts_filtered, top_k=5)
    # performance_logger.debug(f"Retrieved {len(skills_chunks)} chunks for skills. Context length: {len(' '.join(skills_chunks))} chars.")
    # performance_logger.debug(f"Context for Skills (first 800 chars):\n{' '.join(skills_chunks)[:800]}...") # Removed for brevity in log, use for deep debugging
    parsed_data["skills"] = extract_skills_with_llm(' '.join(chunk_texts)) # Changed to use all filtered chunks
    performance_logger.info(f"    Skills (LLM via RAG): {len(parsed_data['skills'])} entries")

    # Experience
    experience_query = "Candidate's work experience, employment history, EMPLOYMENT RECORD RELEVANT TO THE ASSIGNMENT, job titles, companies, start and end dates, and responsibilities."
    # Corrected call: removed redundant clean_text_content argument
    # experience_chunks = retrieve_relevant_chunks(clean_text_content,experience_query, chunk_embeddings_filtered, chunk_texts_filtered, top_k=12)
    # performance_logger.debug(f"Retrieved {len(experience_chunks)} chunks for experience. Context length: {len(' '.join(experience_chunks))} chars.")
    # performance_logger.debug(f"Context for Experience (first 1500 chars):\n{' '.join(experience_chunks)[:1000]}...") # Removed for brevity in log
    parsed_data["experience"] = extract_experience_with_llm(' '.join(chunk_texts))
    performance_logger.info(f"    Experience (LLM via RAG): {len(parsed_data['experience'])} entries")

    # Projects
    projects_query = "List of projects, assignments, or key deliverables with descriptions, technologies, client_company and dates."
    # Corrected call: removed redundant clean_text_content argument
    # projects_chunks = retrieve_relevant_chunks(clean_text_content, projects_query, chunk_embeddings_filtered, chunk_texts_filtered, top_k=10)
    # performance_logger.debug(f"Retrieved {len(projects_chunks)} chunks for projects. Context length: {len(' '.join(projects_chunks))} chars.")
    parsed_data["projects"] = extract_projects_with_llm(' '.join(chunk_texts))
    performance_logger.info(f"    Projects (LLM via RAG): {len(parsed_data['projects'])} entries")

    # Certifications (Prioritize section extraction, fallback to RAG)
    certifications_section_text = extract_section(clean_text_content, "CERTIFICATIONS")
    if not certifications_section_text: # If "CERTIFICATIONS" not found, try "TRAINING"
        certifications_section_text = extract_section(clean_text_content, "TRAINING")
    
    if certifications_section_text:
        performance_logger.debug(f"Passing to LLM for Certifications (from regex section): First 500 chars:\n{certifications_section_text[:500]}...")
        parsed_data["certifications"] = extract_certifications_with_llm(certifications_section_text)
    else:
        certifications_query = "List of certifications, professional licenses, training programs, and workshops completed."
        # Corrected call: removed redundant clean_text_content argument
        # certifications_chunks = retrieve_relevant_chunks(clean_text_content, certifications_query, chunk_embeddings_filtered, chunk_texts_filtered, top_k=5)
        # performance_logger.debug(f"Retrieved {len(certifications_chunks)} chunks for certifications. Context length: {len(' '.join(certifications_chunks))} chars.")
        parsed_data["certifications"] = extract_certifications_with_llm(' '.join(chunk_texts))
    performance_logger.info(f"    Certifications (LLM): {len(parsed_data['certifications'])} entries") # Changed to LLM, as it might be section or RAG

    # Education (Section extraction is usually robust here)
    education_section_text = extract_section(clean_text_content, "EDUCATION")
    if education_section_text:
        performance_logger.debug(f"Passing to LLM for Education (from regex section): First 500 chars:\n{education_section_text[:500]}...")
        parsed_data["education"] = extract_education_with_llm(education_section_text)
    else:
        # Fallback to RAG if explicit section not found
        education_query = "Academic degrees, diplomas, institutions, and graduation years."
        # Corrected call: removed redundant clean_text_content argument
        # education_chunks = retrieve_relevant_chunks(clean_text_content, education_query, chunk_embeddings_filtered, chunk_texts_filtered, top_k=3)
        # performance_logger.debug(f"Retrieved {len(education_chunks)} chunks for education. Context length: {len(' '.join(education_chunks))} chars.")
        parsed_data["education"] = extract_education_with_llm(' '.join(chunk_texts))
    performance_logger.info(f"    Education (LLM): {len(parsed_data['education'])} entries") # Changed to LLM, as it might be section or RAG

    # Languages (Force RAG to handle the table format, increased top_k)
    languages_query = "List of languages spoken, reading and writing proficiency levels from a table."
    # Corrected call: removed redundant clean_text_content argument
    # languages_chunks = retrieve_relevant_chunks(clean_text_content, languages_query, chunk_embeddings_filtered, chunk_texts_filtered, top_k=3)
    if chunk_texts:
        # performance_logger.debug(f"Retrieved {len(languages_chunks)} chunks for languages. Context length: {len(' '.join(languages_chunks))} chars.")
        parsed_data["languages"] = extract_languages_with_llm(' '.join(chunk_texts))
    else:
        performance_logger.info("No relevant chunks found for languages. Languages will be empty.")
        parsed_data["languages"] = [] # Ensure it's an empty list if nothing found
    performance_logger.info(f"    Languages (LLM via RAG): {len(parsed_data['languages'])} entries")

    # --- Post-processing for Experience (to remove education entries misclassified as experience) ---
    original_experience_count = len(parsed_data["experience"])
    parsed_data["experience"] = post_process_experience(parsed_data["experience"], parsed_data["education"])
    performance_logger.info(f"    Experience (After Post-processing): {len(parsed_data['experience'])} entries (removed {original_experience_count - len(parsed_data['experience'])} education-like entries)")


    # --- Final Data Cleaning (remove empty lists/N/A strings) ---
    final_parsed_data = {}
    for key, value in parsed_data.items():
        if isinstance(value, list):
            if value: # Only add non-empty lists
                final_parsed_data[key] = value
        elif isinstance(value, dict):
            # For contact_info, only add if it has at least one non-empty value
            if any(v is not None and (not isinstance(v, list) or v) for v in value.values()):
                final_parsed_data[key] = value
        elif isinstance(value, str):
            if value != "N/A" and value.strip(): # Only add if it's not "N/A" or empty string
                final_parsed_data[key] = value
        else: # For other types like int, bool
            final_parsed_data[key] = value

    performance_logger.info("-" * 40)
    return final_parsed_data

# --- Main Execution Block ---

def main():
    print("---Starting Hybrid Regex + RAG/LLM Parsing Pipeline---")
    start_time = time.time()

    # 1. Preprocess all CVs to plain text
    # Removed CV_FILES_DIR argument as preprocess_cvs() gets it from its own config import.
    processed_files = preprocess_cvs() 

    all_parsed_results = []

    # 2. Iterate through each processed text file and parse
    for file_path in processed_files:
        try:
            parsed_data = parse_cv_with_pipeline(file_path)
            all_parsed_results.append(parsed_data)

            # Save individual JSON results
            output_filename = os.path.splitext(os.path.basename(file_path))[0] + "_parsed.json"
            output_path = os.path.join(REGEX_PARSED_RESULTS_DIR, output_filename)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(parsed_data, f, indent=4)
            performance_logger.info(f"Final parsed data saved to: {output_path}")

        except Exception as e:
            performance_logger.error(f"Error processing {os.path.basename(file_path)}: {type(e).__name__}: {e}", exc_info=True)
            import traceback
            traceback.print_exc() # Print full traceback for deeper debugging
    
    end_time = time.time()
    total_time = end_time - start_time

    
    performance_logger.info(f"Total script execution time: {total_time:.4f} seconds")
    performance_logger.info(f"Processed {len(processed_files)} files.")
    performance_logger.info(f"Results saved to '{REGEX_PARSED_RESULTS_DIR}'.")
    performance_logger.info(f"\n---Program Completed---")

if __name__ == "__main__":
    main()