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

    def get_student_file(self, student_id):
        """Get the path to a student's data file"""
        return os.path.join(self.data_dir, f"{student_id}.json")

    def student_exists(self, student_id):
        """Check if a student exists"""
        return os.path.exists(self.get_student_file(student_id))

    def create_student(self, student_id, name, grade):
        """Create a new student profile"""
        if self.student_exists(student_id):
            return False

        student_data = {
            "student_id": student_id,
            "name": name,
            "grade": grade,
            "created_at": datetime.now().isoformat(),
            "subjects": {
                "math": {"topics": {}, "overall_score": 0, "questions_answered": 0},
                "physics": {"topics": {}, "overall_score": 0, "questions_answered": 0},
                "chemistry": {"topics": {}, "overall_score": 0, "questions_answered": 0}
            },
            "session_history": [],
            "badges": [],
            "preferences": {
                "language": "en",
                "difficulty_level": "medium"
            }
        }

        with open(self.get_student_file(student_id), 'w') as f:
            json.dump(student_data, f, indent=4)

        return True

    def get_student_data(self, student_id):
        """Get a student's data"""
        if not self.student_exists(student_id):
            return None

        with open(self.get_student_file(student_id), 'r') as f:
            return json.load(f)

    def update_student_data(self, student_id, student_data):
        """Update a student's data"""
        if not self.student_exists(student_id):
            return False

        with open(self.get_student_file(student_id), 'w') as f:
            json.dump(student_data, f, indent=4)

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
        subject_data = student_data["subjects"][subject]
        subject_data["questions_answered"] += questions_asked

        # Update or create topic
        if topic not in subject_data["topics"]:
            subject_data["topics"][topic] = {
                "questions_answered": 0,
                "correct_answers": 0,
                "sessions": 0,
                "average_score": 0
            }

        topic_data = subject_data["topics"][topic]
        topic_data["questions_answered"] += questions_asked
        topic_data["correct_answers"] += correct_answers
        topic_data["sessions"] += 1

        if topic_data["questions_answered"] > 0:
            topic_data["average_score"] = (topic_data["correct_answers"] / topic_data["questions_answered"]) * 100

        # Calculate overall subject score (average of all topics)
        total_score = 0
        total_topics = 0
        for t, t_data in subject_data["topics"].items():
            if t_data["questions_answered"] > 0:
                total_score += t_data["average_score"]
                total_topics += 1

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

        student_data["session_history"].append(session)

        # Check and award badges
        self._check_and_award_badges(student_data)

        # Save updated data
        return self.update_student_data(student_id, student_data)

    def _check_and_award_badges(self, student_data):
        """Check and award badges based on student performance"""
        badges = student_data["badges"]

        # Check for subject mastery badges (>90% in 3+ topics)
        for subject, data in student_data["subjects"].items():
            badge_name = f"{subject.capitalize()} Explorer"
            if badge_name not in badges:
                mastered_topics = 0
                for topic, topic_data in data["topics"].items():
                    if topic_data["questions_answered"] >= 10 and topic_data["average_score"] >= 90:
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
            for subject, data in student_data["subjects"].items():
                if data["questions_answered"] < 20:
                    all_subjects_active = False
                    break

            if all_subjects_active:
                badges.append(badge_name)

        student_data["badges"] = badges

    def get_recommended_topics(self, student_id, subject):
        """Get recommended topics based on student performance"""
        student_data = self.get_student_data(student_id)
        if not student_data:
            return []

        subject_data = student_data["subjects"][subject]

        # If no topics studied yet, return some starter topics
        if not subject_data["topics"]:
            if subject == "math":
                return ["Basic Algebra", "Fractions", "Decimals", "Geometry Basics"]
            elif subject == "physics":
                return ["Newton's Laws", "Motion", "Forces", "Energy"]
            else:  # chemistry
                return ["Periodic Table", "Chemical Bonds", "Elements", "Compounds"]

        # Find topics with low scores (<70%)
        weak_topics = []
        for topic, data in subject_data["topics"].items():
            if data["questions_answered"] > 0 and data["average_score"] < 70:
                weak_topics.append((topic, data["average_score"]))

        # Sort by score (lowest first)
        weak_topics.sort(key=lambda x: x[1])

        # Return topics to focus on
        return [topic for topic, score in weak_topics[:3]]

    def generate_performance_report(self, student_id):
        """Generate a performance report for a student"""
        student_data = self.get_student_data(student_id)
        if not student_data:
            return None

        # Create DataFrame for visualization
        data = []
        for subject, subject_data in student_data["subjects"].items():
            for topic, topic_data in subject_data["topics"].items():
                if topic_data["questions_answered"] > 0:
                    data.append({
                        "Subject": subject.capitalize(),
                        "Topic": topic,
                        "Score": topic_data["average_score"],
                        "Questions": topic_data["questions_answered"]
                    })

        if not data:
            return "Not enough data to generate a report."

        df = pd.DataFrame(data)

        # Create visualizations
        plt.figure(figsize=(12, 8))

        # Plot 1: Subject Performance
        plt.subplot(2, 1, 1)
        sns.barplot(x="Subject", y="Score", data=df, estimator=lambda x: sum(x) / len(x) if len(x) > 0 else 0)
        plt.title(f"Average Performance by Subject for {student_data['name']}")
        plt.ylim(0, 100)
        plt.ylabel("Average Score (%)")

        # Plot 2: Topic Performance
        plt.subplot(2, 1, 2)
        topic_scores = df.groupby(["Subject", "Topic"])["Score"].mean().reset_index()
        topic_scores = topic_scores.sort_values("Score")

        # Get the top 10 topics by performance
        if len(topic_scores) > 10:
            topic_scores = pd.concat([topic_scores.head(5), topic_scores.tail(5)])

        sns.barplot(x="Topic", y="Score", hue="Subject", data=topic_scores)
        plt.title("Performance by Topic")
        plt.ylim(0, 100)
        plt.ylabel("Average Score (%)")
        plt.xticks(rotation=45, ha="right")

        plt.tight_layout()

        # Save figure
        report_file = os.path.join(self.data_dir, f"{student_id}_report.png")
        plt.savefig(report_file)
        plt.close()

        # Text summary
        summary = f"Performance Report for {student_data['name']} (Grade {student_data['grade']})\n\n"

        # Overall stats
        for subject, data in student_data["subjects"].items():
            if data["questions_answered"] > 0:
                summary += f"{subject.capitalize()}: Overall Score {data['overall_score']:.1f}% ({data['questions_answered']} questions answered)\n"

        # Strengths and weaknesses
        if len(df) > 0:
            top_topics = df.nlargest(3, "Score")
            bottom_topics = df.nsmallest(3, "Score")

            summary += "\nStrengths:\n"
            for _, row in top_topics.iterrows():
                summary += f"- {row['Topic']} ({row['Subject']}): {row['Score']:.1f}%\n"

            summary += "\nAreas for Improvement:\n"
            for _, row in bottom_topics.iterrows():
                summary += f"- {row['Topic']} ({row['Subject']}): {row['Score']:.1f}%\n"

        # Recent progress
        if len(student_data["session_history"]) > 0:
            recent_sessions = sorted(student_data["session_history"], key=lambda x: x["date"], reverse=True)[:5]

            summary += "\nRecent Progress:\n"
            for session in recent_sessions:
                date = datetime.fromisoformat(session["date"]).strftime("%Y-%m-%d")
                summary += f"- {date}: {session['subject'].capitalize()} - {session['topic']} ({session['score']:.1f}%)\n"

        # Badges
        if student_data["badges"]:
            summary += "\nBadges Earned:\n"
            for badge in student_data["badges"]:
                summary += f"- {badge}\n"

        return {
            "summary": summary,
            "report_file": report_file
        }

    def save_study_plan(self, student_id, plan, goals):
        """Save a new study plan for the student"""
        student_data = self.get_student_data(student_id)
        if not student_data:
            return False

        # Ensure the plan has the correct structure
        if not isinstance(plan, dict) or "daily_schedules" not in plan:
            return False

        plan_data = {
            "id": len(student_data["study_plans"]) + 1,
            "created_at": datetime.now().isoformat(),
            "goals": goals,
            "daily_schedules": plan["daily_schedules"],  # Store the daily_schedules directly
            "status": "active"
        }

        # Set all other plans to inactive
        for existing_plan in student_data["study_plans"]:
            existing_plan["status"] = "inactive"

        student_data["study_plans"].append(plan_data)
        student_data["study_goals"].append({
            "id": len(student_data["study_goals"]) + 1,
            "created_at": datetime.now().isoformat(),
            "goals": goals,
            "status": "in_progress"
        })

        return self.update_student_data(student_id, student_data)

    def get_study_progress(self, student_id):
        """Get the student's study progress"""
        student_data = self.get_student_data(student_id)
        if not student_data or not student_data["study_plans"]:
            return None

        active_plan = self.get_active_study_plan(student_id)
        if not active_plan:
            return None

        completed_tasks = student_data["completed_tasks"]
        
        # Access daily_schedules directly from active_plan
        total_tasks = sum(len(day["sessions"]) for day in active_plan["daily_schedules"].values())
        completed_count = len([t for t in completed_tasks if any(
            t == session["id"]
            for day in active_plan["daily_schedules"].values()
            for session in day["sessions"]
        )])

        return {
            "plan_id": active_plan["id"],
            "total_tasks": total_tasks,
            "completed_tasks": completed_count,
            "completion_rate": (completed_count / total_tasks * 100) if total_tasks > 0 else 0
        }

    def get_active_study_plan(self, student_id):
        """Get the student's active study plan"""
        student_data = self.get_student_data(student_id)
        if not student_data or not student_data["study_plans"]:
            return None

        active_plans = [p for p in student_data["study_plans"] if p["status"] == "active"]
        return active_plans[-1] if active_plans else None

    def mark_task_completed(self, student_id, task_id):
        """Mark a study task as completed"""
        student_data = self.get_student_data(student_id)
        if not student_data:
            return False

        if task_id not in student_data["completed_tasks"]:
            student_data["completed_tasks"].append(task_id)
            return self.update_student_data(student_id, student_data)
        return True