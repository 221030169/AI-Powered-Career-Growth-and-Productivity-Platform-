# llm_parser.py
import ollama
import json
import re
from config import OLLAMA_HOST, OLLAMA_MODEL_NAME, OLLAMA_EMBEDDING_MODEL_NAME
from logger import time_function
# Initialize Ollama client
client = None  
try:
    client = ollama.Client(host=OLLAMA_HOST)
    
except Exception as e:
    print(f"Error connecting to Ollama at {OLLAMA_HOST}: {e}")
    print("Please ensure Ollama is running and the specified model is downloaded.")
    client = None # Set client to None if connection fails


@time_function
def _call_ollama(prompt, model=OLLAMA_MODEL_NAME, context=None):
    """Helper function to call Ollama model with error handling."""
    if client is None:
        return None # Return None if client wasn't initialized

    messages = [{"role": "user", "content": prompt}]
    if context:
        # Prepend context as a system message for better instruction following
        messages.insert(0, {"role": "system", "content": f"Here is the relevant text context to extract information from:\n\n{context}"})

    try:
        response = client.chat(
            model=model,
            messages=messages,
            stream=False # We want the full response
        )
        return response['message']['content']
    except Exception as e:
        print(f"Error calling OLLAMA ({model}) at {OLLAMA_HOST}: {type(e).__name__}: {e}")
        return None

    
def _parse_llm_json_output(llm_output):
    """
    Robustly extracts the first valid JSON block (array or object) from the LLM output.
    Handles extra text, markdown, multiple JSON snippets.
    """
    if not llm_output:
        return None

    llm_output = llm_output.strip()

    # Step 1: Try extracting from ```json ... ``` block
    match = re.search(r'```json\s*(.*?)\s*```', llm_output, re.DOTALL)
    if match:
        candidate = match.group(1).strip()
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass  # Try fallbacks

    # Step 2: Try first valid array-like JSON
    arrays = re.findall(r'(\[\s*[\s\S]*?\])', llm_output)
    for arr in arrays:
        try:
            return json.loads(arr)
        except json.JSONDecodeError:
            continue

    # Step 3: Try object-like JSON
    objects = re.findall(r'(\{\s*[\s\S]*?\})', llm_output)
    for obj in objects:
        try:
            return json.loads(obj)
        except json.JSONDecodeError:
            continue

    # Step 4: Try last resort fallback — clean and try parsing entire string
    try:
        cleaned = llm_output.replace('```json', '').replace('```', '').strip()
        return json.loads(cleaned)
    except Exception as e:
        print(f"JSON decoding failed: {type(e).__name__}: {e}")
        print(f"⚠️ Raw LLM output (first 300 chars):\n{llm_output[:300]}...\n")
        return None

def get_embedding(text):
    """Generates an embedding for the given text using the specified embedding model."""
    if client is None:
        return None
    try:
        response = client.embeddings(
            model=OLLAMA_EMBEDDING_MODEL_NAME,
            prompt=text
        )
        return response['embedding']
    except Exception as e:
        print(f"Error generating embedding with OLLAMA ({OLLAMA_EMBEDDING_MODEL_NAME}): {e}")
        return None
 

# --- LLM Parsing Functions for specific fields ---
@time_function
def extract_name_with_llm(text_context):
    """Extracts the full name from the given text context."""
    prompt = f"""
    Based on the following resume text, extract ONLY the full name of the candidate.
    Return only the name string, without any additional text, labels, or punctuation.
    If the name is not clearly identifiable, return "N/A".

    Context:
    {text_context}
    """
    name = _call_ollama(prompt, context=text_context)
    return name.strip() if name else "N/A"

@time_function
def extract_skills_with_llm(text_context):
    """
    Extracts a list of skills from the given text context.
    Returns a JSON array of strings.
    """
    prompt = f"""
    From the provided resume text, identify and list all distinct technical skills, programming languages, software, tools, and methodologies. Focus on the candidate's actual technical abilities and proficiency, typically found in a 'Skills' or 'Technical Expertise' section, or explicitly mentioned in job descriptions.
    Return the skills as a JSON array of strings. Each string should be a single skill.
    If no relevant skills are found, return an empty JSON array: [].

    Example JSON format (always an array of strings):
    ```json
    [
        "Python",
        "Data Analysis",
        "SQL",
        "Machine Learning",
        "React",
        "Cloud Computing (AWS)"
    ]
    ```

    Resume Context:
    {text_context}
    """
    llm_output = _call_ollama(prompt, context=text_context)
    parsed_data = _parse_llm_json_output(llm_output)
    # Ensure it's a list, otherwise return empty
    return parsed_data if isinstance(parsed_data, list) else []

