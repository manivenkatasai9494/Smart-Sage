import streamlit as st
from datetime import datetime

class OnboardingManager:
    def __init__(self, student_manager):
        self.student_manager = student_manager

    def collect_preferences(self, student_id):
        """Collect student preferences during onboarding"""
        st.markdown("## Let's Personalize Your Learning Experience! 📚")
        
        student_data = self.student_manager.get_student_data(student_id)
        if not student_data:
            return False

        # Check if preferences already exist
        if "detailed_preferences" in student_data:
            choice = st.radio(
                "Would you like to:",
                ["Continue with existing preferences", "Update preferences", "Take new assessment"]
            )
            if choice == "Continue with existing preferences":
                return True
            elif choice == "Take new assessment":
                return self.conduct_vark_assessment(student_id)

        with st.form("preferences_form"):
            # Learning Style (VARK)
            st.subheader("Learning Style Preferences")
            vark_preferences = {
                "visual": st.slider(
                    "Visual Learning (diagrams, charts, videos)",
                    0, 100,
                    value=student_data.get("detailed_preferences", {}).get("vark", {}).get("visual", 50)
                ),
                "auditory": st.slider(
                    "Auditory Learning (lectures, discussions)",
                    0, 100,
                    value=student_data.get("detailed_preferences", {}).get("vark", {}).get("auditory", 50)
                ),
                "reading_writing": st.slider(
                    "Reading/Writing Learning",
                    0, 100,
                    value=student_data.get("detailed_preferences", {}).get("vark", {}).get("reading_writing", 50)
                ),
                "kinesthetic": st.slider(
                    "Kinesthetic Learning (hands-on practice)",
                    0, 100,
                    value=student_data.get("detailed_preferences", {}).get("vark", {}).get("kinesthetic", 50)
                )
            }

            # Study Schedule Preferences
            st.subheader("Study Schedule Preferences")
            
            # Preferred study times
            preferred_times = st.multiselect(
                "When do you prefer to study?",
                ["Early Morning (5-8 AM)", "Morning (8-11 AM)", 
                 "Afternoon (11 AM-3 PM)", "Evening (3-7 PM)", 
                 "Night (7-10 PM)", "Late Night (10 PM-2 AM)"],
                default=student_data.get("detailed_preferences", {}).get("preferred_times", [])
            )

            # Study block preferences
            study_block_preference = st.select_slider(
                "Preferred Study Block Length",
                options=["Short Sprints (25-30 min)", 
                        "Medium Sessions (45-60 min)", 
                        "Long Sessions (90+ min)"],
                value=student_data.get("detailed_preferences", {}).get("study_block_preference", "Medium Sessions (45-60 min)")
            )

            # Break preferences
            break_preference = st.multiselect(
                "Break Schedule Preference",
                ["Pomodoro (25 min work, 5 min break)",
                 "Long Focus (50 min work, 10 min break)",
                 "Custom Schedule",
                 "AI-recommended breaks based on performance"],
                default=student_data.get("detailed_preferences", {}).get("break_preference", [])
            )

            # Adaptive preferences
            st.subheader("Adaptive Learning Preferences")
            
            adaptive_options = st.multiselect(
                "Choose your adaptive learning preferences",
                ["Adjust difficulty based on performance",
                 "Dynamic topic ordering",
                 "Personalized review scheduling",
                 "Real-time focus tracking",
                 "Performance-based break suggestions"],
                default=student_data.get("detailed_preferences", {}).get("adaptive_options", [])
            )

            # Study material preferences
            st.subheader("Study Material Preferences")
            
            material_preferences = st.multiselect(
                "What types of study materials do you prefer?",
                ["Video Lectures",
                 "Interactive Simulations",
                 "Text Books/Notes",
                 "Practice Problems",
                 "Flashcards",
                 "Mind Maps",
                 "Audio Lectures",
                 "Group Discussions"],
                default=student_data.get("detailed_preferences", {}).get("material_preferences", [])
            )

            # Difficulty preferences
            initial_difficulty = st.select_slider(
                "Preferred Starting Difficulty",
                options=["Beginner", "Intermediate", "Advanced"],
                value=student_data.get("detailed_preferences", {}).get("initial_difficulty", "Intermediate")
            )

            # Goals and Targets
            st.subheader("Goals and Targets")
            
            target_scores = {
                subject: st.number_input(
                    f"Target score for {subject.capitalize()} (%)",
                    min_value=0,
                    max_value=100,
                    value=student_data.get("detailed_preferences", {}).get("target_scores", {}).get(subject, 80)
                ) for subject in ["math", "physics", "chemistry"]
            }

            exam_dates = st.text_area(
                "Upcoming Exam Dates (Format: Subject - YYYY-MM-DD)",
                value=student_data.get("detailed_preferences", {}).get("exam_dates", "")
            )

            if st.form_submit_button("Save Preferences"):
                # Update student data with detailed preferences
                student_data["detailed_preferences"] = {
                    "last_updated": datetime.now().isoformat(),
                    "vark": vark_preferences,
                    "preferred_times": preferred_times,
                    "study_block_preference": study_block_preference,
                    "break_preference": break_preference,
                    "adaptive_options": adaptive_options,
                    "material_preferences": material_preferences,
                    "initial_difficulty": initial_difficulty,
                    "target_scores": target_scores,
                    "exam_dates": exam_dates
                }
                self.student_manager.update_student_data(student_id, student_data)
                return True

        return False

    def conduct_vark_assessment(self, student_id):
        """Conduct VARK learning style assessment"""
        st.markdown("## VARK Learning Style Assessment")
        st.info("Answer these questions to determine your preferred learning style.")

        vark_questions = [
            {
                "question": "When learning a new skill, you prefer to:",
                "options": {
                    "visual": "Watch a video demonstration",
                    "auditory": "Listen to someone explain it",
                    "reading_writing": "Read written instructions",
                    "kinesthetic": "Try it hands-on"
                }
            },
            {
                "question": "When studying for an exam, you find it most effective to:",
                "options": {
                    "visual": "Use diagrams and charts",
                    "auditory": "Discuss topics with others",
                    "reading_writing": "Make written notes",
                    "kinesthetic": "Create practice problems"
                }
            },
            # Add more VARK assessment questions here
        ]

        with st.form("vark_assessment"):
            responses = {}
            for i, q in enumerate(vark_questions):
                st.write(f"\n{i+1}. {q['question']}")
                response = st.radio(
                    "Choose your preferred method:",
                    list(q["options"].values()),
                    key=f"vark_q{i}"
                )
                # Map response back to VARK category
                for style, text in q["options"].items():
                    if text == response:
                        responses[style] = responses.get(style, 0) + 1

            if st.form_submit_button("Complete Assessment"):
                # Calculate VARK scores
                total = sum(responses.values())
                vark_scores = {
                    style: (count / total) * 100
                    for style, count in responses.items()
                }

                # Update student data
                student_data = self.student_manager.get_student_data(student_id)
                if "detailed_preferences" not in student_data:
                    student_data["detailed_preferences"] = {}
                student_data["detailed_preferences"]["vark"] = vark_scores
                self.student_manager.update_student_data(student_id, student_data)
                return True

        return False

    def display_learning_options(self, student_id):
        """Display different learning options for the student"""
        st.markdown("## Choose Your Learning Path 🎯")
        
        options = {
            "study_plan": "Generate Daily Study Plan",
            "courses": "Browse Relevant Courses",
            "course_info": "Get Detailed Course Information",
            "roadmap": "View Learning Roadmap",
            "videos": "Access Related Videos"
        }
        
        selected_option = st.selectbox("What would you like to do?", list(options.values()))
        
        if selected_option == options["study_plan"]:
            self.show_study_plan_options(student_id)
        elif selected_option == options["courses"]:
            self.show_course_options(student_id)
        elif selected_option == options["course_info"]:
            self.show_course_details(student_id)
        elif selected_option == options["roadmap"]:
            self.show_learning_roadmap(student_id)
        elif selected_option == options["videos"]:
            self.show_related_videos(student_id)

    def show_study_plan_options(self, student_id):
        """Show options for generating a study plan"""
        st.subheader("Generate Your Study Plan 📚")
        
        student_data = self.student_manager.get_student_data(student_id)
        preferences = student_data.get("detailed_preferences", {})
        
        with st.form("study_plan_options"):
            st.write("Customize your study plan:")
            
            # Get subject priorities
            subjects = ["math", "physics", "chemistry"]
            subject_priorities = {}
            for subject in subjects:
                priority = st.slider(
                    f"Priority for {subject.capitalize()}",
                    0, 10,
                    value=5
                )
                subject_priorities[subject] = priority
            
            # Get difficulty preference
            difficulty = st.select_slider(
                "Select difficulty level",
                options=["Beginner", "Intermediate", "Advanced"],
                value="Intermediate"
            )
            
            # Get plan duration
            duration = st.number_input(
                "Number of days for the plan",
                min_value=1,
                max_value=30,
                value=7
            )
            
            if st.form_submit_button("Generate Plan"):
                # Store preferences in session state
                st.session_state.plan_preferences = {
                    "subject_priorities": subject_priorities,
                    "difficulty": difficulty,
                    "duration": duration
                }
                st.session_state.show_study_planner = True
                st.rerun()

    def show_course_options(self, student_id):
        """Show available courses based on student preferences"""
        st.subheader("Available Courses 📖")
        student_data = self.student_manager.get_student_data(student_id)
        preferences = student_data.get("detailed_preferences", {})
        
        subject = st.selectbox("Select Subject", ["math", "physics", "chemistry"])
        
        # Example course structure (in real app, this would come from a database)
        courses = {
            "math": [
                {"title": "Basic Algebra", "level": "Beginner", "duration": "4 weeks"},
                {"title": "Advanced Calculus", "level": "Advanced", "duration": "6 weeks"},
            ],
            "physics": [
                {"title": "Mechanics Fundamentals", "level": "Beginner", "duration": "5 weeks"},
                {"title": "Quantum Physics", "level": "Advanced", "duration": "8 weeks"},
            ],
            "chemistry": [
                {"title": "Basic Chemistry", "level": "Beginner", "duration": "4 weeks"},
                {"title": "Organic Chemistry", "level": "Advanced", "duration": "6 weeks"},
            ]
        }
        
        for course in courses.get(subject, []):
            with st.expander(f"📘 {course['title']}"):
                st.write(f"Level: {course['level']}")
                st.write(f"Duration: {course['duration']}")
                if st.button("View Details", key=f"view_{course['title']}"):
                    st.session_state.selected_course = course
                    st.session_state.show_course_details = True
                    st.rerun()

    def show_course_details(self, student_id):
        """Show detailed information about a selected course"""
        if hasattr(st.session_state, 'selected_course'):
            course = st.session_state.selected_course
            st.subheader(f"Course Details: {course['title']}")
            
            tabs = st.tabs(["Overview", "Syllabus", "Resources", "Schedule"])
            
            with tabs[0]:
                st.write("Course Overview...")
                
            with tabs[1]:
                st.write("Detailed Syllabus...")
                
            with tabs[2]:
                st.write("Learning Resources...")
                
            with tabs[3]:
                st.write("Course Schedule...")
        else:
            st.info("Please select a course first from the course list.")

    def show_learning_roadmap(self, student_id):
        """Display a learning roadmap based on student goals"""
        st.subheader("Your Learning Roadmap 🗺️")
        student_data = self.student_manager.get_student_data(student_id)
        preferences = student_data.get("detailed_preferences", {})
        
        subject = st.selectbox("Select Subject for Roadmap", ["math", "physics", "chemistry"])
        
        # Example roadmap visualization
        st.write("Learning Path:")
        for i, milestone in enumerate([
            "Fundamentals",
            "Basic Concepts",
            "Intermediate Topics",
            "Advanced Applications",
            "Expert Level"
        ], 1):
            st.markdown(f"{i}. **{milestone}** ➡️")

    def show_related_videos(self, student_id):
        """Show related educational videos"""
        st.subheader("Educational Videos 🎥")
        
        subject = st.selectbox("Select Subject", ["math", "physics", "chemistry"])
        topic = st.text_input("Search for specific topic (optional)")
        
        # Example video listings (in real app, these would come from YouTube API or similar)
        st.write("Available Videos:")
        for i in range(3):
            with st.expander(f"Video {i+1}"):
                st.write(f"Sample video title for {subject}")
                st.write("Video description...")
                st.button("Watch Video", key=f"video_{i}")

    def show_back_button(self):
        """Display a back button"""
        if st.button("⬅️ Back"):
            # Clear any specific view states
            for key in ['show_study_planner', 'show_course_details', 'selected_course']:
                if key in st.session_state:
                    del st.session_state[key]
            return True
        return False 