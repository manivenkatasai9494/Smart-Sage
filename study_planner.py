import json
import os
from datetime import datetime, timedelta

import google.generativeai as genai
import pandas as pd

from config import GEMINI_API_KEY, ALLOWED_SUBJECTS


class StudyPlanner:
    def __init__(self):
        self.api_key = GEMINI_API_KEY
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")

    def generate_study_plan(self, student_data, goals, duration_days=7, hours_per_day=None):
        """Generate a personalized study plan based on student data and goals"""
        # Extract relevant information
        subjects = student_data["subjects"]
        grade = student_data["grade"]
        
        # Analyze student performance
        weak_subjects = []
        for subject, data in subjects.items():
            if data["questions_answered"] > 0 and data["overall_score"] < 70:
                weak_subjects.append((subject, data["overall_score"]))
        
        # Sort weak subjects by score (lowest first)
        weak_subjects.sort(key=lambda x: x[1])
        
        # Create prompt for AI
        prompt = f"""
        Create a detailed {duration_days}-day study plan for a Grade {grade} student with the following parameters:
        
        Student Profile:
        - Grade Level: {grade}
        - Weak Subjects: {', '.join([s[0] for s in weak_subjects]) if weak_subjects else 'None identified yet'}
        
        Goals:
        {goals}
        
        Study Preferences:
        - Available hours per day: {hours_per_day if hours_per_day else 'Flexible'}
        
        Please provide a structured daily plan that follows this EXACT JSON format:
        {{
            "daily_schedules": {{
                "Day 1": {{
                    "sessions": [
                        {{
                            "id": "1",
                            "subject": "math",
                            "topic": "Algebra Basics",
                            "duration": "1 hours",
                            "method": "Video tutorials and practice problems"
                        }}
                    ]
                }}
            }}
        }}

        Important rules:
        1. Use EXACTLY this JSON structure with "daily_schedules" as the root key
        2. Each day must be named "Day X" where X is the day number
        3. Each session must have all five fields: id, subject, topic, duration, method
        4. Subject must be one of: {', '.join(ALLOWED_SUBJECTS)}
        5. Duration must be in the format "X hours" where X is a number
        6. Generate {duration_days} days of content
        """
        
        response = self.model.generate_content(prompt)
        try:
            plan = json.loads(response.text)
            return self._format_study_plan(plan)
        except json.JSONDecodeError:
            # Create a basic structured plan if JSON parsing fails
            basic_plan = {
                "daily_schedules": {
                    f"Day {i+1}": {
                        "sessions": [{
                            "id": str(i*3 + j + 1),
                            "subject": ALLOWED_SUBJECTS[j % len(ALLOWED_SUBJECTS)],
                            "topic": "Review Basics",
                            "duration": "1 hours",
                            "method": "Self-study and practice"
                        } for j in range(3)]
                    } for i in range(duration_days)
                }
            }
            return self._format_study_plan(basic_plan)

    def _format_study_plan(self, plan_data):
        """Format the study plan into a structured format"""
        # Ensure we have the correct structure
        if isinstance(plan_data, dict) and "daily_schedules" in plan_data:
            formatted_plan = plan_data
        else:
            # If we received a different structure, reformat it
            formatted_plan = {
                "daily_schedules": plan_data if isinstance(plan_data, dict) else {}
            }

        formatted_plan["structured"] = True
        formatted_plan["summary"] = self._generate_plan_summary(formatted_plan["daily_schedules"])
        return formatted_plan

    def _generate_plan_summary(self, plan_data):
        """Generate a summary of the study plan"""
        total_hours = 0
        subject_hours = {}
        
        for day, schedule in plan_data.items():
            if isinstance(schedule, dict) and "sessions" in schedule:
                for session in schedule["sessions"]:
                    if isinstance(session, dict) and "duration" in session and "subject" in session:
                        try:
                            duration = float(session["duration"].split()[0])
                            subject = session["subject"]
                            total_hours += duration
                            subject_hours[subject] = subject_hours.get(subject, 0) + duration
                        except (ValueError, AttributeError):
                            continue
        
        return {
            "total_hours": total_hours,
            "subject_distribution": subject_hours,
            "days_covered": len(plan_data)
        }

    def adjust_plan(self, original_plan, feedback):
        """Adjust the study plan based on student feedback"""
        prompt = f"""
        Please adjust the following study plan based on this feedback:
        {feedback}
        
        Current plan:
        {json.dumps(original_plan, indent=2)}
        
        Provide an adjusted plan that addresses the feedback while maintaining the overall structure.
        """
        
        response = self.model.generate_content(prompt)
        try:
            adjusted_plan = json.loads(response.text)
            return self._format_study_plan(adjusted_plan)
        except:
            return {"text": response.text, "structured": False}

    def generate_progress_check(self, plan, completed_tasks):
        """Generate a progress check based on completed tasks"""
        total_tasks = 0
        completed = 0
        
        for day, schedule in plan["daily_schedules"].items():
            total_tasks += len(schedule["sessions"])
            completed += sum(1 for task in schedule["sessions"] if task["id"] in completed_tasks)
        
        completion_rate = (completed / total_tasks) * 100 if total_tasks > 0 else 0
        
        return {
            "completion_rate": completion_rate,
            "total_tasks": total_tasks,
            "completed_tasks": completed,
            "remaining_tasks": total_tasks - completed
        } 