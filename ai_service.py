import base64
import io
import os
import tempfile

import google.generativeai as genai
import pytesseract
from gtts import gTTS
from langdetect import detect
from PIL import Image

from config import ALLOWED_SUBJECTS, GEMINI_API_KEY


class AITutorService:
    def __init__(self):
        # Configure Gemini API
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        self.vision_model = genai.GenerativeModel('gemini-1.5-pro-vision')
        
        # Initialize empty chat sessions dict
        self.chat_sessions = {}

    def get_chat_session(self, subject):
        """Get or create a chat session for the given subject"""
        if subject not in self.chat_sessions:
            # Initialize new chat session
            self.chat_sessions[subject] = self.model.start_chat(history=[])
            
            # Set up the initial context
            prompt = f"""You are an expert tutor in {subject}. Your role is to:
            1. Help students understand concepts clearly
            2. Provide practical examples
            3. Answer questions patiently
            4. Give constructive feedback
            5. Encourage learning through practice
            
            Please maintain a friendly and supportive tone while being professional."""
            self.chat_sessions[subject].send_message(prompt)
            
        return self.chat_sessions[subject]

    def process_image(self, image_file):
        """Extract text from an image using OCR"""
        img = Image.open(image_file)
        text = pytesseract.image_to_string(img)
        return text

    def encode_image(self, image_file):
        """Encode image for Gemini API"""
        if isinstance(image_file, str):
            with open(image_file, "rb") as f:
                image_bytes = f.read()
        else:
            image_file.seek(0)
            image_bytes = image_file.read()

        return {"mime_type": "image/jpeg", "data": base64.b64encode(image_bytes).decode("utf-8")}

    def detect_language(self, text):
        """Detect the language of input text"""
        try:
            return detect(text)
        except:
            return "en"  # Default to English if detection fails

    def text_to_speech(self, text, language="en"):
        """Convert text to speech"""
        speech = gTTS(text=text, lang=language, slow=False)
        fp = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        speech.save(fp.name)
        return fp.name

    def ask_question(self, question, subject, grade_level, image_file=None, language="en"):
        """Ask a question and get a response"""
        try:
            if image_file:
                # Handle image upload
                image = Image.open(image_file)
                response = self.vision_model.generate_content([question, image])
                text_response = response.text
            else:
                # Text-only question
                chat_session = self.get_chat_session(subject)
                response = chat_session.send_message(question)
                text_response = response.text

            # Generate audio response if needed
            audio_file = None
            if language != "en":
                audio_file = self.text_to_speech(text_response, language)

            return {
                "text_response": text_response,
                "audio_file": audio_file
            }
        except Exception as e:
            return {
                "text_response": f"I apologize, but I encountered an error: {str(e)}",
                "audio_file": None
            }

    def generate_practice_questions(self, subject, topic, difficulty="medium"):
        """Generate practice questions based on subject and topic"""
        try:
            prompt = f"""Generate 3 practice questions for {subject} topic: {topic}
            Difficulty level: {difficulty}
            Include:
            1. Clear question statement
            2. Multiple choice options
            3. Correct answer
            4. Brief explanation
            
            Format the output in markdown."""
            
            chat_session = self.get_chat_session(subject)
            response = chat_session.send_message(prompt)
            return response.text
        except Exception as e:
            return f"Error generating questions: {str(e)}"

    def evaluate_answer(self, question, student_answer, subject, grade_level):
        """Evaluate student's answer and provide feedback"""
        try:
            prompt = f"""Evaluate this student's answer for the following question:
            
            Question: {question}
            
            Student's Answer: {student_answer}
            
            Please provide:
            1. Score (0-100)
            2. Detailed feedback
            3. Suggestions for improvement
            4. Key concepts to review
            
            Format the response in markdown."""
            
            chat_session = self.get_chat_session(subject)
            response = chat_session.send_message(prompt)
            return response.text
        except Exception as e:
            return f"Error evaluating answer: {str(e)}" 