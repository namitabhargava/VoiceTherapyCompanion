import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from services.auth_service import AuthService
from services.zoom_service import ZoomService
from services.google_meet_service import GoogleMeetService
from services.teams_service import TeamsService
from services.transcription_service import TranscriptionService
from services.analysis_service import AnalysisService
from services.vapi_service import VAPIService
from services.pdf_service import PDFService
from services.session_manager import SessionManager
from models.session_data import SessionData
from utils.security import SecurityUtils
from config.settings import Settings

# Initialize services
@st.cache_resource
def init_services():
    auth_service = AuthService()
    zoom_service = ZoomService()
    google_meet_service = GoogleMeetService()
    teams_service = TeamsService()
    transcription_service = TranscriptionService()
    analysis_service = AnalysisService()
    vapi_service = VAPIService()
    pdf_service = PDFService()
    session_manager = SessionManager()
    
    return {
        'auth': auth_service,
        'zoom': zoom_service,
        'google_meet': google_meet_service,
        'teams': teams_service,
        'transcription': transcription_service,
        'analysis': analysis_service,
        'vapi': vapi_service,
        'pdf': pdf_service,
        'session_manager': session_manager
    }

def main():
    st.set_page_config(
        page_title="Therapeutic Assessment AI",
        page_icon="🎤",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    services = init_services()
    
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'current_session' not in st.session_state:
        st.session_state.current_session = None
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    
    # Header
    st.title("🎤 Therapeutic Assessment AI")
    st.markdown("*Voice-enabled therapeutic session analysis with multi-platform integration*")
    
    # Sidebar
    with st.sidebar:
        st.header("Navigation")
        
        # API Status Check
        st.subheader("Service Status")
        openai_key = os.getenv("OPENAI_API_KEY")
        hf_key = os.getenv("HUGGINGFACE_API_KEY")
        
        if openai_key:
            st.success("✅ OpenAI API (Premium)")
        elif hf_key:
            st.info("🆓 Hugging Face (Free)")
        else:
            st.warning("🔧 Local Analysis Only")
            
        st.caption("Local analysis uses basic keyword matching. For detailed insights, add API keys in settings.")
        
        # Platform Authentication
        st.subheader("Platform Authentication")
        platform = st.selectbox(
            "Select Platform",
            ["Zoom", "Google Meet", "Microsoft Teams"],
            key="platform_selector"
        )
        
        if st.button("Authenticate"):
            with st.spinner("Authenticating..."):
                auth_result = authenticate_platform(services, platform)
                if auth_result:
                    st.success(f"Successfully authenticated with {platform}")
                    st.session_state.authenticated = True
                else:
                    st.error(f"Authentication failed for {platform}")
        
        # Session Management
        if st.session_state.authenticated:
            st.subheader("Session Management")
            
            # Auto-detect sessions
            if st.button("Detect New Sessions"):
                with st.spinner("Detecting sessions..."):
                    sessions = detect_sessions(services, platform)
                    if sessions:
                        st.success(f"Found {len(sessions)} new sessions")
                        st.session_state.detected_sessions = sessions
                    else:
                        st.info("No new sessions found")
            
            # Manual upload
            st.subheader("Manual Upload")
            uploaded_file = st.file_uploader(
                "Upload audio file",
                type=['mp3', 'wav', 'mp4', 'm4a'],
                help="Upload a therapy session recording"
            )
            
            if uploaded_file and st.button("Process Uploaded File"):
                process_uploaded_file(services, uploaded_file)
        
        # Demo Section
        if not openai_key and not hf_key:
            st.subheader("🎯 Try Demo")
            st.caption("Test the local analysis with sample text")
            if st.button("Run Demo Analysis"):
                show_demo_analysis(services)
    
    # Main content
    if not st.session_state.authenticated:
        show_welcome_screen()
    else:
        show_main_interface(services)

def authenticate_platform(services, platform):
    """Authenticate with the selected platform"""
    try:
        if platform == "Zoom":
            return services['auth'].authenticate_zoom()
        elif platform == "Google Meet":
            return services['auth'].authenticate_google()
        elif platform == "Microsoft Teams":
            return services['auth'].authenticate_teams()
        return False
    except Exception as e:
        st.error(f"Authentication error: {str(e)}")
        return False

def detect_sessions(services, platform):
    """Detect new sessions from the platform"""
    try:
        if platform == "Zoom":
            return services['zoom'].get_recent_recordings()
        elif platform == "Google Meet":
            return services['google_meet'].get_recent_recordings()
        elif platform == "Microsoft Teams":
            return services['teams'].get_recent_recordings()
        return []
    except Exception as e:
        st.error(f"Session detection error: {str(e)}")
        return []

def process_uploaded_file(services, uploaded_file):
    """Process manually uploaded audio file"""
    try:
        with st.spinner("Processing audio file..."):
            # Save uploaded file
            file_path = services['session_manager'].save_uploaded_file(uploaded_file)
            
            # Transcribe
            st.info("Transcribing audio...")
            transcript = services['transcription'].transcribe_audio(file_path)
            
            # Analyze
            st.info("Analyzing session content...")
            analysis_results = services['analysis'].analyze_session(transcript)
            
            # Store results
            session_data = SessionData(
                file_path=file_path,
                transcript=transcript,
                analysis=analysis_results,
                timestamp=datetime.now()
            )
            
            services['session_manager'].save_session(session_data)
            st.session_state.current_session = session_data
            st.session_state.analysis_results = analysis_results
            
            st.success("Session processed successfully!")
            st.rerun()
            
    except Exception as e:
        st.error(f"Processing error: {str(e)}")

def show_welcome_screen():
    """Show welcome screen for unauthenticated users"""
    st.markdown("""
    ## Welcome to Therapeutic Assessment AI
    
    This application provides AI-powered analysis of therapy sessions using multiple psychological frameworks:
    
    ### Supported Platforms
    - **Zoom** - Automatic cloud recording retrieval
    - **Google Meet** - Integration via Google Drive API
    - **Microsoft Teams** - Recording access via Graph API
    
    ### Analysis Frameworks
    1. **Emotional Safety & Relational Depth** (Carl Rogers)
    2. **Unconscious Pattern Emergence** (Freud, Klein)
    3. **Cognitive Restructuring** (Ellis, Beck)
    4. **Communication/Family Role Changes** (Satir)
    5. **Strengths and Well-being** (Seligman)
    6. **Narrative/Identity Coherence**
    7. **Behavioral Activation in Real Life**
    
    ### Features
    - 🎤 Voice-based querying via VAPI
    - 📊 Progress tracking over time
    - 📄 Professional PDF reports
    - 🔒 HIPAA-compliant data handling
    
    **Get started by authenticating with your platform in the sidebar.**
    """)

def show_main_interface(services):
    """Show main interface for authenticated users"""
    
    # Tab navigation
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Dashboard", 
        "🎤 Voice Query", 
        "📈 Progress Tracking", 
        "📄 Reports", 
        "⚙️ Settings"
    ])
    
    with tab1:
        show_dashboard(services)
    
    with tab2:
        show_voice_interface(services)
    
    with tab3:
        show_progress_tracking(services)
    
    with tab4:
        show_reports(services)
    
    with tab5:
        show_settings(services)

