import json
from llm_parser import _call_ollama, _parse_llm_json_output
from config import OLLAMA_MODEL_NAME

def analyze_resume_with_llm(parsed_resume):
    """
    Uses Ollama LLM to generate:
    - Career Growth Potential (0–10)
    - ATS Compatibility (0–100)
    - Recommended Jobs
    Returns a dictionary with all results.
    """

    # Prepare structured input for the LLM
    resume_json = json.dumps(parsed_resume, indent=2)

    prompt = f"""
    You are an expert career and recruitment assistant.

    Below is a candidate's structured resume data in JSON format. 
    Analyze it carefully and provide:
    1. A **Career Growth Potential Score** (0-10) based on experience, education, and skills.
    2. An **ATS Compatibility Score** (0-100) — evaluate section completeness, keyword diversity, and structure.
    3. A **list of 3-5 recommended job roles** that best match the candidate’s profile.
    4. A **short summary (2 sentences)** explaining your reasoning for both scores.

    Return your answer as a clean JSON object exactly like this format:
    ```json
    {{
      "career_growth_score": 8.5,
      "ats_score": 77,
      "recommended_jobs": ["Python Developer", "Data Analyst", "ML Engineer"],
      "summary": "Strong technical base with good experience. Resume could use better keyword optimization."
    }}
    ```

    Candidate Resume JSON:
    {resume_json}
    """

    response = _call_ollama(prompt, model=OLLAMA_MODEL_NAME)
    parsed = _parse_llm_json_output(response)

    if not parsed or not isinstance(parsed, dict):
        return {
            "career_growth_score": "N/A",
            "ats_score": "N/A",
            "recommended_jobs": [],
            "summary": "AI analysis failed or returned an invalid format."
        }

    return parsed