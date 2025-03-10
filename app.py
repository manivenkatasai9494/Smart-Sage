import os

import streamlit as st
import streamlit.components.v1 as components
from PIL import Image

from ai_service import AITutorService
from config import ALLOWED_SUBJECTS, APP_NAME, SUBJECT_DISPLAY_NAMES
from student_manager import StudentManager


# Initialize services
@st.cache_resource
def init_services():
    return AITutorService(), StudentManager()


def display_login():
    """Display login/registration form"""
    st.markdown('<h1 class="main-header">AI Learning Companion</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subheader">Your personalized tutor for Computer Science and Technology</p>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Login")
        login_id = st.text_input("Student ID", key="login_id")
        if st.button("Login"):
            if student_manager.student_exists(login_id):
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

    if st.button("Generate New Practice Questions"):
        student_data = student_manager.get_student_data(st.session_state.student_id)
        with st.spinner("Generating questions..."):
            questions = ai_tutor.generate_practice_questions(
                subject=st.session_state.subject,
                topic=st.session_state.current_topic,
                difficulty=student_data["preferences"]["difficulty_level"]
            )
            st.session_state.practice_questions = questions

    if st.session_state.practice_questions:
        st.markdown(st.session_state.practice_questions)

        st.divider()
        st.subheader("Submit Your Answer")
        answer = st.text_area("Your solution:", height=150)

        if st.button("Check Answer"):
            if answer:
                student_data = student_manager.get_student_data(st.session_state.student_id)
                evaluation = ai_tutor.evaluate_answer(
                    question=st.session_state.practice_questions,
                    student_answer=answer,
                    subject=st.session_state.subject,
                    grade_level=student_data["grade"]
                )
                st.markdown(evaluation)


def display_progress():
    """Display progress tracking interface"""
    st.subheader("My Progress")

    report = student_manager.generate_performance_report(st.session_state.student_id)
    if isinstance(report, str):
        st.info(report)
    elif report:
        st.markdown(report["summary"])
        if report.get("report_file") and os.path.exists(report["report_file"]):
            st.image(report["report_file"])


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

if "practice_questions" not in st.session_state:
    st.session_state.practice_questions = None

if "questions_asked" not in st.session_state:
    st.session_state.questions_asked = 0

if "correct_answers" not in st.session_state:
    st.session_state.correct_answers = 0

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
        if student_data["badges"]:
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
    tab1, tab2, tab3 = st.tabs(["Tutor Chat", "Practice Questions", "My Progress"])

    with tab1:
        display_chat()

    with tab2:
        display_practice()

    with tab3:
        display_progress() 