@time_function
def extract_experience_with_llm(text_context):
    """
    Extracts a list of formal work experience entries from the given text context,
    EXCLUDING project or assignment-based experience.
    Returns a JSON array of objects.
    """
    prompt = f"""
    From the provided resume text, extract ONLY formal work experience entries.
    Focus exclusively on instances where the candidate held a specific 'title' at a 'company' (employer) during a defined period ('start_date' and 'end_date').
    **DO NOT include any entries that describe projects, assignments, freelancing, or client-based work. Focus strictly on traditional employment history.**

    For each formal employment entry, extract the following fields and adhere strictly to the date logic and formatting:

    - 'title': The job title (e.g., "Senior Software Engineer").
    - 'company': The name of the employer.
    - 'start_date': The start date of the employment (YYYY-MM format, or YYYY if only year is available).
    - 'end_date': The end date of the employment (YYYY-MM format, or YYYY if only year is available, or 'Present' if ongoing).
    - 'description': A concise summary of responsibilities, achievements, and key duties.

    Return ALL extracted formal employment entries as a JSON array of objects. If no formal employment entries are found, return an empty JSON array: [].

    Example JSON format for multiple entries (focus on formal employment, and strict date formats):
    ```json
    [
        {{
            "title": "Principal Pavement Engineer",
            "company": "ADG Mobility Pvt. Ltd., India",
            "start_date": "2021-11",
            "end_date": "Present",
            "description": "Responsible for detailed engineering design of pavements, project management, and quality control."
        }},
        {{
            "title": "Lecturer",
            "company": "Eduardo Mondlane University",
            "start_date": "1987-01",
            "end_date": "1997-12",
            "description": "Taught various civil engineering subjects and supervised student projects."
        }},
        {{
            "title": "Head of Pavement Design",
            "company": "Infrastructure Solutions Inc.",
            "start_date": "2015-03",
            "end_date": "2021-10",
            "description": "Managed a team of engineers, oversaw pavement design projects from conceptualization to completion."
        }}
    ]
    ```
    Resume Context:
    {text_context}
    """
    llm_output = _call_ollama(prompt, context=text_context) # Use unified call
    parsed_data = _parse_llm_json_output(llm_output)
    return parsed_data if isinstance(parsed_data, list) else []

@time_function
def extract_education_with_llm(text_context):
    """
    Extracts a list of education entries from the given text context.
    Returns a JSON array of objects.
    """
    prompt = f"""
    From the provided resume text, extract ALL education entries.
    For each entry, extract the following:
    - 'degree': The full degree obtained (e.g., "Master of Science in Computer Science").
    - 'institution': The name of the university or institution.
    - 'year': The year of completion (YYYY format).

    Return ALL education entries as a JSON array of objects. If no education entries are found, return an empty JSON array: [].

    Example JSON format:
    ```json
    [
        {{
            "degree": "Master of Technology (M. Tech.) in Transportation Systems Engineering",
            "institution": "Indian Institute of Technology (IIT), Bombay",
            "year": "1990"
        }},
        {{
            "degree": "Bachelor of Engineering (B.E.) (Civil) Hons",
            "institution": "Malviya National Institute of Technology (MNIT), Jaipur, Rajasthan, India",
            "year": "1987"
        }}
    ]
    ```

    Resume Context:
    {text_context}
    """
    llm_output = _call_ollama(prompt, context=text_context) 
    parsed_data = _parse_llm_json_output(llm_output)
    return parsed_data if isinstance(parsed_data, list) else []

