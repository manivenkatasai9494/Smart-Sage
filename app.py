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
        if st.button("Login"):
            if student_manager.student_exists(login_id):
                # Get student data
                student_data = student_manager.get_student_data(login_id)
                
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
                st.error("Student ID not found. Please register first.")

    with col2:
        st.subheader("Register")
        reg_id = st.text_input("Choose Student ID", key="reg_id")
        name = st.text_input("Your Name")
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
            if reg_id and name:
                if student_manager.create_student(reg_id, name, grade, selected_courses):
                    st.success("Registration successful! You can now login.")
                else:
                    st.error("Student ID already exists. Please choose another.")
            else:
                st.error("Please fill all fields.")


def display_chat():
    """Display chat interface"""
    st.subheader(f"{st.session_state.subject.capitalize()} Tutor")

    # Topic selection
    topics = {
        "programming": ["Python", "Java", "C++", "JavaScript", "SQL"],
        "web_dev": ["HTML/CSS", "React", "Node.js", "MongoDB", "APIs"],
        "mobile_dev": ["Android", "iOS", "React Native", "Flutter", "UI/UX"],
        "ai": ["Machine Learning", "Deep Learning", "Computer Vision", "NLP", "AI Ethics"],
        "software_eng": ["Design Patterns", "Clean Code", "Testing", "DevOps", "Agile"],
        "networks": ["Protocols", "Security", "Cloud", "Distributed Systems", "Cybersecurity"],
        "databases": ["SQL", "NoSQL", "Design", "Big Data", "Analytics"],
        "os": ["Process Management", "Memory", "File Systems", "Security", "Shell Scripting"],
        "architecture": ["Digital Logic", "Organization", "Assembly", "Microprocessors", "Embedded"]
    }

    col1, col2 = st.columns([3, 1])
    with col1:
        st.session_state.current_topic = st.selectbox(
            "Select Topic",
            topics[st.session_state.subject],
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
        language = student_data["preferences"]["language"]

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
                    subject=st.session_state.subject,
                    topic=st.session_state.current_topic,
                    difficulty=student_data["preferences"]["difficulty_level"],
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
                            subject=st.session_state.subject,
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
            if st.session_state.subject not in student_data["progress"]:
                student_data["progress"][st.session_state.subject] = {}
            
            # Update topic progress
            topic_progress = student_data["progress"][st.session_state.subject].get(st.session_state.current_topic, [])
            topic_progress.append(st.session_state.score)
            student_data["progress"][st.session_state.subject][st.session_state.current_topic] = topic_progress
            
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
    .main-header {
        color: #1E88E5;
        text-align: center;
        font-size: 3em;
        margin-bottom: 20px;
    }
    .subheader {
        color: #424242;
        text-align: center;
        font-size: 1.5em;
        margin-bottom: 30px;
    }
    .badge {
        background-color: #1E88E5;
        color: white;
        padding: 5px 10px;
        border-radius: 10px;
        margin: 5px;
        display: inline-block;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        border-radius: 4px 4px 0px 0px;
        padding: 10px 16px;
        background-color: #33373b;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1E88E5 !important;
        color: white !important;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .chat-message.user {
        background-color: #2b313e;
    }
    .chat-message.bot {
        background-color: #475063;
    }
    .chat-message .message-content {
        display: flex;
        margin-bottom: 0.5rem;
    }
    .chat-message .message-content img {
        width: 42px;
        height: 42px;
        border-radius: 3px;
        margin-right: 1rem;
    }
    .chat-message .message-content .message {
        padding: 0.5rem 1rem;
        border-radius: 3px;
    }
    .chat-message .message-content .message p {
        margin: 0;
    }
    .feature-description {
        background-color: rgba(30, 136, 229, 0.1);
        border-left: 4px solid #1E88E5;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 4px 4px 0;
        font-size: 1.1em;
        line-height: 1.6;
    }
    
    /* Study Plan Styles */
    .stSlider {
        padding: 1rem 0;
    }
    
    .study-session {
        background-color: #2b313e;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    .study-session:hover {
        transform: translateY(-2px);
        transition: transform 0.2s ease;
    }
    
    .metric-card {
        background-color: #1E88E5;
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
    
    .metric-card h3 {
        margin: 0;
        font-size: 2em;
    }
    
    .metric-card p {
        margin: 0;
        opacity: 0.8;
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

# Main app logic
if not st.session_state.authenticated:
    display_login()
else:
    # Subject selection
    st.sidebar.title("Navigation")
    selected_subject = st.sidebar.radio(
        "Choose a subject",
        ALLOWED_SUBJECTS,
        format_func=lambda x: SUBJECT_DISPLAY_NAMES[x],
        index=ALLOWED_SUBJECTS.index(st.session_state.subject)
    )
    
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