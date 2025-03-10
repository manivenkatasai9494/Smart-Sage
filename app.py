import os

import streamlit as st
import streamlit.components.v1 as components
from PIL import Image

from ai_service import AITutorService
from config import ALLOWED_SUBJECTS, APP_NAME
from student_manager import StudentManager


# Initialize services
@st.cache_resource
def init_services():
    return AITutorService(), StudentManager()


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

# Session state initialization
if "student_id" not in st.session_state:
    st.session_state.student_id = None
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
if "study_plan" not in st.session_state:
    st.session_state.study_plan = None


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
    st.subheader("Learning Roadmap")
    
    # Get current plan
    current_plan = student_manager.get_active_study_plan(st.session_state.student_id)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if not current_plan:
            st.info("Create your personalized learning roadmap!")
            with st.form("new_plan"):
                # Quick Setup Section
                st.write("### Quick Setup")
                st.markdown("""
                <div style='background-color: #e6f3ff; padding: 15px; border-radius: 8px; margin-bottom: 15px;'>
                    <p>Let's create your personalized learning journey!</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Subject and topic selection
                st.write("### What Do You Want to Learn?")
                subject = st.selectbox(
                    "Select Subject",
                    ALLOWED_SUBJECTS,
                    format_func=lambda x: x.capitalize()
                )
                
                topics = st.multiselect(
                    "Select Topics to Cover",
                    topics[subject],
                    help="Choose the topics you want to learn"
                )
                
                # Learning Style Assessment
                st.write("### Learning Style Assessment")
                learning_style = st.radio(
                    "How do you prefer to learn?",
                    ["Visual (Charts, Diagrams)", "Auditory (Listening, Speaking)", 
                     "Reading/Writing", "Kinesthetic (Hands-on, Practice)"]
                )
                
                # Goals and preferences
                st.write("### Your Goals")
                goals = st.text_area(
                    "What do you want to achieve?",
                    placeholder="Example: Master calculus fundamentals, Understand quantum mechanics...",
                    help="Be specific about your goals for better plan customization"
                )
                
                # Study preferences
                st.write("### Learning Schedule")
                col1, col2 = st.columns(2)
                with col1:
                    duration = st.slider("Plan Duration (days)", 1, 90, 30)
                with col2:
                    hours = st.slider("Study Hours per Day", 1, 8, 2)
                
                # Preferred study times
                st.write("### Preferred Study Times")
                morning = st.checkbox("Morning (6 AM - 12 PM)", value=True)
                afternoon = st.checkbox("Afternoon (12 PM - 6 PM)", value=True)
                evening = st.checkbox("Evening (6 PM - 12 AM)", value=True)
                
                # Study methods
                st.write("### Learning Methods")
                methods = {
                    "Reading": st.checkbox("Reading", value=True),
                    "Practice Exercises": st.checkbox("Practice Exercises", value=True),
                    "Video Tutorials": st.checkbox("Video Tutorials", value=True),
                    "Group Learning": st.checkbox("Group Learning", value=False),
                    "Flashcards": st.checkbox("Flashcards", value=True),
                    "Mind Mapping": st.checkbox("Mind Mapping", value=True),
                    "Project Work": st.checkbox("Project Work", value=True)
                }
                
                # Additional preferences
                st.write("### Learning Preferences")
                focus_duration = st.slider("Preferred Focus Duration (minutes)", 25, 120, 45, step=5)
                break_duration = st.slider("Preferred Break Duration (minutes)", 5, 30, 10, step=5)

                if st.form_submit_button("Generate Learning Roadmap"):
                    if subject and topics and goals:
                        with st.spinner("Creating your personalized learning roadmap..."):
                            # Create plan structure
                            plan = {
                                "daily_schedules": {},
                                "subject": subject,
                                "topics": topics,
                                "learning_style": learning_style,
                                "duration_days": duration,
                                "hours_per_day": hours,
                                "study_times": {
                                    "morning": morning,
                                    "afternoon": afternoon,
                                    "evening": evening
                                },
                                "study_methods": [method for method, selected in methods.items() if selected],
                                "focus_duration": focus_duration,
                                "break_duration": break_duration
                            }
                            
                            # Generate daily schedules
                            for day in range(1, duration + 1):
                                day_key = f"Day {day}"
                                plan["daily_schedules"][day_key] = {
                                    "sessions": []
                                }
                                
                                # Add study sessions based on hours per day
                                sessions_per_day = hours * 2  # Assuming 30-minute sessions
                                for session in range(sessions_per_day):
                                    session_id = f"{day_key}_session_{session + 1}"
                                    topic = topics[session % len(topics)]
                                    method = plan["study_methods"][session % len(plan["study_methods"])]
                                    
                                    # Get AI-generated description for the session
                                    prompt = f"Generate a brief, specific study task for {topic} using {method} method."
                                    description = ai_tutor.model.generate_content(prompt).text.strip()
                                    
                                    plan["daily_schedules"][day_key]["sessions"].append({
                                        "id": session_id,
                                        "topic": topic,
                                        "method": method,
                                        "duration": f"{focus_duration} minutes",
                                        "description": description
                                    })
                            
                            if student_manager.save_study_plan(st.session_state.student_id, plan, goals):
                                st.success("Your personalized learning roadmap has been created!")
                                st.balloons()
                                st.rerun()
                    else:
                        st.error("Please fill in all required fields.")
        else:
            # Display current plan
            st.write("### Your Learning Roadmap")
            st.markdown(f"""
            <div style='background-color: #e6f3ff; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
                <h4>🎯 Learning Goals</h4>
                <p>{current_plan['goals']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Progress overview
            progress = student_manager.get_study_progress(st.session_state.student_id)
            if progress:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.progress(progress["completion_rate"] / 100)
                with col2:
                    st.metric(
                        "Completion Rate",
                        f"{progress['completion_rate']:.1f}%",
                        f"{progress['completed_tasks']}/{progress['total_tasks']} tasks"
                    )
            
            # Daily schedule
            for day, schedule in current_plan["daily_schedules"].items():
                with st.expander(f"📅 {day}", expanded=True):
                    for session in schedule["sessions"]:
                        col1, col2, col3 = st.columns([3, 1, 1])
                        with col1:
                            st.markdown(f"""
                            <div style='background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 10px;'>
                                <h4>📚 {session['topic']}</h4>
                                <p><strong>Method:</strong> {session['method']}</p>
                                <p><em>{session.get('description', f"Study {session['topic']} using {session['method']}")}</em></p>
                            </div>
                            """, unsafe_allow_html=True)
                        with col2:
                            st.write(f"⏱️ {session['duration']}")
                        with col3:
                            if st.button("✅ Complete", key=f"task_{session['id']}"):
                                student_manager.mark_task_completed(st.session_state.student_id, session['id'])
                                st.rerun()
    
    with col2:
        # Learning Tips
        st.write("### AI-Recommended Learning Tips")
        tips = [
            "Take regular breaks (5-10 minutes every hour)",
            "Stay hydrated and maintain good posture",
            "Use active recall techniques",
            "Explain concepts to others",
            "Review material before sleeping",
            "Use the Pomodoro Technique",
            "Create mind maps for complex topics",
            "Work on real projects",
            "Join learning communities",
            "Use spaced repetition"
        ]
        for tip in tips:
            st.info(tip)
        
        if current_plan:
            st.write("### Plan Adjustment")
            st.markdown("""
            <div style='background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 15px;'>
                <p>Need to adjust your learning roadmap? Our AI will help optimize it based on your feedback.</p>
            </div>
            """, unsafe_allow_html=True)
            
            feedback = st.text_area(
                "What would you like to adjust?",
                placeholder="Example: I need more time for certain topics...",
                help="Be specific about what you'd like to change"
            )
            if st.button("Optimize Plan"):
                if feedback:
                    with st.spinner("Optimizing your learning roadmap..."):
                        # Create adjusted plan based on feedback
                        adjusted_plan = current_plan.copy()
                        # Here you could add AI-based plan adjustment logic
                        if student_manager.save_study_plan(st.session_state.student_id, adjusted_plan, current_plan["goals"]):
                            st.success("Your learning roadmap has been optimized!")
                            st.rerun()


def main():
    """Main application function"""
    if not st.session_state.student_id:
        display_login()
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

            # Subject selection
            st.subheader("Select Subject")
            subject = st.radio(
                "",
                ALLOWED_SUBJECTS,
                format_func=lambda x: x.capitalize(),
                index=ALLOWED_SUBJECTS.index(st.session_state.subject)
            )

            if subject != st.session_state.subject:
                st.session_state.subject = subject
                st.session_state.chat_history = []
                st.rerun()

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
                st.rerun()

        # Main content
        tab1, tab2, tab3, tab4 = st.tabs(["Tutor Chat", "Practice Questions", "Learning Roadmap", "My Progress"])

        with tab1:
            display_chat()

        with tab2:
            display_practice()

        with tab3:
            display_study_planner()

        with tab4:
            display_progress()


if __name__ == "__main__":
    main()
