import base64
import os
from datetime import datetime

import streamlit as st
import streamlit.components.v1 as components
from PIL import Image

from ai_service import AITutorService
from config import ALLOWED_SUBJECTS, APP_NAME, SUBJECT_DISPLAY_NAMES
from student_manager import StudentManager
from study_planner import StudyPlanner, generate_study_schedule


# Initialize services
@st.cache_resource
def init_services():
    return AITutorService(), StudentManager()

# Define courses dictionary
courses = {
    "Programming": [
        "Python",
        "Java",
        "JavaScript",
        "C++",
        "SQL"
    ],
    "Web Development": [
        "HTML/CSS",
        "React",
        "Node.js",
        "MongoDB",
        "APIs"
    ],
    "Mobile Development": [
        "Android Development",
        "iOS Development",
        "React Native",
        "Flutter",
        "Mobile UI/UX"
    ],
    "Artificial Intelligence": [
        "Machine Learning",
        "Deep Learning",
        "Neural Networks",
        "Computer Vision",
        "Natural Language Processing"
    ],
    "Software Engineering": [
        "Software Design Patterns",
        "Clean Code",
        "Testing & QA",
        "DevOps & CI/CD",
        "Agile Methodologies"
    ],
    "Computer Networks": [
        "Network Protocols",
        "Network Security",
        "Cloud Computing",
        "Distributed Systems",
        "Cybersecurity"
    ],
    "Database Systems": [
        "SQL Advanced",
        "NoSQL Databases",
        "Database Design",
        "Data Warehousing",
        "Big Data"
    ],
    "Operating Systems": [
        "Process Management",
        "Memory Management",
        "File Systems",
        "System Security",
        "Shell Scripting"
    ],
    "Computer Architecture": [
        "Digital Logic",
        "Computer Organization",
        "Assembly Language",
        "Microprocessors",
        "Embedded Systems"
    ]
}

def display_sidebar_profile(student_data):
    """Display user profile in sidebar"""
    with st.sidebar:
        st.markdown("""
            <div class="profile-section">
                <img src="https://img.icons8.com/color/96/000000/user-male-circle.png" class="profile-image">
                <h3>{}</h3>
                <p>Grade {}</p>
            </div>
        """.format(student_data["name"], student_data["grade"]), unsafe_allow_html=True)
        
        # Study Stats
        st.markdown("### 📊 Study Stats")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Questions", st.session_state.get("questions_asked", 0))
        with col2:
            correct = st.session_state.get("correct_answers", 0)
            total = st.session_state.get("questions_asked", 0)
            accuracy = (correct / total * 100) if total > 0 else 0
            st.metric("Accuracy", f"{accuracy:.1f}%")
        
        # Course Categories with Interactive Checkboxes
        st.markdown("### 📚 Course Categories")
        
        # Initialize session state for selected category if not exists
        if "selected_category" not in st.session_state:
            st.session_state.selected_category = None
        
        # Display course categories with checkboxes
        for category in courses.keys():
            is_selected = st.checkbox(
                category,
                key=f"category_{category}",
                value=category == st.session_state.selected_category
            )
            if is_selected:
                st.session_state.selected_category = category
                st.session_state.subject = category.lower().replace(" ", "_")
                st.session_state.current_topic = courses[category][0]  # Set first course as default
                st.rerun()
        
        # Settings
        st.markdown("### ⚙️ Settings")
        
        # Language selection
        if "preferences" not in student_data:
            student_data["preferences"] = {}
        if "language" not in student_data["preferences"]:
            student_data["preferences"]["language"] = "English"
        
        language = st.selectbox(
            "Language",
            ["English", "Spanish", "French", "German", "Chinese"],
            index=["English", "Spanish", "French", "German", "Chinese"].index(student_data["preferences"]["language"])
        )
        
        # Theme selection
        if "theme" not in student_data["preferences"]:
            student_data["preferences"]["theme"] = "Dark"
        
        theme = st.selectbox(
            "Theme",
            ["Dark", "Light"],
            index=["Dark", "Light"].index(student_data["preferences"]["theme"])
        )
        
        # Notification settings
        if "notifications" not in student_data["preferences"]:
            student_data["preferences"]["notifications"] = True
        
        notifications = st.checkbox("Enable Notifications", value=student_data["preferences"]["notifications"])
        
        # Save settings
        if st.button("Save Settings"):
            student_data["preferences"].update({
                "language": language,
                "theme": theme,
                "notifications": notifications
            })
            
            student_manager.update_student_data(st.session_state.student_id, student_data)
            st.success("Settings saved!")
        
        # Logout button
        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()