def show_dashboard(services):
    """Show main dashboard"""
    st.header("Session Dashboard")
    
    # Recent sessions
    sessions = services['session_manager'].get_recent_sessions()
    
    if not sessions:
        st.info("No sessions processed yet. Upload an audio file or detect sessions from your platform.")
        return
    
    # Session selection
    session_options = {
        f"Session {i+1} - {session.timestamp.strftime('%Y-%m-%d %H:%M')}": session
        for i, session in enumerate(sessions)
    }
    
    selected_session_key = st.selectbox("Select Session", list(session_options.keys()))
    selected_session = session_options[selected_session_key]
    
    if selected_session:
        st.session_state.current_session = selected_session
        
        # Display analysis results
        if selected_session.analysis:
            display_analysis_results(selected_session.analysis)
        
        # Display transcript
        with st.expander("View Transcript"):
            st.text_area("Session Transcript", selected_session.transcript, height=200)

def display_analysis_results(analysis):
    """Display analysis results in a structured format"""
    st.subheader("Therapeutic Analysis Results")
    
    # Domain scores
    scores = analysis.get('domain_scores', {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Emotional Safety", f"{scores.get('emotional_safety', 0)}/10")
        st.metric("Unconscious Patterns", f"{scores.get('unconscious_patterns', 0)}/10")
        st.metric("Cognitive Restructuring", f"{scores.get('cognitive_restructuring', 0)}/10")
        st.metric("Communication Changes", f"{scores.get('communication_changes', 0)}/10")
    
    with col2:
        st.metric("Strengths & Well-being", f"{scores.get('strengths_wellbeing', 0)}/10")
        st.metric("Narrative Coherence", f"{scores.get('narrative_coherence', 0)}/10")
        st.metric("Behavioral Activation", f"{scores.get('behavioral_activation', 0)}/10")
    
    # Radar chart
    categories = list(scores.keys())
    values = list(scores.values())
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Current Session'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )),
        showlegend=True,
        title="Therapeutic Domain Scores"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Key insights
    insights = analysis.get('key_insights', [])
    if insights:
        st.subheader("Key Insights")
        for insight in insights:
            st.write(f"• {insight}")
    
    # Recommendations
    recommendations = analysis.get('recommendations', [])
    if recommendations:
        st.subheader("Recommendations")
        for rec in recommendations:
            st.write(f"• {rec}")

def show_voice_interface(services):
    """Show voice interaction interface"""
    st.header("🎤 Voice Query Interface")
    
    if not st.session_state.current_session:
        st.warning("Please select a session from the dashboard first.")
        return
    
    # VAPI integration
    st.subheader("Ask About Your Session")
    
    # Voice input button
    if st.button("🎤 Start Voice Query", type="primary"):
        with st.spinner("Listening..."):
            try:
                # Initialize VAPI session
                vapi_response = services['vapi'].start_voice_session(
                    st.session_state.current_session
                )
                
                if vapi_response:
                    st.success("Voice session started successfully!")
                    st.info("You can now ask questions like:")
                    st.write("• 'Am I making progress in therapy?'")
                    st.write("• 'What themes came up in today's session?'")
                    st.write("• 'How is my emotional safety improving?'")
                else:
                    st.error("Failed to start voice session")
                    
            except Exception as e:
                st.error(f"Voice interface error: {str(e)}")
    
    # Text-based queries as fallback
    st.subheader("Text-based Queries")
    
    query = st.text_input("Ask a question about your session:")
    
    if query and st.button("Submit Query"):
        with st.spinner("Processing query..."):
            try:
                response = services['analysis'].answer_query(
                    query, 
                    st.session_state.current_session
                )
                
                st.subheader("Response")
                st.write(response)
                
            except Exception as e:
                st.error(f"Query processing error: {str(e)}")

def show_progress_tracking(services):
    """Show progress tracking over time"""
    st.header("📈 Progress Tracking")
    
    sessions = services['session_manager'].get_all_sessions()
    
    if len(sessions) < 2:
        st.info("At least 2 sessions are needed for progress tracking.")
        return
    
    # Prepare data for visualization
    session_data = []
    for i, session in enumerate(sessions):
        scores = session.analysis.get('domain_scores', {})
        session_data.append({
            'session': i + 1,
            'date': session.timestamp.strftime('%Y-%m-%d'),
            **scores
        })
    
    df = pd.DataFrame(session_data)
    
    # Progress charts
    domain_options = [
        'emotional_safety',
        'unconscious_patterns', 
        'cognitive_restructuring',
        'communication_changes',
        'strengths_wellbeing',
        'narrative_coherence',
        'behavioral_activation'
    ]
    
    selected_domains = st.multiselect(
        "Select domains to track:",
        domain_options,
        default=domain_options[:3]
    )
    
    if selected_domains:
        fig = px.line(
            df, 
            x='session', 
            y=selected_domains,
            title="Progress Over Time",
            labels={'session': 'Session Number', 'value': 'Score (0-10)'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Progress summary
    st.subheader("Progress Summary")
    
    if len(sessions) >= 2:
        first_session = sessions[0].analysis.get('domain_scores', {})
        last_session = sessions[-1].analysis.get('domain_scores', {})
        
        for domain in domain_options:
            if domain in first_session and domain in last_session:
                change = last_session[domain] - first_session[domain]
                direction = "↗️" if change > 0 else "↘️" if change < 0 else "➡️"
                st.write(f"{domain.replace('_', ' ').title()}: {direction} {change:+.1f}")

def show_reports(services):
    """Show report generation interface"""
    st.header("📄 Report Generation")
    
    if not st.session_state.current_session:
        st.warning("Please select a session from the dashboard first.")
        return
    
    # Report options
    st.subheader("Generate Reports")
    
    report_type = st.selectbox(
        "Report Type",
        ["Single Session Report", "Progress Report", "Comprehensive Analysis"]
    )
    
    include_transcript = st.checkbox("Include full transcript")
    include_recommendations = st.checkbox("Include recommendations", value=True)
    include_visualizations = st.checkbox("Include charts and graphs", value=True)
    
    if st.button("Generate PDF Report", type="primary"):
        with st.spinner("Generating report..."):
            try:
                # Generate PDF
                pdf_path = services['pdf'].generate_report(
                    st.session_state.current_session,
                    report_type=report_type,
                    include_transcript=include_transcript,
                    include_recommendations=include_recommendations,
                    include_visualizations=include_visualizations
                )
                
                # Offer download
                with open(pdf_path, 'rb') as pdf_file:
                    st.download_button(
                        label="Download PDF Report",
                        data=pdf_file.read(),
                        file_name=f"therapy_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                        mime="application/pdf"
                    )
                
                st.success("Report generated successfully!")
                
            except Exception as e:
                st.error(f"Report generation error: {str(e)}")

def show_demo_analysis(services):
    """Show demo analysis with sample therapeutic content"""
    st.header("🎯 Demo: Local Analysis")
    
    # Sample therapeutic session transcript
    demo_transcript = """
    Therapist: How are you feeling today?
    
    Client: I've been feeling better lately. I had a difficult week at work, but I'm starting to understand how to handle stress better. I've been practicing the breathing exercises we talked about.
    
    Therapist: That's great progress. What specifically helped you feel better?
    
    Client: I think recognizing my patterns helped. When I feel overwhelmed, I now take a step back instead of getting anxious. I also talked to my supervisor about my workload, which was scary but went well.
    
    Therapist: You mentioned feeling scared. Can you tell me more about that?
    
    Client: I was worried they'd think I wasn't capable. But actually, they were understanding and we worked out a better schedule. I feel more confident now.
    
    Therapist: It sounds like you're developing good self-awareness and communication skills. How do you feel about the progress you've made?
    
    Client: I'm proud of myself. A few months ago, I would have just suffered in silence. Now I'm learning to speak up and take care of myself better.
    """
    
    st.subheader("Sample Session Transcript")
    st.text_area("Demo Transcript", demo_transcript, height=200, disabled=True)
    
    if st.button("Analyze This Session"):
        with st.spinner("Running local analysis..."):
            # Simulate analysis
            analysis_results = services['analysis'].analyze_session(demo_transcript)
            
            if analysis_results:
                st.success("Analysis complete!")
                display_analysis_results(analysis_results)
            else:
                st.error("Analysis failed. Please check the logs.")

def show_settings(services):
    """Show settings and configuration"""
    st.header("⚙️ Settings")
    
    # API Configuration
    st.subheader("API Configuration")
    
    with st.expander("Add API Keys (Optional)"):
        st.markdown("""
        **Free Options Available:**
        - **Local Analysis**: Basic keyword-based analysis (no API key needed)
        - **Google Speech Recognition**: Free transcription service (no API key needed)
        - **Hugging Face**: Free tier available with API key
        
        **Premium Options:**
        - **OpenAI**: Advanced AI analysis and transcription
        - **AssemblyAI**: Professional transcription service
        """)
        
        # Show current status
        openai_key = os.getenv("OPENAI_API_KEY")
        hf_key = os.getenv("HUGGINGFACE_API_KEY")
        vapi_key = os.getenv("VAPI_API_KEY")
        
        if openai_key:
            st.success("✅ OpenAI API Key configured")
        else:
            st.info("To add OpenAI API key, set it in your environment variables")
            
        if hf_key:
            st.success("✅ Hugging Face API Key configured")
        else:
            st.info("To add Hugging Face API key, set it in your environment variables")
            
        if vapi_key:
            st.success("✅ VAPI API Key configured")
        else:
            st.info("To add VAPI API key, set it in your environment variables")
    
    # Analysis Settings
    st.subheader("Analysis Settings")
    
    analysis_depth = st.selectbox(
        "Analysis Depth",
        ["Standard", "Detailed", "Comprehensive"],
        index=1
    )
    
    # Privacy Settings
    st.subheader("Privacy & Security")
    
    auto_delete = st.checkbox("Auto-delete audio files after processing")
    local_only = st.checkbox("Local-only processing mode")
    
    # Save settings
    if st.button("Save Settings"):
        settings = {
            'analysis_depth': analysis_depth,
            'auto_delete': auto_delete,
            'local_only': local_only
        }
        
        # Save to configuration
        services['session_manager'].save_settings(settings)
        st.success("Settings saved successfully!")

if __name__ == "__main__":
    main()
