import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Application Settings
APP_NAME = "AI Learning Companion"
DATA_DIR = "student_data"
ALLOWED_SUBJECTS = ["math", "physics", "chemistry"]
DEFAULT_LANGUAGE = "en"
DEFAULT_DIFFICULTY = "medium"

# File Upload Settings
ALLOWED_IMAGE_TYPES = ["jpg", "jpeg", "png"]
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB

# Session Settings
MAX_CHAT_HISTORY = 50
MAX_PRACTICE_QUESTIONS = 10