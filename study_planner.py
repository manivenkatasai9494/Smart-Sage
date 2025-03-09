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
        
        Please provide a structured daily plan that includes:
        1. Subject rotation to maintain engagement
        2. Specific topics to focus on
        3. Recommended study methods
        4. Short breaks between sessions
        5. Progress check points
        
        Format the plan as a JSON structure with days as keys and detailed hourly schedules.
        """
        
        response = self.model.generate_content(prompt)
        try:
            plan = json.loads(response.text)
            return self._format_study_plan(plan)
        except:
            # Fallback to text format if JSON parsing fails
            return {"text": response.text, "structured": False}

    def _format_study_plan(self, plan_data):
        """Format the study plan into a structured format"""
        formatted_plan = {
            "daily_schedules": plan_data,
            "structured": True,
            "summary": self._generate_plan_summary(plan_data)
        }
        return formatted_plan

    def _generate_plan_summary(self, plan_data):
        """Generate a summary of the study plan"""
        total_hours = 0
        subject_hours = {}
        
        for day, schedule in plan_data.items():
            for session in schedule["sessions"]:
                duration = float(session["duration"].split()[0])
                subject = session["subject"]
                total_hours += duration
                subject_hours[subject] = subject_hours.get(subject, 0) + duration
        
        summary = {
            "total_hours": total_hours,
            "subject_distribution": subject_hours,
            "days_covered": len(plan_data)
        }
        return summary

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