def display_login():
    """Display login/registration form"""
    st.markdown('<h1 class="main-header">StudyBud: AI Personalized Study Planner</h1>', unsafe_allow_html=True)
    st.markdown('''
        <p class="subheader">Your intelligent study companion powered by BERT</p>
        <div class="feature-description">
            StudyBud is an intelligent application designed to create customized study plans based on your specific goals, 
            strengths, weaknesses, and preferences. Using advanced AI technology, we help you optimize your study schedule 
            to achieve your academic targets efficiently.
        </div>
    ''', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Login")
        login_id = st.text_input("Student ID", key="login_id")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            if student_manager.student_exists(login_id):
                # Get student data
                student_data = student_manager.get_student_data(login_id)
                
                # Verify password
                if student_data.get("password") == password:
                    # Initialize login tracking if not exists
                    if "login_tracking" not in student_data:
                        student_data["login_tracking"] = {
                            "last_login": None,
                            "login_streak": 0
                        }
                    
                    # Get current time
                    current_time = datetime.now()
                    
                    # Update login streak
                    if student_data["login_tracking"]["last_login"]:
                        last_login = datetime.fromisoformat(student_data["login_tracking"]["last_login"])
                        days_diff = (current_time.date() - last_login.date()).days
                        
                        if days_diff == 1:  # Consecutive day login
                            student_data["login_tracking"]["login_streak"] += 1
                        elif days_diff > 1:  # Streak broken
                            student_data["login_tracking"]["login_streak"] = 1
                        # If same day login, keep streak as is
                    else:
                        # First time login
                        student_data["login_tracking"]["login_streak"] = 1
                    
                    # Update last login time
                    student_data["login_tracking"]["last_login"] = current_time.isoformat()
                    
                    # Save updated data
                    student_manager.update_student_data(login_id, student_data)
                    
                    # Set session state
                    st.session_state.student_id = login_id
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Incorrect password. Please try again.")
            else:
                st.error("Student ID not found. Please register first.")

    with col2:
        st.subheader("Register")
        reg_id = st.text_input("Choose Student ID", key="reg_id")
        name = st.text_input("Your Name")
        password = st.text_input("Choose Password", type="password", key="reg_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
        grade = st.selectbox("Grade Level", list(range(1, 13)))
        
        # Course selection
        st.subheader("Select Your Courses")
        courses = {
            "Programming Fundamentals": [
                "Python Programming",
                "Java Programming",
                "C++ Programming",
                "JavaScript",
                "SQL Database",
                "Web Development Basics"
            ],
            "Data Structures & Algorithms": [
                "Arrays & Strings",
                "Linked Lists",
                "Stacks & Queues",
                "Trees & Graphs",
                "Sorting & Searching",
                "Dynamic Programming"
            ],
            "Web Development": [
                "HTML & CSS",
                "JavaScript Advanced",
                "React.js",
                "Node.js",
                "MongoDB",
                "RESTful APIs"
            ],
            "Mobile Development": [
                "Android Development",
                "iOS Development",
                "React Native",
                "Flutter",
                "Mobile UI/UX",
                "App Testing"
            ],
            "Artificial Intelligence": [
                "Machine Learning Basics",
                "Deep Learning",
                "Neural Networks",
                "Computer Vision",
                "Natural Language Processing",
                "AI Ethics"
            ],
            "Software Engineering": [
                "Software Design Patterns",
                "Clean Code",
                "Testing & QA",
                "DevOps & CI/CD",
                "Agile Methodologies",
                "Project Management"
            ],
            "Computer Networks": [
                "Network Protocols",
                "Network Security",
                "Cloud Computing",
                "Distributed Systems",
                "Network Architecture",
                "Cybersecurity"
            ],
            "Database Systems": [
                "SQL Advanced",
                "NoSQL Databases",
                "Database Design",
                "Data Warehousing",
                "Big Data",
                "Data Analytics"
            ],
            "Operating Systems": [
                "Process Management",
                "Memory Management",
                "File Systems",
                "System Security",
                "Shell Scripting",
                "System Administration"
            ],
            "Computer Architecture": [
                "Digital Logic",
                "Computer Organization",
                "Assembly Language",
                "Microprocessors",
                "Embedded Systems",
                "Hardware Design"
            ]
        }
        
        selected_courses = []
        for category, course_list in courses.items():
            with st.expander(f"📚 {category}", expanded=True):
                for course in course_list:
                    if st.checkbox(course, key=f"course_{category}_{course}"):
                        selected_courses.append(course)

        if st.button("Register"):
            if reg_id and name and password and confirm_password:
                if password != confirm_password:
                    st.error("Passwords do not match. Please try again.")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters long.")
                else:
                    if student_manager.create_student(reg_id, name, grade, selected_courses, password):
                        st.success("Registration successful! You can now login.")
                    else:
                        st.error("Student ID already exists. Please choose another.")
            else:
                st.error("Please fill all fields.")


def display_chat():
    """Display chat interface"""
    # Convert subject name to proper format for display
    subject_display_names = {
        "programming": "Programming",
        "web_dev": "Web Development",
        "mobile_dev": "Mobile Development",
        "ai": "Artificial Intelligence",
        "software_eng": "Software Engineering",
        "networks": "Computer Networks",
        "dbms": "Database Systems",
        "os": "Operating Systems",
        "computer_arch": "Computer Architecture"
    }
    
    display_subject = subject_display_names.get(st.session_state.subject, 
                                              st.session_state.subject.replace('_', ' ').title())
    st.subheader(f"{display_subject} Tutor")

    # Get the list of courses for the selected subject
    selected_courses = courses.get(display_subject, [])
    
    # If no courses found for the subject, show error
    if not selected_courses:
        st.error(f"No courses found for {display_subject}")
        return

    col1, col2 = st.columns([3, 1])
    with col1:
        # Topic selection using the courses dictionary
        st.session_state.current_topic = st.selectbox(
            "Select Course/Topic",
            selected_courses,
            index=0
        )

    with col2:
        st.write("")
        st.write("")
        if st.button("Get Topic Recommendations"):
            recommended = student_manager.get_recommended_topics(
                st.session_state.student_id,
                st.session_state.subject
            )
            if recommended:
                st.info(f"Recommended topics: {', '.join(recommended)}")
            else:
                st.info("Start learning to get personalized recommendations!")

    # Chat display
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history:
            if msg["role"] == "student":
                with st.chat_message("user"):
                    st.write(msg["content"])
            else:
                with st.chat_message("assistant"):
                    st.write(msg["content"])
                    if "audio_file" in msg and msg["audio_file"]:
                        try:
                            st.audio(msg["audio_file"])
                        except:
                            st.warning("Audio file not available")

    # Input area
    st.divider()
    col1, col2 = st.columns([4, 1])

    with col1:
        user_input = st.chat_input("Ask your question...")

    with col2:
        uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

    if user_input or uploaded_file:
        # Add user message to history
        st.session_state.chat_history.append({
            "role": "student",
            "content": user_input if user_input else "I've uploaded an image"
        })

        # Get student data
        student_data = student_manager.get_student_data(st.session_state.student_id)
        grade_level = student_data["grade"]
        
        # Convert UI language name to language code
        language_mapping = {
            "English": "en",
            "Spanish": "es",
            "French": "fr",
            "German": "de",
            "Chinese": "zh"
        }
        language = language_mapping.get(student_data["preferences"]["language"], "en")

        # Get AI response
        with st.spinner("Thinking..."):
            response = ai_tutor.ask_question(
                question=user_input,
                subject=st.session_state.subject,
                grade_level=grade_level,
                image_file=uploaded_file,
                language=language
            )

        # Add AI response to history
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response["text_response"],
            "audio_file": response["audio_file"]
        })

        # Update session count
        st.session_state.questions_asked += 1

        st.rerun()


