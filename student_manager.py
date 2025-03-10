import json
import os
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from config import DATA_DIR


class StudentManager:
    def __init__(self):
        self.data_dir = DATA_DIR
        os.makedirs(self.data_dir, exist_ok=True)
        self.students_file = "students.json"
        self.load_students()

    def load_students(self):
        if os.path.exists(self.students_file):
            with open(self.students_file, "r") as f:
                self.students = json.load(f)
        else:
            self.students = {}
            self.save_students()

    def save_students(self):
        with open(self.students_file, "w") as f:
            json.dump(self.students, f, indent=4)

    def get_student_file(self, student_id):
        """Get the path to a student's data file"""
        return os.path.join(self.data_dir, f"{student_id}.json")

    def student_exists(self, student_id):
        """Check if a student exists"""
        return student_id in self.students

    def create_student(self, student_id, name, grade, selected_courses):
        """Create a new student profile"""
        if self.student_exists(student_id):
            return False

        self.students[student_id] = {
            "name": name,
            "grade": grade,
            "created_at": str(datetime.now()),
            "courses": selected_courses,
            "progress": {},
            "badges": [],
            "preferences": {
                "language": "en",
                "difficulty_level": "medium"
            }
        }
        self.save_students()
        return True

    def get_student_data(self, student_id):
        """Get a student's data"""
        if not self.student_exists(student_id):
            return None

        return self.students[student_id]

    def update_student_data(self, student_id, data):
        """Update a student's data"""
        if not self.student_exists(student_id):
            return False

        self.students[student_id].update(data)
        self.save_students()
        return True

    def record_session(self, student_id, subject, topic, questions_asked, correct_answers):
        """Record a learning session"""
        student_data = self.get_student_data(student_id)
        if not student_data:
            return False

        # Calculate score
        score = 0
        if questions_asked > 0:
            score = (correct_answers / questions_asked) * 100

        # Update subject stats
        subject_data = student_data["progress"][subject]
        subject_data[topic] = subject_data.get(topic, []) + [score]

        # Calculate overall subject score (average of all topics)
        total_score = 0
        total_topics = 0
        for t, t_data in subject_data.items():
            if isinstance(t_data, list):
                total_score += sum(t_data) / len(t_data) if t_data else 0
                total_topics += len(t_data)

        if total_topics > 0:
            subject_data["overall_score"] = total_score / total_topics

        # Record session in history
        session = {
            "date": datetime.now().isoformat(),
            "subject": subject,
            "topic": topic,
            "questions_asked": questions_asked,
            "correct_answers": correct_answers,
            "score": score
        }

        student_data["session_history"] = student_data.get("session_history", []) + [session]

        # Check and award badges
        self._check_and_award_badges(student_data)

        # Save updated data
        return self.update_student_data(student_id, student_data)

    def _check_and_award_badges(self, student_data):
        """Check and award badges based on student performance"""
        badges = student_data["badges"]

        # Check for subject mastery badges (>90% in 3+ topics)
        for subject, data in student_data["progress"].items():
            badge_name = f"{subject.capitalize()} Explorer"
            if badge_name not in badges:
                mastered_topics = 0
                for topic, topic_data in data.items():
                    if isinstance(topic_data, list) and len(topic_data) > 0 and sum(topic_data) / len(topic_data) >= 90:
                        mastered_topics += 1

                if mastered_topics >= 3:
                    badges.append(badge_name)

        # Check for consistency badge
        badge_name = "Consistent Learner"
        if badge_name not in badges:
            if len(student_data["session_history"]) >= 10:
                badges.append(badge_name)

        # Check for all-rounder badge
        badge_name = "All-Rounder"
        if badge_name not in badges:
            all_subjects_active = True
            for subject, data in student_data["progress"].items():
                if isinstance(data, dict) and len(data) < 20:
                    all_subjects_active = False
                    break

            if all_subjects_active:
                badges.append(badge_name)

        student_data["badges"] = badges

    def get_recommended_topics(self, student_id, subject):
        """Get recommended topics based on student performance"""
        student_data = self.get_student_data(student_id)
        if not student_data or "progress" not in student_data:
            return None

        # Get completed topics
        completed_topics = []
        for topic, subtopics in student_data["progress"].get(subject, {}).items():
            if isinstance(subtopics, list) and len(subtopics) > 0:
                completed_topics.append(topic)

        # Return recommendations based on completed topics
        if completed_topics:
            return [f"Next topic after {topic}" for topic in completed_topics]
        return None

    def generate_performance_report(self, student_id):
        """Generate a performance report for a student"""
        student_data = self.get_student_data(student_id)
        if not student_data or "progress" not in student_data:
            return "No progress data available yet."

        # Calculate overall progress
        total_topics = 0
        completed_topics = 0

        for subject, topics in student_data["progress"].items():
            for topic, subtopics in topics.items():
                total_topics += 1
                if isinstance(subtopics, list) and len(subtopics) > 0:
                    completed_topics += 1

        progress_percentage = (completed_topics / total_topics * 100) if total_topics > 0 else 0

        # Create DataFrame for visualization
        data = []
        for subject, topics in student_data["progress"].items():
            for topic, subtopics in topics.items():
                if isinstance(subtopics, list) and len(subtopics) > 0:
                    avg_score = sum(subtopics) / len(subtopics)
                    data.append({
                        "Subject": subject,
                        "Topic": topic,
                        "Score": avg_score
                    })

        if data:
            df = pd.DataFrame(data)
            
            # Create visualizations
            plt.figure(figsize=(12, 6))
            
            # Plot performance by subject
            plt.subplot(1, 2, 1)
            sns.barplot(x="Subject", y="Score", data=df)
            plt.title("Performance by Subject")
            plt.xticks(rotation=45)
            plt.ylim(0, 100)
            
            # Plot performance by topic
            plt.subplot(1, 2, 2)
            topic_scores = df.groupby("Topic")["Score"].mean().sort_values(ascending=True)
            topic_scores.plot(kind="barh")
            plt.title("Performance by Topic")
            plt.xlabel("Score")
            plt.ylim(0, 100)
            
            plt.tight_layout()
            
            # Save the plot
            report_file = os.path.join(self.data_dir, f"{student_id}_report.png")
            plt.savefig(report_file)
            plt.close()
        else:
            report_file = None

        # Generate report
        report = {
            "summary": f"""
                ### Performance Report
                - Overall Progress: {progress_percentage:.1f}%
                - Completed Topics: {completed_topics}/{total_topics}
                - Active Subjects: {len(student_data["progress"])}
                
                ### Course Progress
                {self._generate_course_progress_summary(student_data)}
            """,
            "report_file": report_file
        }

        return report

    def _generate_course_progress_summary(self, student_data):
        """Generate a summary of course progress"""
        if "courses" not in student_data:
            return "No courses enrolled yet."
        
        summary = []
        for course in student_data["courses"]:
            progress = 0
            if course in student_data["progress"]:
                topics = student_data["progress"][course]
                completed = sum(1 for t in topics.values() if isinstance(t, list) and len(t) > 0)
                total = len(topics)
                progress = (completed / total * 100) if total > 0 else 0
            
            summary.append(f"- {course}: {progress:.1f}% complete")
        
        return "\n".join(summary) 