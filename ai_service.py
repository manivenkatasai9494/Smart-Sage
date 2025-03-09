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
        self.api_key = GEMINI_API_KEY
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")

        # System prompts for different subjects
        self.subject_prompts = {
            "math": "You are a helpful, patient, and encouraging math tutor for school students. Provide clear, step-by-step explanations for math problems. Break down complex concepts into simple terms. Use examples to illustrate concepts. Adjust your explanations based on the student's grade level.",
            "physics": "You are a helpful, patient, and encouraging physics tutor for school students. Explain physics concepts with real-world examples. Provide step-by-step solutions to physics problems. Use analogies to make abstract concepts concrete. Include diagrams when beneficial.",
            "chemistry": "You are a helpful, patient, and encouraging chemistry tutor for school students. Explain chemical concepts clearly. Draw connections between theory and everyday applications. Break down chemical reactions step by step. Use visualizations to illustrate molecular structures and reactions."
        }

        # Create chat sessions for each subject
        self.chat_sessions = {
            subject: self.model.start_chat(history=[]) for subject in ALLOWED_SUBJECTS
        }

        # Initialize each chat with its system prompt
        for subject, prompt in self.subject_prompts.items():
            self.chat_sessions[subject].send_message(prompt)

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
        """Process a student's question and return an appropriate response"""
        try:
            # Build context-specific prompt
            context_prompt = f"I am a grade {grade_level} student. "

            # Process image if provided
            image_content = None
            extracted_text = ""
            if image_file:
                # Try OCR first
                extracted_text = self.process_image(image_file)
                # Also prepare the image for direct model processing
                image_content = self.encode_image(image_file)

            # Prepare the full prompt with all context
            full_prompt = context_prompt + question
            if extracted_text:
                full_prompt += f"\n\nText extracted from my image: {extracted_text}"

            # Get language-specific instructions if not English
            if language != "en":
                full_prompt += f"\n\nPlease respond in {language} language."

            # Send to the appropriate chat session with or without image
            if image_content:
                response = self.chat_sessions[subject].send_message(
                    [full_prompt, image_content]
                )
            else:
                response = self.chat_sessions[subject].send_message(full_prompt)

            # Generate audio if needed
            audio_file = None
            if language != "en" or True:  # Always generate for now, can make optional
                audio_file = self.text_to_speech(response.text, language)

            return {
                "text_response": response.text,
                "audio_file": audio_file,
            }

        except Exception as e:
            return {
                "text_response": f"I encountered an error: {str(e)}. Please try again.",
                "audio_file": None
            }

    def generate_practice_questions(self, subject, topic, difficulty, num_questions=5):
        """Generate practice questions on a specific topic"""
        prompt = f"Generate {num_questions} {difficulty} level practice questions about {topic} in {subject} for students. Include answers and detailed explanations for each question."
        response = self.model.generate_content(prompt)
        return response.text

    def evaluate_answer(self, question, student_answer, subject, grade_level):
        """Evaluate a student's answer to a question"""
        prompt = f"""As a tutor, evaluate this grade {grade_level} student's answer:

        Question: {question}
        Student's Answer: {student_answer}

        Provide:
        1. Is the answer correct? (Yes/No/Partially)
        2. The correct solution if the student's answer is wrong
        3. Detailed explanation of any mistakes
        4. Suggestions for improvement
        """

        response = self.chat_sessions[subject].send_message(prompt)
        return response.text