def display_practice():
    """Display practice questions interface"""
    st.subheader("Practice Questions")

    # Initialize session state variables if they don't exist
    if "practice_questions" not in st.session_state:
        st.session_state.practice_questions = None
    if "current_answers" not in st.session_state:
        st.session_state.current_answers = []
    if "submitted" not in st.session_state:
        st.session_state.submitted = False
    if "score" not in st.session_state:
        st.session_state.score = 0
    if "questions_asked" not in st.session_state:
        st.session_state.questions_asked = 0
    if "correct_answers" not in st.session_state:
        st.session_state.correct_answers = 0

    # Get the current course and subject
    current_course = st.session_state.current_topic
    current_subject = st.session_state.subject

    # Display current course info
    st.info(f"Current Course: {current_course} ({current_subject.capitalize()})")

    # Question type selection
    question_type = st.radio(
        "Select Question Type",
        ["Multiple Choice", "Open-ended"],
        help="Choose the type of practice questions you want to attempt"
    )

    # Question count selection
    num_questions = st.slider("Number of Questions", min_value=1, max_value=10, value=5)

    if st.button("Generate New Practice Questions"):
        student_data = student_manager.get_student_data(st.session_state.student_id)
        with st.spinner("Generating questions..."):
            try:
                questions = ai_tutor.generate_practice_questions(
                    subject=current_subject,
                    topic=current_course,
                    difficulty=student_data["preferences"].get("difficulty_level", "medium"),
                    question_type=question_type,
                    num_questions=num_questions
                )
                st.session_state.practice_questions = questions
                st.session_state.current_answers = []
                st.session_state.submitted = False
                st.session_state.score = 0
                st.rerun()
            except Exception as e:
                st.error(f"Error generating questions: {str(e)}")
                return

    if st.session_state.practice_questions:
        # Display questions
        for i, question in enumerate(st.session_state.practice_questions):
            st.markdown(f"### Question {i+1}")
            st.markdown(question.get("question", "Error: Question not found"))
            
            if question_type == "Multiple Choice":
                options = question.get("options", [])
                if options:
                    # Display multiple choice options
                    selected_option = st.radio(
                        f"Select your answer for Question {i+1}",
                        options,
                        key=f"q_{i}"
                    )
                    
                    # Store answer
                    while len(st.session_state.current_answers) <= i:
                        st.session_state.current_answers.append(None)
                    st.session_state.current_answers[i] = selected_option
            else:
                # Open-ended response
                answer = st.text_area(
                    "Your answer:",
                    key=f"q_{i}",
                    height=100
                )
                
                # Store answer
                while len(st.session_state.current_answers) <= i:
                    st.session_state.current_answers.append("")
                st.session_state.current_answers[i] = answer

        # Submit button
        if st.button("Submit Answers"):
            st.session_state.submitted = True
            
            if question_type == "Multiple Choice":
                # Calculate score for multiple choice
                correct_count = sum(
                    1 for q, a in zip(st.session_state.practice_questions, st.session_state.current_answers)
                    if a == q.get("correct_answer")
                )
                st.session_state.score = (correct_count / len(st.session_state.practice_questions)) * 100
                
                # Display results
                st.markdown("### Results")
                st.metric("Your Score", f"{st.session_state.score:.1f}%")
                
                # Show detailed feedback
                for i, (question, answer) in enumerate(zip(st.session_state.practice_questions, st.session_state.current_answers)):
                    with st.expander(f"Question {i+1} Feedback"):
                        st.markdown(question.get("question", ""))
                        st.markdown(f"Your answer: **{answer}**")
                        st.markdown(f"Correct answer: **{question.get('correct_answer', '')}**")
                        if answer == question.get("correct_answer"):
                            st.success("Correct! " + question.get("explanation", ""))
                        else:
                            st.error("Incorrect. " + question.get("explanation", ""))
            else:
                # For open-ended questions, use AI to evaluate answers
                student_data = student_manager.get_student_data(st.session_state.student_id)
                total_score = 0
                
                st.markdown("### Results")
                for i, (question, answer) in enumerate(zip(st.session_state.practice_questions, st.session_state.current_answers)):
                    with st.expander(f"Question {i+1} Feedback", expanded=True):
                        evaluation = ai_tutor.evaluate_answer(
                            question=question.get("question", ""),
                            student_answer=answer,
                            subject=current_subject,
                            grade_level=student_data["grade"]
                        )
                        st.markdown(evaluation)
                        
                        # Extract score from evaluation (assuming AI returns score in the format "Score: X/100")
                        try:
                            score_line = [line for line in evaluation.split('\n') if 'Score' in line][0]
                            question_score = float(score_line.split(':')[1].strip().split('/')[0])
                            total_score += question_score
                        except:
                            question_score = 0
                
                # Calculate and display average score
                st.session_state.score = total_score / len(st.session_state.practice_questions)
                st.metric("Overall Score", f"{st.session_state.score:.1f}%")
            
            # Update student progress
            student_data = student_manager.get_student_data(st.session_state.student_id)
            if "progress" not in student_data:
                student_data["progress"] = {}
            if current_subject not in student_data["progress"]:
                student_data["progress"][current_subject] = {}
            
            # Update topic progress
            topic_progress = student_data["progress"][current_subject].get(current_course, [])
            topic_progress.append(st.session_state.score)
            student_data["progress"][current_subject][current_course] = topic_progress
            
            # Update total questions and correct answers
            st.session_state.questions_asked += len(st.session_state.practice_questions)
            st.session_state.correct_answers += int((st.session_state.score / 100) * len(st.session_state.practice_questions))
            
            # Save updated progress
            student_manager.update_student_data(st.session_state.student_id, student_data)
            
            # Show encouragement message
            if st.session_state.score >= 80:
                st.balloons()
                st.success("Excellent work! You've mastered this topic! 🌟")
            elif st.session_state.score >= 60:
                st.success("Good job! Keep practicing to improve further! 💪")
            else:
                st.info("Keep practicing! Review the topics and try again. 📚")