@time_function
def extract_projects_with_llm(text_context):
    """
    Extracts project entries.
    Returns a JSON array of objects.
    """
    prompt = f"""
    From the following resume text, extract all relevant project entries. Each entry should include:
    - project_name or Name of assignment (the name of the project)
    - client_company (Optional) The name of the client company or organization for whom the project was done. If not explicitly mentioned, infer or return "N/A".
    - role (your role in the project, if specified)(optional).
    - description (a concise summary of the project and your contributions).
    - technologies_used (a list of technologies/skills used in the project, if specified).

    Return the projects as a JSON array of objects. If no projects are found, return an empty JSON array: [].

    Example JSON format:
    ```json
    [
        {{
            "project_name": "E-commerce Recommendation System",
            "client_company": "Retail Innovations Inc.",
            "role": "Lead Developer",
            "description": "Developed a real-time recommendation engine using collaborative filtering; Improved user engagement by 15%.",
            "technologies_used": ["Python", "TensorFlow", "Kafka", "PostgreSQL"]
        }},
        {{
            "project_name": "Personal Portfolio Website",
            "client_company": "Self-project",
            "role": "Full-stack Developer",
            "description": "Built and deployed a personal portfolio site showcasing projects and skills.",
            "technologies_used": ["React", "Node.js", "MongoDB", "AWS S3"]
        }},
        {{
            "project_name": "Road Construction Project in Mozambique",
            "client_company": "ADMINISTRAÇÃO NACIONAL DE ESTRADAS, I.P., MOZAMBIQUE",
            "role": "Geotechnical/Materials Engineer",
            "description": "Preparation of Feasibility Study, Conceptual Design, Environmental and Social Impact Assessment, Resettlement Action Plan, Bidding Documents and Procurement Support for civil works under design and build methodology for roads N381, N380, and N762 in Cabo Delgado province, Mozambique.",
            "technologies_used": ["Design and Build Methodology", "Feasibility Study", "Environmental Impact Assessment"]
        }}
    ]
    ```

    Resume Context:
    {text_context}
    """
    llm_output = _call_ollama(prompt, context=text_context) # Use unified call
    parsed_data = _parse_llm_json_output(llm_output)
    return parsed_data if isinstance(parsed_data, list) else []

@time_function
def extract_certifications_with_llm(text_context):
    """
    Extracts a list of certifications from the given text context.
    Returns a JSON array of objects.
    """
    prompt = f"""
    From the provided resume text, identify and extract ALL distinct certifications, professional licenses, and formal training programs and also if the resume has heading i.e Other Training.
    For each entry, include:
    - 'name': The full name of the certification or training.
    - 'issuing_body': (Optional) The organization or institution that issued it. If not found, return "N/A".
    - 'dates': (Optional) The date of completion or validity (e.g., "2022-05", "2023", "2024-Expiration"). If not found, return "N/A".

    Return ALL certifications as a JSON array of objects. If no certifications are found, return an empty JSON array: [].

    Example JSON format for multiple entries:
    ```json
    [
        {{
            "name": "Project Management Professional (PMP)",
            "issuing_body": "PMI",
            "dates": "2021-08"
        }},
        {{
            "name": "AWS Certified Solutions Architect - Associate",
            "issuing_body": "Amazon Web Services",
            "dates": "2023-12-Expiration"
        }},
        {{
            "name": "Sub – Urban Railway System, Training",
            "issuing_body": "Indian Railway Institute of Civil Engineering",
            "dates": "2005"
        }}
    ]
    ```

    Resume Context:
    {text_context}
    """
    llm_output = _call_ollama(prompt, context=text_context) # Use unified call
    parsed_data = _parse_llm_json_output(llm_output)
    return parsed_data if isinstance(parsed_data, list) else []

@time_function
def extract_languages_with_llm(text_context):
    """
    Extracts a list of languages and their proficiency levels.
    Attempts to parse a table-like structure if present.
    Returns a JSON array of objects.
    """
    prompt = f"""
    From the provided resume text, identify and extract ALL distinct languages spoken by the candidate, along with their corresponding proficiency levels for speaking, reading, and writing.
    If proficiency levels are not explicitly stated for a category (e.g., only "Fluent" overall), infer them as 'Fluent' for all categories. Use 'Native' or 'Mother tongue' for highest proficiency. If no level is given, use 'N/A'.
    Return the languages as a JSON array of objects. If no languages are found, return an empty JSON array: [].

    Example JSON format (always an array of objects):
    ```json
    [
        {{
            "language": "English",
            "speaking": "Fluent",
            "reading": "Excellent",
            "writing": "Excellent"
        }},
        {{
            "language": "Hindi",
            "speaking": "Native",
            "reading": "Mother tongue",
            "writing": "Mother tongue"
        }},
        {{
            "language": "Bengali",
            "speaking": "Mother tongue",
            "reading": "Mother tongue",
            "writing": "Mother tongue"
        }},
        {{
            "language": "Arabic",
            "speaking": "Beginner",
            "reading": "Beginner",
            "writing": "Beginner"
        }}
    ]
    ```

    Resume Context:
    {text_context}
    """
    llm_output = _call_ollama(prompt, context=text_context) # Use unified call
    parsed_data = _parse_llm_json_output(llm_output)
    return parsed_data if isinstance(parsed_data, list) else []