import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


class StudyPlanner:
    def __init__(self):
        # Study session templates
        self.session_templates = {
            "visual": [
                "Create mind maps for {topic}",
                "Watch video tutorials on {topic}",
                "Draw diagrams to understand {topic}",
                "Study infographics about {topic}"
            ],
            "auditory": [
                "Listen to lectures on {topic}",
                "Participate in discussion groups about {topic}",
                "Record and review explanations of {topic}",
                "Use audio resources for {topic}"
            ],
            "practical": [
                "Complete hands-on exercises in {topic}",
                "Build projects related to {topic}",
                "Solve practice problems about {topic}",
                "Implement concepts from {topic}"
            ]
        }
        
        # Days of the week
        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        # Topic difficulty mapping
        self.topic_difficulty = {
            "Variables & Data Types": 0.3,
            "Control Flow": 0.4,
            "Functions": 0.5,
            "Classes & Objects": 0.7,
            "HTML Basics": 0.2,
            "CSS Styling": 0.3,
            "JavaScript Fundamentals": 0.5,
            "React Components": 0.7,
            "UI Design": 0.4,
            "State Management": 0.7,
            "API Integration": 0.6,
            "App Deployment": 0.5,
            "Neural Networks": 0.8,
            "Deep Learning": 0.9,
            "Computer Vision": 0.8,
            "NLP": 0.8,
            "Design Patterns": 0.7,
            "Testing": 0.5,
            "Version Control": 0.4,
            "CI/CD": 0.6,
            "TCP/IP": 0.6,
            "Network Security": 0.7,
            "Cloud Computing": 0.6,
            "APIs": 0.5,
            "SQL Queries": 0.5,
            "Database Design": 0.6,
            "NoSQL": 0.6,
            "Data Modeling": 0.7,
            "Process Management": 0.6,
            "Memory Management": 0.7,
            "File Systems": 0.5,
            "Security": 0.7,
            "CPU Architecture": 0.7,
            "Memory Hierarchy": 0.6,
            "I/O Systems": 0.5,
            "Pipelining": 0.8
        }

        # Progress tracking
        self.progress_metrics = {
            "completion_rate": 0.0,  # Overall completion rate
            "study_streak": 0,       # Consecutive days of study
            "total_hours": 0,        # Total hours studied
            "topic_mastery": {},     # Mastery level per topic
            "weekly_goals": {},      # Weekly goals and achievements
            "learning_pace": {}      # Learning pace per subject
        }

    def analyze_content_difficulty(self, topic: str) -> float:
        """Analyze topic difficulty using predefined mapping"""
        return self.topic_difficulty.get(topic, 0.5)  # Default to medium difficulty if topic not found

    def generate_schedule(self, student_data: Dict) -> Dict[str, List[Dict]]:
        """Generate personalized study schedule based on student preferences"""
        schedule = {day: [] for day in self.days}
        
        # Extract preferences
        weekly_hours = student_data["study_preferences"]["weekly_hours"]
        preferred_times = student_data["study_preferences"]["preferred_times"]
        learning_styles = student_data["study_preferences"]["learning_styles"]
        priorities = student_data["subject_priorities"]
        
        # Calculate sessions per day
        sessions_per_day = max(1, round(weekly_hours / 7))
        
        # Generate sessions for each day
        for day in self.days:
            for _ in range(sessions_per_day):
                # Select subject based on priorities
                subject = self._select_subject(priorities)
                topic = self._get_topic_for_subject(subject)
                
                # Determine learning style
                style = self._select_learning_style(learning_styles)
                
                # Generate focus based on topic analysis
                difficulty = self.analyze_content_difficulty(topic)
                focus = self._generate_focus(style, topic)
                
                # Select time slot
                time = random.choice(preferred_times) if preferred_times else "Morning (9-12 PM)"
                
                # Create session
                session = {
                    "time": time,
                    "subject": subject,
                    "topic": topic,
                    "style": style,
                    "focus": focus,
                    "difficulty": difficulty
                }
                
                schedule[day].append(session)
        
        return schedule

    def _select_subject(self, priorities: Dict[str, str]) -> str:
        """Select subject based on priorities"""
        weights = {"High": 0.6, "Medium": 0.3, "Low": 0.1}
        subjects = list(priorities.keys())
        probabilities = [weights[priorities[s]] for s in subjects]
        probabilities = np.array(probabilities) / sum(probabilities)
        return np.random.choice(subjects, p=probabilities)

    def _get_topic_for_subject(self, subject: str) -> str:
        """Get appropriate topic for the subject"""
        topics = {
            "programming": ["Variables & Data Types", "Control Flow", "Functions", "Classes & Objects"],
            "web_dev": ["HTML Basics", "CSS Styling", "JavaScript Fundamentals", "React Components"],
            "mobile_dev": ["UI Design", "State Management", "API Integration", "App Deployment"],
            "ai": ["Neural Networks", "Deep Learning", "Computer Vision", "NLP"],
            "software_eng": ["Design Patterns", "Testing", "Version Control", "CI/CD"],
            "networks": ["TCP/IP", "Network Security", "Cloud Computing", "APIs"],
            "databases": ["SQL Queries", "Database Design", "NoSQL", "Data Modeling"],
            "os": ["Process Management", "Memory Management", "File Systems", "Security"],
            "architecture": ["CPU Architecture", "Memory Hierarchy", "I/O Systems", "Pipelining"]
        }
        return random.choice(topics.get(subject, ["General Concepts"]))

    def _select_learning_style(self, styles: Dict[str, bool]) -> str:
        """Select learning style based on preferences"""
        available_styles = [style for style, enabled in styles.items() if enabled]
        return random.choice(available_styles) if available_styles else "visual"

    def _generate_focus(self, style: str, topic: str) -> str:
        """Generate focus activity based on learning style"""
        templates = self.session_templates.get(style, self.session_templates["visual"])
        return random.choice(templates).format(topic=topic)

    def track_session_completion(self, student_id: str, session: Dict, completion_data: Dict) -> Dict:
        """Track completion of a study session"""
        # Update completion metrics
        completion_rate = completion_data.get("completion_rate", 0)
        understanding = completion_data.get("understanding_level", 0)
        time_spent = completion_data.get("time_spent", 0)
        
        # Calculate session score (0-100)
        session_score = (completion_rate * 0.4 + understanding * 0.4 + min(time_spent/60, 1) * 0.2) * 100
        
        # Update topic mastery
        topic = session["topic"]
        subject = session["subject"]
        current_mastery = self.progress_metrics["topic_mastery"].get(topic, 0)
        new_mastery = current_mastery * 0.7 + (session_score/100) * 0.3  # Weighted update
        self.progress_metrics["topic_mastery"][topic] = new_mastery
        
        # Update learning pace
        if subject not in self.progress_metrics["learning_pace"]:
            self.progress_metrics["learning_pace"][subject] = []
        self.progress_metrics["learning_pace"][subject].append({
            "date": datetime.now().isoformat(),
            "score": session_score,
            "time_spent": time_spent
        })
        
        # Update total hours
        self.progress_metrics["total_hours"] += time_spent / 60
        
        return {
            "session_score": session_score,
            "mastery_level": new_mastery,
            "total_hours": self.progress_metrics["total_hours"]
        }

    def generate_progress_report(self, student_id: str) -> Tuple[Dict, str]:
        """Generate a comprehensive progress report"""
        # Calculate overall progress
        overall_progress = sum(self.progress_metrics["topic_mastery"].values()) / len(self.progress_metrics["topic_mastery"]) if self.progress_metrics["topic_mastery"] else 0
        
        # Generate visualizations
        plt.figure(figsize=(15, 10))
        
        # 1. Topic Mastery Heatmap
        plt.subplot(2, 2, 1)
        mastery_data = [[v] for v in self.progress_metrics["topic_mastery"].values()]
        sns.heatmap(mastery_data, 
                   yticklabels=list(self.progress_metrics["topic_mastery"].keys()),
                   xticklabels=["Mastery"],
                   cmap="YlOrRd",
                   cbar_kws={'label': 'Mastery Level'})
        plt.title("Topic Mastery Levels")
        
        # 2. Learning Pace Over Time
        plt.subplot(2, 2, 2)
        for subject, pace_data in self.progress_metrics["learning_pace"].items():
            dates = [datetime.fromisoformat(d["date"]) for d in pace_data]
            scores = [d["score"] for d in pace_data]
            plt.plot(dates, scores, label=subject, marker='o')
        plt.title("Learning Progress Over Time")
        plt.xlabel("Date")
        plt.ylabel("Session Score")
        plt.legend()
        plt.xticks(rotation=45)
        
        # 3. Time Distribution
        plt.subplot(2, 2, 3)
        subject_times = {}
        for subject, pace_data in self.progress_metrics["learning_pace"].items():
            subject_times[subject] = sum(d["time_spent"] for d in pace_data) / 60
        plt.pie(subject_times.values(), labels=subject_times.keys(), autopct='%1.1f%%')
        plt.title("Study Time Distribution")
        
        # Save plot
        plot_path = f"progress_report_{student_id}.png"
        plt.tight_layout()
        plt.savefig(plot_path)
        plt.close()
        
        # Generate summary statistics
        summary = {
            "overall_progress": overall_progress * 100,
            "total_study_hours": self.progress_metrics["total_hours"],
            "topics_mastered": sum(1 for v in self.progress_metrics["topic_mastery"].values() if v >= 0.8),
            "total_topics": len(self.progress_metrics["topic_mastery"]),
            "study_streak": self.progress_metrics["study_streak"],
            "plot_path": plot_path
        }
        
        # Generate recommendations
        weak_topics = [
            topic for topic, mastery in self.progress_metrics["topic_mastery"].items()
            if mastery < 0.6
        ]
        
        recommendations = {
            "focus_areas": weak_topics[:3],
            "suggested_hours": max(10, self.progress_metrics["total_hours"] * 0.1),
            "pace_adjustment": "increase" if overall_progress < 0.6 else "maintain"
        }
        
        return summary, recommendations

    def update_study_streak(self, last_study_date: datetime) -> None:
        """Update the study streak based on last study date"""
        days_diff = (datetime.now() - last_study_date).days
        if days_diff <= 1:
            self.progress_metrics["study_streak"] += 1
        else:
            self.progress_metrics["study_streak"] = 0


def generate_study_schedule(student_data: Dict) -> Dict[str, List[Dict]]:
    """Generate a study schedule for the student"""
    planner = StudyPlanner()
    return planner.generate_schedule(student_data) 