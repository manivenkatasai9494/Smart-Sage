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

    def generate_practice_questions(self, subject, topic, difficulty="medium", question_type="Multiple Choice", num_questions=5):
        """Generate practice questions based on subject and topic"""
        try:
            # Initialize chat session if not exists
            chat_session = self.get_chat_session(subject)
            
            if question_type == "Multiple Choice":
                prompt = f"""Generate {num_questions} {difficulty} level multiple-choice questions about {topic} in {subject}.
                For each question, provide:
                1. Clear question statement
                2. Four options (A, B, C, D)
                3. Correct answer
                4. Brief explanation why the answer is correct
                
                Return the response in this exact JSON format:
                [
                    {{
                        "question": "What is...",
                        "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
                        "correct_answer": "A) ...",
                        "explanation": "This is correct because..."
                    }},
                    ...
                ]"""
            else:
                prompt = f"""Generate {num_questions} {difficulty} level open-ended questions about {topic} in {subject}.
                For each question, provide:
                1. Clear question statement
                2. Key points that should be included in the answer
                3. Sample correct answer
                4. Evaluation criteria
                
                Return the response in this exact JSON format:
                [
                    {{
                        "question": "What is...",
                        "key_points": ["point1", "point2", "point3"],
                        "sample_answer": "A detailed answer...",
                        "evaluation_criteria": "Look for these aspects..."
                    }},
                    ...
                ]"""
            
            # Send message using the initialized chat session
            try:
                response = chat_session.send_message(prompt)
                
                # Extract JSON from response
                import json
                import re

                # Find JSON array in the response
                json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
                if json_match:
                    try:
                        questions = json.loads(json_match.group())
                        if questions and isinstance(questions, list):
                            return questions[:num_questions]  # Ensure we return the requested number of questions
                    except json.JSONDecodeError:
                        print("Failed to parse JSON from match")
                
                # If we get here, either no JSON array was found or parsing failed
                return self._get_offline_questions(subject, topic, question_type, num_questions)
                
            except Exception as e:
                print(f"API request failed: {str(e)}")
                return self._get_offline_questions(subject, topic, question_type, num_questions)
            
        except Exception as e:
            print(f"Error generating questions: {str(e)}")
            return self._get_offline_questions(subject, topic, question_type, num_questions)

    def _get_offline_questions(self, subject, topic, question_type, num_questions):
        """Get pre-defined offline questions when API is unavailable"""
        if question_type == "Multiple Choice":
            # Basic programming questions
            programming_questions = [
                {
                    "question": "What is the primary purpose of a variable in programming?",
                    "options": [
                        "A) To store and manage data",
                        "B) To create user interfaces",
                        "C) To connect to databases",
                        "D) To format code"
                    ],
                    "correct_answer": "A) To store and manage data",
                    "explanation": "Variables are fundamental containers used to store and manage data in programming."
                },
                {
                    "question": "Which of the following is a correct way to comment code in Python?",
                    "options": [
                        "A) // This is a comment",
                        "B) /* This is a comment */",
                        "C) # This is a comment",
                        "D) -- This is a comment"
                    ],
                    "correct_answer": "C) # This is a comment",
                    "explanation": "In Python, single-line comments start with the # symbol."
                },
                {
                    "question": "What is the purpose of a loop in programming?",
                    "options": [
                        "A) To store multiple values",
                        "B) To repeat a block of code",
                        "C) To define functions",
                        "D) To import libraries"
                    ],
                    "correct_answer": "B) To repeat a block of code",
                    "explanation": "Loops are used to execute a block of code multiple times based on a condition."
                },
                {
                    "question": "What is a function in programming?",
                    "options": [
                        "A) A type of variable",
                        "B) A reusable block of code",
                        "C) A database connection",
                        "D) A file format"
                    ],
                    "correct_answer": "B) A reusable block of code",
                    "explanation": "Functions are reusable blocks of code that perform specific tasks when called."
                },
                {
                    "question": "What is the purpose of conditional statements (if/else)?",
                    "options": [
                        "A) To create loops",
                        "B) To define variables",
                        "C) To make decisions in code",
                        "D) To format output"
                    ],
                    "correct_answer": "C) To make decisions in code",
                    "explanation": "Conditional statements allow programs to make decisions based on specific conditions."
                }
            ]
            return programming_questions[:num_questions]
        else:
            # Basic open-ended questions
            open_ended_questions = [
                {
                    "question": "Explain the concept of variables in programming and provide examples.",
                    "key_points": [
                        "Definition of variables",
                        "Types of variables",
                        "Variable naming conventions",
                        "Examples of variable usage"
                    ],
                    "sample_answer": "Variables are containers for storing data values...",
                    "evaluation_criteria": "Understanding of basic programming concepts"
                },
                {
                    "question": "Describe the importance of functions in programming and how they are used.",
                    "key_points": [
                        "Purpose of functions",
                        "Function components",
                        "Function parameters and return values",
                        "Benefits of using functions"
                    ],
                    "sample_answer": "Functions are reusable blocks of code that help organize and modularize programs...",
                    "evaluation_criteria": "Clear explanation of function concepts and benefits"
                },
                {
                    "question": "What are loops in programming and when should they be used?",
                    "key_points": [
                        "Types of loops",
                        "Loop control structures",
                        "Use cases for loops",
                        "Loop efficiency considerations"
                    ],
                    "sample_answer": "Loops are control structures used to repeat a block of code...",
                    "evaluation_criteria": "Understanding of loop concepts and applications"
                }
            ]
            return open_ended_questions[:num_questions]

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