def display_progress():
    """Display progress tracking interface"""
    st.subheader("My Progress")

    # Get student data and progress
    student_data = student_manager.get_student_data(st.session_state.student_id)
    
    # Initialize progress if not exists
    if "topic_progress" not in student_data:
        student_data["topic_progress"] = {}
    
    # Topics by category
    topics_by_category = {
        "Programming Fundamentals": [
            "Variables & Data Types",
            "Control Flow",
            "Functions",
            "Object-Oriented Programming",
            "Error Handling",
            "File I/O"
        ],
        "Data Structures": [
            "Arrays & Lists",
            "Stacks & Queues",
            "Trees",
            "Graphs",
            "Hash Tables",
            "Heaps"
        ],
        "Web Development": [
            "HTML & CSS",
            "JavaScript Basics",
            "DOM Manipulation",
            "API Integration",
            "React Components",
            "State Management"
        ],
        "Database Systems": [
            "SQL Basics",
            "Database Design",
            "Normalization",
            "Indexing",
            "Transactions",
            "NoSQL Concepts"
        ],
        "Software Engineering": [
            "Version Control",
            "Testing Methods",
            "Design Patterns",
            "Code Review",
            "CI/CD",
            "Agile Practices"
        ]
    }
    
    # Display overall progress
    st.markdown("### 📊 Overall Progress")
    progress_col1, progress_col2, progress_col3 = st.columns(3)
    
    # Calculate overall progress
    total_topics = sum(len(topics) for topics in topics_by_category.values())
    completed_topics = sum(1 for topic_status in student_data["topic_progress"].values() if topic_status)
    overall_progress = (completed_topics / total_topics) * 100 if total_topics > 0 else 0
    
    with progress_col1:
        st.metric("Progress", f"{overall_progress:.1f}%")
    with progress_col2:
        st.metric("Topics Completed", f"{completed_topics}/{total_topics}")
    with progress_col3:
        login_streak = student_data.get("login_tracking", {}).get("login_streak", 0)
        st.metric(
            "Login Streak", 
            f"{login_streak} days",
            help="Number of consecutive days you've logged in"
        )
    
    # Display topic progress by category
    st.markdown("### 📚 Topic Progress")
    
    # Track changes to update progress
    topics_changed = False
    
    for category, topics in topics_by_category.items():
        with st.expander(f"📘 {category}", expanded=True):
            # Create columns for better layout
            cols = st.columns(2)
            for i, topic in enumerate(topics):
                col = cols[i % 2]
                with col:
                    # Check if topic was previously completed
                    was_completed = student_data["topic_progress"].get(topic, False)
                    
                    # Create checkbox with previous state
                    is_completed = st.checkbox(
                        topic,
                        value=was_completed,
                        key=f"topic_{category}_{topic}"
                    )
                    
                    # If checkbox state changed, update progress
                    if is_completed != was_completed:
                        student_data["topic_progress"][topic] = is_completed
                        topics_changed = True
                        
                        # Show celebration on completion
                        if is_completed and not was_completed:
                            st.success(f"🎉 Completed: {topic}")
                            if len([t for t in student_data["topic_progress"].values() if t]) % 5 == 0:
                                st.balloons()
    
    # Update progress bars for each category
    st.markdown("### 📈 Category Progress")
    category_cols = st.columns(len(topics_by_category))
    for i, (category, topics) in enumerate(topics_by_category.items()):
        with category_cols[i]:
            completed_in_category = sum(1 for topic in topics if student_data["topic_progress"].get(topic, False))
            category_progress = (completed_in_category / len(topics)) * 100
            st.progress(category_progress / 100)
            st.caption(f"{category}: {category_progress:.1f}%")
    
    # Achievement badges
    st.markdown("### 🏆 Achievements")
    achievement_cols = st.columns(3)
    
    # Define achievements and their criteria
    achievements = {
        "Quick Starter": {"required": 5, "icon": "🚀", "description": "Complete 5 topics"},
        "Half Way There": {"required": total_topics // 2, "icon": "🎯", "description": f"Complete {total_topics // 2} topics"},
        "Master Learner": {"required": total_topics, "icon": "👑", "description": f"Complete all {total_topics} topics"}
    }
    
    # Display achievements
    for i, (badge, info) in enumerate(achievements.items()):
        with achievement_cols[i]:
            progress = min(completed_topics / info["required"], 1.0) * 100
            st.markdown(f"### {info['icon']}")
            st.progress(progress / 100)
            st.markdown(f"**{badge}**")
            st.caption(f"{info['description']}")
            if completed_topics >= info["required"]:
                st.success("Unlocked!")
            else:
                st.info(f"{completed_topics}/{info['required']} topics")
    
    # Save progress if changes were made
    if topics_changed:
        # Save updated data
        student_manager.update_student_data(st.session_state.student_id, student_data)
        
        # Force refresh to update progress bars
        st.rerun()


def display_study_plan():
    """Display personalized study planner interface"""
    st.subheader("Your Personalized Study Plan")
    
    # Get student data
    student_data = student_manager.get_student_data(st.session_state.student_id)
    
    # Study Goals Section
    st.markdown("### 📚 Study Goals")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Weekly study hours
        weekly_hours = st.slider(
            "Weekly Study Hours Target",
            min_value=1,
            max_value=40,
            value=student_data.get("study_preferences", {}).get("weekly_hours", 20),
            help="Set your target study hours per week"
        )
        
        # Preferred study times
        study_times = st.multiselect(
            "Preferred Study Times",
            ["Early Morning (6-9 AM)", "Morning (9-12 PM)", "Afternoon (12-4 PM)", 
             "Evening (4-8 PM)", "Night (8-11 PM)"],
            default=student_data.get("study_preferences", {}).get("preferred_times", ["Morning (9-12 PM)"])
        )
    
    with col2:
        # Study style preferences
        st.markdown("#### Learning Style")
        visual = st.checkbox("Visual Learning", value=True)
        auditory = st.checkbox("Auditory Learning")
        practical = st.checkbox("Hands-on Practice")
    
    # Priority Subjects
    st.markdown("### 📋 Subject Priorities")
    priorities = {}
    cols = st.columns(3)
    for i, subject in enumerate(ALLOWED_SUBJECTS):
        with cols[i % 3]:
            priorities[subject] = st.select_slider(
                f"{SUBJECT_DISPLAY_NAMES[subject]}",
                options=["Low", "Medium", "High"],
                value=student_data.get("subject_priorities", {}).get(subject, "Medium")
            )
    
    # Generate/Update Plan
    if st.button("Generate Study Plan"):
        with st.spinner("Analyzing your preferences and generating personalized study plan..."):
            # Save preferences
            student_data["study_preferences"] = {
                "weekly_hours": weekly_hours,
                "preferred_times": study_times,
                "learning_styles": {
                    "visual": visual,
                    "auditory": auditory,
                    "practical": practical
                }
            }
            student_data["subject_priorities"] = priorities
            student_manager.update_student_data(st.session_state.student_id, student_data)
            
            # Display generated plan
            st.markdown("### 📅 Your Weekly Study Schedule")
            
            # Create schedule grid
            schedule = generate_study_schedule(student_data)
            for day, sessions in schedule.items():
                with st.expander(f"📆 {day}", expanded=True):
                    for session in sessions:
                        st.markdown(f"""
                        * **{session['time']}**: {session['subject']} - {session['topic']}
                          * Focus: {session['focus']}
                          * Learning Style: {session['style']}
                        """)
            
            # Progress tracking
            st.markdown("### 📊 Progress Overview")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Weekly Progress", f"{student_data.get('weekly_progress', 0)}%", "+5%")
            with col2:
                st.metric("Topics Covered", str(student_data.get('topics_covered', 0)), "+2")
            with col3:
                st.metric("Study Streak", f"{student_data.get('study_streak', 0)} days", "+1")


def display_about():
    """Display About Us section"""
    st.title("About StudyBud")
    
    # Mission and Vision
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Our Mission")
        st.info("To revolutionize online learning through AI-powered personalized education, making quality education accessible to everyone.")
    
    with col2:
        st.markdown("### 👁️ Our Vision")
        st.info("To become the leading AI-driven educational platform that transforms how students learn and master technical subjects.")

    # Features
    st.markdown("## 🌟 Why Choose StudyBud?")
    feat_col1, feat_col2, feat_col3, feat_col4 = st.columns(4)
    
    with feat_col1:
        st.markdown("### 🤖 AI-Powered Learning")
        st.write("Advanced AI tutoring system that adapts to your learning style and pace.")
    
    with feat_col2:
        st.markdown("### 📊 Progress Tracking")
        st.write("Comprehensive progress monitoring and performance analytics.")
    
    with feat_col3:
        st.markdown("### 🎯 Personalized Plans")
        st.write("Custom study schedules based on your goals and preferences.")
    
    with feat_col4:
        st.markdown("### 🏆 Achievement System")
        st.write("Gamified learning experience with badges and rewards.")

    # Team
    st.markdown("## 👥 Our Team")
    team_col1, team_col2, team_col3 = st.columns(3)
    
    with team_col1:
        st.image("https://img.icons8.com/color/96/000000/administrator-male.png", width=120)
        st.markdown("### Dr. Sarah Johnson")
        st.write("Lead AI Researcher")
    
    with team_col2:
        st.image("https://img.icons8.com/color/96/000000/administrator-female.png", width=120)
        st.markdown("### Prof. Michael Chen")
        st.write("Education Director")
    
    with team_col3:
        st.image("https://img.icons8.com/color/96/000000/user-male.png", width=120)
        st.markdown("### Alex Thompson")
        st.write("Lead Developer")


def display_contact():
    """Display Contact Us section"""
    st.title("Contact Us")
    
    # Contact Information
    info_col1, info_col2 = st.columns(2)
    
    with info_col1:
        st.markdown("### 📍 Our Location")
        st.write("123 Education Street")
        st.write("Tech Valley, CA 94025")
        st.write("United States")
        
        st.markdown("### 📞 Phone")
        st.write("+1 (555) 123-4567")
        
        st.markdown("### ✉️ Email")
        st.write("support@studybud.com")
    
    with info_col2:
        st.markdown("### ⏰ Hours of Operation")
        st.write("Monday - Friday: 9:00 AM - 6:00 PM PST")
        st.write("Saturday: 10:00 AM - 4:00 PM PST")
        st.write("Sunday: Closed")
    
    # Contact Form
    st.markdown("## 📝 Send us a Message")
    
    form_col1, form_col2 = st.columns(2)
    with form_col1:
        name = st.text_input("Your Name")
        email = st.text_input("Your Email")
    
    with form_col2:
        subject = st.text_input("Subject")
        message = st.text_area("Message")
    
    if st.button("Send Message", type="primary"):
        if name and email and subject and message:
            st.success("Thank you for your message! We'll get back to you soon.")
        else:
            st.error("Please fill in all fields.")
    
    # Social Links
    st.markdown("## 🌐 Follow Us")
    social_col1, social_col2, social_col3, social_col4 = st.columns(4)
    
    with social_col1:
        st.image("https://img.icons8.com/color/48/000000/facebook-new.png", width=40)
        st.write("[Facebook](#)")
    
    with social_col2:
        st.image("https://img.icons8.com/color/48/000000/twitter.png", width=40)
        st.write("[Twitter](#)")
    
    with social_col3:
        st.image("https://img.icons8.com/color/48/000000/linkedin.png", width=40)
        st.write("[LinkedIn](#)")
    
    with social_col4:
        st.image("https://img.icons8.com/color/48/000000/instagram-new.png", width=40)
        st.write("[Instagram](#)")

def display_courses():
    """Display courses dashboard"""
    st.title("📚 Course Dashboard")
    
    # Get student data
    student_data = student_manager.get_student_data(st.session_state.student_id)
    
    # Course category selection
    st.markdown("### Select Course Category")
    selected_category = st.selectbox(
        "Choose a Category",
        list(courses.keys()),
        key="category_selection",
        help="Select a course category to view available courses"
    )
    
    if selected_category:
        # Update session state with selected category
        st.session_state.subject = selected_category.lower().replace(" ", "_")
        
        # Display courses for selected category
        st.markdown(f"### Available Courses in {selected_category}")
        
        # Create columns for course cards
        cols = st.columns(2)
        
        for idx, course in enumerate(courses[selected_category]):
            with cols[idx % 2]:
                st.markdown(f"""
                <div class="course-card">
                    <div class="course-icon">📚</div>
                    <h3>{course}</h3>
                    <div class="course-details">
                        <span class="course-level">Level: {'Beginner' if idx < 2 else 'Intermediate' if idx < 4 else 'Advanced'}</span>
                        <span class="course-duration">Duration: 8 weeks</span>
                    </div>
                    <div class="course-description">
                        Master {course} fundamentals and advanced concepts through interactive learning.
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Add buttons for each course
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Start Learning", key=f"start_{course}"):
                        st.session_state.current_topic = course
                        st.session_state.current_course = course
                        st.session_state.active_tab = "🤖 AI Tutor"
                        st.rerun()
                
                with col2:
                    if st.button("Text-to-Speech", key=f"tts_{course}"):
                        # Generate course description for TTS
                        description = f"Welcome to {course}. This is a {selected_category} course. "
                        description += "You will learn fundamental concepts and advanced topics. "
                        description += "The course duration is 8 weeks. "
                        description += "Let's begin your learning journey!"
                        
                        # Use browser's built-in speech synthesis
                        st.markdown(f"""
                        <script>
                            const utterance = new SpeechSynthesisUtterance("{description}");
                            utterance.lang = "en-US";
                            window.speechSynthesis.speak(utterance);
                        </script>
                        """, unsafe_allow_html=True)
        
        # Update student's courses if not already enrolled
        if "courses" not in student_data:
            student_data["courses"] = []
        for course in courses[selected_category]:
            if course not in student_data["courses"]:
                student_data["courses"].append(course)
        student_manager.update_student_data(st.session_state.student_id, student_data)

# App configuration
st.set_page_config(
    page_title=APP_NAME,
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize services
ai_tutor, student_manager = init_services()

# Custom CSS
st.markdown("""
<style>
    /* Global Styles */
    [data-testid="stAppViewContainer"] {
        background: #1a1a1a;
        color: #e0e0e0;
    }
    
    /* Dark theme overlay */
    [data-testid="stAppViewContainer"]::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(26, 26, 26, 0.85);
        z-index: -1;
    }
    
    /* Light theme overlay */
    [data-testid="stAppViewContainer"][data-theme="light"]::before {
        background: rgba(255, 255, 255, 0.85);
    }
    
    .main-header {
        background: linear-gradient(135deg, #2c3e50, #1a1a1a);
        color: white;
        padding: 3rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    .subheader {
        color: #b0b0b0;
        text-align: center;
        font-size: 1.3em;
        margin: 1rem 0 2rem;
        font-weight: 300;
    }
    
    /* Cards and Containers */
    .stCard {
        background: #2c2c2c;
        color: #e0e0e0;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.2);
        margin: 1rem 0;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .stCard:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        background: #323232;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #2c2c2c;
        padding: 2rem 1rem;
        box-shadow: 2px 0 10px rgba(0,0,0,0.2);
    }
    
    [data-testid="stSidebar"] .stButton>button {
        width: 100%;
        margin: 0.5rem 0;
    }
    
    /* Buttons and Interactive Elements */
    .stButton>button {
        background: linear-gradient(135deg, #2c3e50, #34495e);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #34495e, #2c3e50);
        transform: translateY(-2px);
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    
    /* Form Elements */
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea {
        background: #2c2c2c;
        color: #e0e0e0;
        border: 2px solid #404040;
        border-radius: 8px;
        padding: 0.75rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput>div>div>input:focus,
    .stTextArea>div>div>textarea:focus {
        border-color: #2c3e50;
        box-shadow: 0 0 0 2px rgba(44,62,80,0.3);
    }
    
    /* Progress Bars and Metrics */
    .stProgress>div>div>div {
        background: linear-gradient(90deg, #2c3e50, #34495e);
        border-radius: 10px;
    }
    
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 600;
        color: #3498db;
    }
    
    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: #2c2c2c;
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 60px;
        background-color: transparent;
        border: 2px solid #404040;
        border-radius: 8px;
        padding: 15px 25px;
        font-weight: 500;
        transition: all 0.3s ease;
        color: #e0e0e0;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #323232;
        border-color: #2c3e50;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #2c3e50, #34495e) !important;
        color: white !important;
        border: none !important;
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background: #2c2c2c;
        border-radius: 8px;
        padding: 1rem;
        font-weight: 500;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        color: #e0e0e0;
    }
    
    /* Chat Interface */
    [data-testid="stChatMessage"] {
        background: #2c2c2c;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        color: #e0e0e0;
    }
    
    /* Alerts and Notifications */
    .stAlert {
        background: #2c2c2c;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        color: #e0e0e0;
    }
    
    /* Custom Classes */
    .feature-card {
        background: #2c2c2c;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        text-align: center;
        transition: transform 0.3s ease;
        color: #e0e0e0;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        background: #323232;
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        color: #3498db;
    }
    
    .achievement-card {
        background: linear-gradient(135deg, #2c3e50, #34495e);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .profile-section {
        text-align: center;
        padding: 2rem;
        background: #2c2c2c;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        color: #e0e0e0;
    }
    
    .profile-image {
        width: 120px;
        height: 120px;
        border-radius: 60px;
        margin: 0 auto 1rem;
        border: 4px solid #2c3e50;
    }

    /* Additional Dark Theme Elements */
    .stSelectbox>div>div {
        background-color: #2c2c2c;
        color: #e0e0e0;
    }

    .stMultiSelect>div>div {
        background-color: #2c2c2c;
        color: #e0e0e0;
    }

    .stSlider>div>div {
        background-color: #2c2c2c;
        color: #e0e0e0;
    }

    /* Info, Success, and Error Messages */
    .stSuccess {
        background-color: rgba(46, 204, 113, 0.2);
        color: #2ecc71;
    }

    .stInfo {
        background-color: rgba(52, 152, 219, 0.2);
        color: #3498db;
    }

    .stError {
        background-color: rgba(231, 76, 60, 0.2);
        color: #e74c3c;
    }

    /* Code Blocks */
    .stCodeBlock {
        background-color: #1a1a1a !important;
        color: #e0e0e0 !important;
    }

    /* Tooltips */
    .stTooltipIcon {
        color: #3498db;
    }

    /* Radio Buttons and Checkboxes */
    .stRadio>div {
        color: #e0e0e0;
    }

    .stCheckbox>div {
        color: #e0e0e0;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main-header {
            padding: 2rem;
        }
        
        .feature-card {
            margin-bottom: 1rem;
        }
        
        [data-testid="stMetricValue"] {
            font-size: 1.5rem;
        }
    }

    /* Course Card Styling */
    .course-card {
        background: #2c2c2c;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        transition: all 0.3s ease;
        border: 2px solid #404040;
        height: 100%;
    }
    
    .course-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        border-color: #3498db;
        background: #323232;
    }
    
    .course-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        color: #3498db;
    }
    
    .course-card h3 {
        color: #e0e0e0;
        margin: 0.5rem 0;
        font-size: 1.3rem;
    }
    
    .course-details {
        margin: 0.5rem 0;
        font-size: 0.9rem;
        color: #b0b0b0;
    }
    
    .course-level {
        background: rgba(52, 152, 219, 0.2);
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        color: #3498db;
    }
    
    .course-duration {
        margin-left: 0.5rem;
    }
    
    .course-description {
        color: #b0b0b0;
        font-size: 0.9rem;
        margin-top: 1rem;
        line-height: 1.4;
    }
    
    /* Course Progress Bar */
    .course-progress {
        margin-top: 1rem;
        background: #404040;
        border-radius: 10px;
        height: 6px;
        overflow: hidden;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #3498db, #2ecc71);
        border-radius: 10px;
        transition: width 0.3s ease;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables if they don't exist
if "subject" not in st.session_state:
    st.session_state.subject = "programming"  # Default to programming

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "student_id" not in st.session_state:
    st.session_state.student_id = None

if "current_topic" not in st.session_state:
    st.session_state.current_topic = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "active_tab" not in st.session_state:
    st.session_state.active_tab = "📚 Study Plan"

if "current_course" not in st.session_state:
    st.session_state.current_course = None

# Main app logic
if not st.session_state.authenticated:
    display_login()
else:
    # Subject selection
    st.sidebar.title("Navigation")
    
    # Convert subject names for display
    subject_display_names = {
        "programming": "Programming",
        "web_dev": "Web Development",
        "mobile_dev": "Mobile Development",
        "ai": "Artificial Intelligence",
        "software_eng": "Software Engineering",
        "networks": "Computer Networks",
        "dbms": "Database Systems",
        "os": "Operating Systems",
        "computer_arch": "Computer Architecture"
    }
    
    # Create a list of display names for the radio button
    display_subjects = [subject_display_names.get(subject, subject.replace('_', ' ').title()) 
                       for subject in ALLOWED_SUBJECTS]
    
    selected_display = st.sidebar.radio(
        "Choose a subject",
        display_subjects,
        index=display_subjects.index(subject_display_names.get(st.session_state.subject, 
                                                              st.session_state.subject.replace('_', ' ').title()))
    )
    
    # Convert display name back to internal format
    selected_subject = next((k for k, v in subject_display_names.items() if v == selected_display), 
                          selected_display.lower().replace(' ', '_'))
    
    if selected_subject != st.session_state.subject:
        st.session_state.subject = selected_subject
        st.session_state.current_topic = None
        st.session_state.chat_history = []
        st.rerun()

    # Get student data
    student_data = student_manager.get_student_data(st.session_state.student_id)

    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/student-male--v1.png", width=100)
        st.subheader(f"Welcome, {student_data['name']}!")
        st.write(f"Grade: {student_data['grade']}")

        # Display badges
        if student_data.get("badges"):
            st.divider()
            st.subheader("Your Badges")
            badges_html = ""
            for badge in student_data["badges"]:
                badges_html += f'<div class="badge">{badge}</div>'
            st.markdown(badges_html, unsafe_allow_html=True)

        st.divider()

        # Settings
        st.subheader("Settings")
        language = st.selectbox(
            "Language",
            ["en", "es", "fr", "de", "zh", "hi", "ar", "ru"],
            format_func=lambda x: {
                "en": "English", "es": "Spanish", "fr": "French",
                "de": "German", "zh": "Chinese", "hi": "Hindi",
                "ar": "Arabic", "ru": "Russian"
            }.get(x, x),
            index=0
        )
        student_data["preferences"]["language"] = language

        difficulty = st.select_slider(
            "Difficulty Level",
            options=["easy", "medium", "hard"],
            value=student_data["preferences"]["difficulty_level"]
        )
        student_data["preferences"]["difficulty_level"] = difficulty

        # Save preferences
        student_manager.update_student_data(st.session_state.student_id, student_data)

        st.divider()

        # Logout button
        if st.button("Logout"):
            st.session_state.student_id = None
            st.session_state.authenticated = False
            st.rerun()

    # Main content
    tab1, tab2, tab3, tab4 = st.tabs(["Study Plan", "Tutor Chat", "Practice Questions", "My Progress"])

    with tab1:
        display_study_plan()

    with tab2:
        display_chat()

    with tab3:
        display_practice()

    with tab4:
        display_progress() 