import streamlit as st
import streamlit.components.v1 as components
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def render_analytics_dashboard(student_data):
    """Render the analytics dashboard with charts and metrics"""
    st.markdown("""
    <style>
        .analytics-container {
            display: grid;
            gap: 2rem;
        }
        .analytics-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
        }
        .analytics-title {
            font-size: 1.5rem;
            font-weight: 600;
            color: #111827;
        }
        .analytics-card {
            background: white;
            border-radius: 0.5rem;
            padding: 1.5rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        .metric-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        .metric-card {
            background: #F3F4F6;
            padding: 1.5rem;
            border-radius: 0.5rem;
            text-align: center;
        }
        .metric-value {
            font-size: 2rem;
            font-weight: bold;
            color: #1E88E5;
            margin-bottom: 0.5rem;
        }
        .metric-label {
            color: #6B7280;
            font-size: 0.875rem;
        }
        .chart-container {
            height: 300px;
            margin: 1rem 0;
        }
    </style>
    """, unsafe_allow_html=True)

    # Overall Progress Metrics
    st.markdown("""
    <div class="analytics-container">
        <div class="analytics-header">
            <h2 class="analytics-title">Learning Progress</h2>
            <select class="form-input" style="width: 150px;">
                <option>Last 7 days</option>
                <option>Last 30 days</option>
                <option>All time</option>
            </select>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Calculate metrics
    total_sessions = len(student_data.get("session_history", []))
    total_questions = sum(session.get("questions_asked", 0) for session in student_data.get("session_history", []))
    avg_score = np.mean([session.get("score", 0) for session in student_data.get("session_history", [])]) if total_sessions > 0 else 0

    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_sessions}</div>
            <div class="metric-label">Total Sessions</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_questions}</div>
            <div class="metric-label">Questions Asked</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{avg_score:.1f}%</div>
            <div class="metric-label">Average Score</div>
        </div>
        """, unsafe_allow_html=True)

    # Subject Performance Chart
    st.markdown("""
    <div class="analytics-card">
        <h3 class="analytics-title">Subject Performance</h3>
        <div class="chart-container">
    """, unsafe_allow_html=True)

    # Create subject performance data
    subjects = ["math", "physics", "chemistry"]
    scores = [student_data["subjects"][subject]["overall_score"] for subject in subjects]
    
    fig = go.Figure(data=[
        go.Bar(
            x=subjects,
            y=scores,
            marker_color='#1E88E5',
            text=[f"{score:.1f}%" for score in scores],
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title="Overall Performance by Subject",
        xaxis_title="Subject",
        yaxis_title="Score (%)",
        yaxis=dict(range=[0, 100]),
        showlegend=False,
        height=300
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div></div>", unsafe_allow_html=True)

    # Learning Progress Over Time
    st.markdown("""
    <div class="analytics-card">
        <h3 class="analytics-title">Learning Progress Over Time</h3>
        <div class="chart-container">
    """, unsafe_allow_html=True)

    # Create time series data
    if total_sessions > 0:
        dates = [session["date"] for session in student_data["session_history"]]
        scores = [session["score"] for session in student_data["session_history"]]
        
        df = pd.DataFrame({
            'Date': pd.to_datetime(dates),
            'Score': scores
        })
        
        fig = px.line(df, x='Date', y='Score',
                     title='Score Trend Over Time',
                     labels={'Score': 'Score (%)', 'Date': 'Date'})
        
        fig.update_layout(
            height=300,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No session data available yet.")
    
    st.markdown("</div></div>", unsafe_allow_html=True)

    # Topic Performance
    st.markdown("""
    <div class="analytics-card">
        <h3 class="analytics-title">Topic Performance</h3>
        <div class="chart-container">
    """, unsafe_allow_html=True)

    # Create topic performance data
    topics_data = []
    for subject in subjects:
        for topic, data in student_data["subjects"][subject]["topics"].items():
            topics_data.append({
                'Topic': topic,
                'Subject': subject,
                'Score': data.get('average_score', 0)
            })
    
    if topics_data:
        df = pd.DataFrame(topics_data)
        fig = px.bar(df, x='Topic', y='Score', color='Subject',
                    title='Performance by Topic',
                    labels={'Score': 'Score (%)', 'Topic': 'Topic'})
        
        fig.update_layout(
            height=300,
            xaxis_tickangle=-45
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No topic data available yet.")
    
    st.markdown("</div></div>", unsafe_allow_html=True)

def render_achievement_badges(student_data):
    """Render the achievement badges section"""
    st.markdown("""
    <style>
        .badges-container {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }
        .badge-card {
            background: white;
            border-radius: 0.5rem;
            padding: 1rem;
            text-align: center;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        .badge-icon {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }
        .badge-name {
            font-weight: 500;
            color: #111827;
            margin-bottom: 0.25rem;
        }
        .badge-description {
            font-size: 0.875rem;
            color: #6B7280;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="analytics-card">
        <h3 class="analytics-title">Achievement Badges</h3>
        <div class="badges-container">
    """, unsafe_allow_html=True)

    badges = student_data.get("badges", [])
    if badges:
        for badge in badges:
            st.markdown(f"""
            <div class="badge-card">
                <div class="badge-icon">🏆</div>
                <div class="badge-name">{badge}</div>
                <div class="badge-description">Achievement unlocked!</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No badges earned yet. Keep learning to earn achievements!")
    
    st.markdown("</div></div>", unsafe_allow_html=True) 