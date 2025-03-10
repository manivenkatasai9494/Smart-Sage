import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Application Settings
APP_NAME = "StudyBud - AI Learning Companion"
DATA_DIR = "data"

# Create data directory if it doesn't exist
os.makedirs(DATA_DIR, exist_ok=True)

# Allowed subjects
ALLOWED_SUBJECTS = [
    "programming",
    "web_dev",
    "mobile_dev",
    "ai",
    "software_eng",
    "networks",
    "databases",
    "os",
    "architecture"
]

# Subject display names
SUBJECT_DISPLAY_NAMES = {
    "programming": "Programming",
    "web_dev": "Web Development",
    "mobile_dev": "Mobile Development",
    "ai": "Artificial Intelligence",
    "software_eng": "Software Engineering",
    "networks": "Computer Networks",
    "databases": "Database Systems",
    "os": "Operating Systems",
    "architecture": "Computer Architecture"
}

# Application Settings
DEFAULT_LANGUAGE = "en"
DEFAULT_DIFFICULTY = "medium"

# File Upload Settings
ALLOWED_IMAGE_TYPES = ["jpg", "jpeg", "png"]
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB

# Session Settings
MAX_CHAT_HISTORY = 50
MAX_PRACTICE_QUESTIONS = 10 