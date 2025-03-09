import os

import streamlit as st
import streamlit.components.v1 as components
from PIL import Image

from ai_service import AITutorService
from study_planner import StudyPlanner
from onboarding import OnboardingManager
from assessment import AssessmentManager
from config import ALLOWED_SUBJECTS, APP_NAME
from student_manager import StudentManager


# Initialize services
@st.cache_resource
def init_services():
    student_manager = StudentManager()
    return (
        AITutorService(),
        student_manager,
        StudyPlanner(),
        OnboardingManager(student_manager),
        AssessmentManager(student_manager)
    )


# App configuration
st.set_page_config(
    page_title=APP_NAME,
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize services
ai_tutor, student_manager, study_planner, onboarding_manager, assessment_manager = init_services()

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
    .study-plan {
        background-color: #2b313e;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .study-session {
        background-color: #475063;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .progress-bar {
        height: 20px;
        background-color: #1E88E5;
        border-radius: 10px;
    }
    .goal-card {
        background-color: #1E88E5;
        padding: 15px;
        border-radius: 5px;
        margin: 5px 0;
        color: white;
    }
    .nav-button {
        background-color: #1E88E5;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        margin: 5px;
        text-align: center;
        cursor: pointer;
    }
    .back-button {
        background-color: #424242;
        color: white;
        padding: 5px 15px;
        border-radius: 5px;
        margin: 5px;
        text-align: center;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if "student_id" not in st.session_state:
    st.session_state.student_id = None
if "onboarding_complete" not in st.session_state:
    st.session_state.onboarding_complete = False
if "assessment_complete" not in st.session_state:
    st.session_state.assessment_complete = False
if "current_view" not in st.session_state:
    st.session_state.current_view = "main"
if "navigation_history" not in st.session_state:
    st.session_state.navigation_history = []
if "subject" not in st.session_state:
    st.session_state.subject = "math"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_topic" not in st.session_state:
    st.session_state.current_topic = None
if "practice_questions" not in st.session_state:
    st.session_state.practice_questions = None
if "questions_asked" not in st.session_state:
    st.session_state.questions_asked = 0
if "correct_answers" not in st.session_state:
    st.session_state.correct_answers = 0
if "current_plan" not in st.session_state:
    st.session_state.current_plan = None


def navigate_to(view):
    """Handle navigation between views"""
    st.session_state.navigation_history.append(st.session_state.current_view)
    st.session_state.current_view = view
    st.rerun()

def go_back():
    """Handle navigation back"""
    if st.session_state.navigation_history:
        st.session_state.current_view = st.session_state.navigation_history.pop()
        st.rerun()

def display_login():
    """Display login/registration form"""
    st.markdown('<h1 class="main-header">AI Learning Companion</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subheader">Your personalized tutor for Math, Physics, and Chemistry</p>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Login")
        login_id = st.text_input("Student ID", key="login_id")
        if st.button("Login"):
            if student_manager.student_exists(login_id):
                st.session_state.student_id = login_id
                st.session_state.onboarding_complete = False
                st.rerun()
            else:
                st.error("Student ID not found. Please register first.")

    with col2:
        st.subheader("Register")
        reg_id = st.text_input("Choose Student ID", key="reg_id")
        name = st.text_input("Your Name")
        grade = st.selectbox("Grade Level", list(range(1, 13)))

        if st.button("Register"):
            if reg_id and name:
                if student_manager.create_student(reg_id, name, grade):
                    st.success("Registration successful! You can now login.")
                else:
                    st.error("Student ID already exists. Please choose another.")
            else:
                st.error("Please fill all fields.")


def display_main_menu():
    """Display the main menu after onboarding"""
    st.markdown("## Welcome to Your Learning Dashboard 🎓")
    
    # Display VARK profile if available
    student_data = student_manager.get_student_data(st.session_state.student_id)
    if "detailed_preferences" in student_data and "vark" in student_data["detailed_preferences"]:
        st.subheader("Your Learning Style Profile")
        col1, col2, col3, col4 = st.columns(4)
        vark = student_data["detailed_preferences"]["vark"]
        with col1:
            st.metric("Visual", f"{vark.get('visual', 0):.0f}%")
        with col2:
            st.metric("Auditory", f"{vark.get('auditory', 0):.0f}%")
        with col3:
            st.metric("Reading/Writing", f"{vark.get('reading_writing', 0):.0f}%")
        with col4:
            st.metric("Kinesthetic", f"{vark.get('kinesthetic', 0):.0f}%")
    
    # Main navigation options
    st.divider()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📚 Study Planner", use_container_width=True):
            navigate_to("study_planner")
            
    with col2:
        if st.button("🎯 Course Explorer", use_container_width=True):
            navigate_to("courses")
            
    with col3:
        if st.button("📊 Analytics Dashboard", use_container_width=True):
            navigate_to("analytics")

    # Quick access to recent activities and progress
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Recent Activities")
        if student_data["session_history"]:
            for session in student_data["session_history"][-5:]:
                st.info(f"{session['subject'].capitalize()}: {session['topic']} - Score: {session['score']}%")
        else:
            st.info("No activities yet. Start your learning journey!")
            
    with col2:
        st.subheader("Quick Stats")
        if "assessments" in student_data:
            latest_assessment = student_data["assessments"][-1]
            st.write("Latest Assessment Scores:")
            for subject, data in latest_assessment["results"].items():
                st.metric(subject.capitalize(), f"{data['score']:.1f}%")
        else:
            if st.button("Take Initial Assessment"):
                navigate_to("assessment")


def display_chat():
    """Display chat interface"""
    st.subheader(f"{st.session_state.subject.capitalize()} Tutor")

    # Topic selection
    topics = {
        "math": ["Algebra", "Geometry", "Calculus", "Statistics", "Trigonometry", "Number Theory"],
        "physics": ["Mechanics", "Thermodynamics", "Electricity", "Magnetism", "Optics", "Nuclear Physics"],
        "chemistry": ["Periodic Table", "Chemical Bonds", "Organic Chemistry", "Acids and Bases", "Thermochemistry", "Electrochemistry"]
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
        if os.path.exists(report["report_file"]):
            st.image(report["report_file"])


def display_study_planner():
    """Display study planner interface"""
    st.subheader("Study Planner")
    
    # Get current plan
    current_plan = student_manager.get_active_study_plan(st.session_state.student_id)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if not current_plan:
            st.info("Create a new study plan to get started!")
            with st.form("new_plan"):
                st.write("Set Your Study Goals")
                goals = st.text_area("What do you want to achieve?", 
                    placeholder="Example: Improve math grade, prepare for physics exam...")
                duration = st.slider("Plan Duration (days)", 1, 30, 7)
                hours = st.slider("Study Hours per Day", 1, 8, 4)
                
                if st.form_submit_button("Generate Plan"):
                    if goals:
                        student_data = student_manager.get_student_data(st.session_state.student_id)
                        plan = study_planner.generate_study_plan(
                            student_data=student_data,
                            goals=goals,
                            duration_days=duration,
                            hours_per_day=hours
                        )
                        if student_manager.save_study_plan(st.session_state.student_id, plan, goals):
                            st.success("Study plan created successfully!")
                            st.rerun()
        else:
            # Display current plan
            st.markdown("### Current Study Plan")
            st.markdown(f"**Goals:** {current_plan['goals']}")
            
            # Progress overview
            progress = student_manager.get_study_progress(st.session_state.student_id)
            if progress:
                st.progress(progress["completion_rate"] / 100)
                st.write(f"Progress: {progress['completion_rate']:.1f}% ({progress['completed_tasks']}/{progress['total_tasks']} tasks completed)")
            
            # Daily schedule
            for day, schedule in current_plan["daily_schedules"].items():
                with st.expander(f"📅 {day}"):
                    for session in schedule["sessions"]:
                        col1, col2, col3 = st.columns([3, 1, 1])
                        with col1:
                            st.write(f"📚 **{session['subject']}:** {session['topic']}")
                            st.write(f"_{session['method']}_")
                        with col2:
                            st.write(f"⏱️ {session['duration']}")
                        with col3:
                            if st.button("✅ Complete", key=f"task_{session['id']}"):
                                student_manager.mark_task_completed(st.session_state.student_id, session['id'])
                                st.rerun()
    
    with col2:
        st.markdown("### Study Tips")
        tips = [
            "Take regular breaks (5-10 minutes every hour)",
            "Stay hydrated and maintain good posture",
            "Use active recall techniques",
            "Explain concepts to others",
            "Review material before sleeping"
        ]
        for tip in tips:
            st.info(tip)
        
        if current_plan:
            st.markdown("### Plan Adjustment")
            feedback = st.text_area("Need to adjust your plan?", 
                placeholder="Example: I need more time for math, prefer studying in the morning...")
            if st.button("Adjust Plan"):
                if feedback:
                    adjusted_plan = study_planner.adjust_plan(current_plan, feedback)
                    if student_manager.save_study_plan(st.session_state.student_id, adjusted_plan, current_plan["goals"]):
                        st.success("Plan adjusted successfully!")
                        st.rerun()


def display_analytics():
    """Display the analytics dashboard"""
    st.markdown("## Performance Analytics Dashboard 📊")
    
    # Show back button
    if st.button("⬅️ Back to Main Menu"):
        navigate_to("main")
        return
    
    # Display analytics dashboard
    assessment_manager.display_analytics_dashboard(st.session_state.student_id)


def main():
    """Main application function"""
    if not st.session_state.student_id:
        display_login()
    else:
        # Check if initial assessment is complete
        if not st.session_state.assessment_complete:
            if assessment_manager.conduct_initial_assessment(st.session_state.student_id):
                st.session_state.assessment_complete = True
                st.rerun()
        # Check if onboarding is complete
        elif not st.session_state.onboarding_complete:
            if onboarding_manager.collect_preferences(st.session_state.student_id):
                st.session_state.onboarding_complete = True
                st.rerun()
        else:
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

                # Quick navigation
                st.subheader("Quick Navigation")
                if st.button("🏠 Home"):
                    navigate_to("main")
                if st.button("📊 Analytics"):
                    navigate_to("analytics")
                if st.button("⚙️ Update Preferences"):
                    st.session_state.onboarding_complete = False
                    st.rerun()
                if st.button("📝 Study Notes"):
                    navigate_to("notes")
                
                st.divider()

                # Logout button
                if st.button("Logout"):
                    for key in st.session_state.keys():
                        del st.session_state[key]
                    st.rerun()

            # Main content based on current view
            if st.session_state.current_view == "main":
                display_main_menu()
            elif st.session_state.current_view == "study_planner":
                display_study_planner()
            elif st.session_state.current_view == "courses":
                onboarding_manager.show_course_options(st.session_state.student_id)
            elif st.session_state.current_view == "analytics":
                display_analytics()
            elif st.session_state.current_view == "assessment":
                if assessment_manager.conduct_initial_assessment(st.session_state.student_id):
                    navigate_to("main")
            elif st.session_state.current_view == "notes":
                st.markdown("## 📝 Study Notes")
                st.info("This feature is coming soon!")


if __name__ == "__main__":
    main()
