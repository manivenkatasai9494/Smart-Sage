import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Union

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from config import DATA_DIR


class StudentManager:
    def __init__(self):
        """Initialize StudentManager"""
        self.data_dir = DATA_DIR
        os.makedirs(self.data_dir, exist_ok=True)

    def create_student(self, student_id: str, name: str, grade: int, courses: List[str]) -> bool:
        """Create a new student record"""
        if self.student_exists(student_id):
            return False

        student_data = {
            "name": name,
            "grade": grade,
            "courses": courses,
            "joined_date": datetime.now().isoformat(),
            "last_active": datetime.now().isoformat(),
            "progress": {},
            "badges": [],
            "preferences": {
                "language": "en",
                "difficulty_level": "medium"
            },
            "study_preferences": {
                "weekly_hours": 20,
                "preferred_times": ["Morning (9-12 PM)"],
                "learning_styles": {
                    "visual": True,
                    "auditory": False,
                    "practical": False
                }
            },
            "subject_priorities": {},
            "weekly_progress": 0,
            "topics_covered": 0,
            "study_streak": 0
        }

        self._save_student_data(student_id, student_data)
        return True

    def student_exists(self, student_id: str) -> bool:
        """Check if a student exists"""
        return os.path.exists(self._get_student_file_path(student_id))

    def get_student_data(self, student_id: str) -> Dict:
        """Get student data"""
        if not self.student_exists(student_id):
            raise ValueError(f"Student {student_id} not found")

        with open(self._get_student_file_path(student_id), 'r') as f:
            return json.load(f)

    def update_student_data(self, student_id: str, data: Dict) -> None:
        """Update student data"""
        if not self.student_exists(student_id):
            raise ValueError(f"Student {student_id} not found")

        # Update last active timestamp
        data["last_active"] = datetime.now().isoformat()
        
        # Calculate study streak
        last_active = datetime.fromisoformat(data["last_active"])
        current_time = datetime.now()
        if (current_time - last_active).days <= 1:
            data["study_streak"] = data.get("study_streak", 0) + 1
        else:
            data["study_streak"] = 0

        self._save_student_data(student_id, data)

    def get_recommended_topics(self, student_id: str, subject: str) -> List[str]:
        """Get recommended topics based on student progress"""
        student_data = self.get_student_data(student_id)
        progress = student_data.get("progress", {}).get(subject, {})
        
        # Get topics with low progress
        weak_topics = [
            topic for topic, score in progress.items()
            if score < 0.7  # Topics with less than 70% mastery
        ]
        
        return weak_topics[:3] if weak_topics else []

    def generate_performance_report(self, student_id: str) -> Union[str, Dict]:
        """Generate a performance report for the student"""
        if not self.student_exists(student_id):
            return "Student not found"

        student_data = self.get_student_data(student_id)
        progress_data = student_data.get("progress", {})
        
        if not progress_data:
            return "No progress data available yet"

        # Create visualization
        plt.figure(figsize=(12, 6))
        
        # Progress by subject
        subject_progress = []
        for subject, topics in progress_data.items():
            avg_progress = sum(topics.values()) / len(topics) if topics else 0
            subject_progress.append({
                "Subject": subject,
                "Progress": avg_progress * 100
            })
        
        df = pd.DataFrame(subject_progress)
        
        # Create bar plot
        sns.barplot(data=df, x="Subject", y="Progress")
        plt.title("Progress by Subject")
        plt.xticks(rotation=45)
        plt.ylabel("Progress (%)")
        
        # Save plot
        report_file = os.path.join(self.data_dir, f"{student_id}_report.png")
        plt.savefig(report_file, bbox_inches='tight')
        plt.close()

        # Generate summary
        total_topics = sum(len(topics) for topics in progress_data.values())
        completed_topics = sum(
            sum(1 for score in topics.values() if score >= 0.8)
            for topics in progress_data.values()
        )
        
        summary = f"""
        ### 📊 Performance Summary
        
        - **Overall Progress**: {student_data.get('weekly_progress', 0)}%
        - **Topics Covered**: {completed_topics} out of {total_topics}
        - **Study Streak**: {student_data.get('study_streak', 0)} days
        - **Active Since**: {student_data.get('joined_date', 'N/A')}
        
        #### 🎯 Subject Progress
        """
        
        for subject in progress_data:
            topic_count = len(progress_data[subject])
            avg_progress = sum(progress_data[subject].values()) / topic_count if topic_count > 0 else 0
            summary += f"\n- **{subject}**: {avg_progress:.1%} complete"

        return {
            "summary": summary,
            "report_file": report_file
        }

    def _get_student_file_path(self, student_id: str) -> str:
        """Get the file path for student data"""
        return os.path.join(self.data_dir, f"{student_id}.json")

    def _save_student_data(self, student_id: str, data: Dict) -> None:
        """Save student data to file"""
        with open(self._get_student_file_path(student_id), 'w') as f:
            json.dump(data, f, indent=4) 