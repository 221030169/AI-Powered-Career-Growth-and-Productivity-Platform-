# config.py
import os

# Base directory for the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Directory where raw CV files are stored (PDF, DOCX)
CV_FILES_DIR = os.path.join(BASE_DIR, 'cv_files')

# Directory where preprocessed plain text from CVs will be saved
EXTRACTED_TEXT_DIR = os.path.join(BASE_DIR, 'extracted_text')

# Directory where final parsed JSON results will be saved
REGEX_PARSED_RESULTS_DIR = os.path.join(BASE_DIR, 'parsed_results')

# Ensure directories exist
os.makedirs(CV_FILES_DIR, exist_ok=True)
os.makedirs(EXTRACTED_TEXT_DIR, exist_ok=True)
os.makedirs(REGEX_PARSED_RESULTS_DIR, exist_ok=True)

# Ollama Configuration
OLLAMA_HOST = "http://localhost:11434"  
OLLAMA_MODEL_NAME = "llama3.2:latest"  
# OLLAMA_MODEL_NAME = "llama3.3-32k:latest"          
OLLAMA_EMBEDDING_MODEL_NAME = "mxbai-embed-large"  # mxbai-embed-large:334m, mxbai-embed-large:latest (335M), nomic-embeded-text (137M)



# mxbai-embed-large:335m, mxbai-embed-large:latest (334M), nomic-embeded-text (137M)