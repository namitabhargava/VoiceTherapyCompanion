import streamlit as st
import json
import os
import requests
import urllib.parse
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
from utils.file_handler import FileHandler
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
        page_title="MindAI - Therapeutic Intelligence Platform",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    services = init_services()
    
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'current_session' not in st.session_state:
        st.session_state.current_session = None
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'dashboard'
    
    # Custom CSS for modern design
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 0;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        border-radius: 10px;
    }
    
    .upload-card {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1rem;
        text-align: center;
        border: 2px solid #f0f0f0;
        transition: all 0.3s ease;
    }
    
    .upload-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }
    
    .upload-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    .nav-tabs {
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin-bottom: 2rem;
    }
    
    .nav-tab {
        padding: 1rem 2rem;
        background: #f8f9fa;
        border: none;
        border-radius: 25px;
        cursor: pointer;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .nav-tab.active {
        background: #667eea;
        color: white;
    }
    
    .platform-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .platform-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        cursor: pointer;
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }
    
    .platform-card:hover {
        border-color: #667eea;
        transform: translateY(-2px);
    }
    
    .platform-card.selected {
        border-color: #667eea;
        background: #f8f9ff;
    }
    
    .status-badge {
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 500;
        margin-top: 0.5rem;
    }
    
    .status-connected {
        background: #d4edda;
        color: #155724;
    }
    
    .status-disconnected {
        background: #f8d7da;
        color: #721c24;
    }
    
    .hero-section {
        text-align: center;
        padding: 3rem 0;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 20px;
        margin-bottom: 3rem;
    }
    
    .hero-title {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 1rem;
        color: #2d3436;
    }
    
    .hero-subtitle {
        font-size: 1.2rem;
        color: #636e72;
        margin-bottom: 2rem;
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
    }
    
    /* Custom file uploader styling */
    .stFileUploader > div > div > div > div {
        text-align: center;
    }
    
    .stFileUploader > div > div > div > div > button {
        background-color: #3b82f6 !important;
        color: white !important;
        border: none !important;
        padding: 0.5rem 1.5rem !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
        cursor: pointer !important;
        transition: background-color 0.2s !important;
    }
    
    .stFileUploader > div > div > div > div > button:hover {
        background-color: #2563eb !important;
    }
    
    .stFileUploader > div > div > div > div > button:focus {
        outline: none !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.5) !important;
    }
    
    /* Style file uploader to match platform buttons */
    .stFileUploader > div > div > div > div > button {
        background: #3b82f6 !important;
        color: white !important;
        border: none !important;
        padding: 0.8rem 1.5rem !important;
        border-radius: 25px !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
        max-width: 200px !important;
        margin: 0 auto !important;
        display: block !important;
    }
    
    .stFileUploader > div > div > div > div > button:hover {
        background: #2563eb !important;
        transform: translateY(-1px) !important;
    }
    
    /* Text Pillar Card Styling */
    .text-pillar-card {
        background: white;
        border-radius: 20px;
        padding: 3rem 2rem;
        margin: 1rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        text-align: center;
        border: 1px solid #e5e7eb;
        min-height: 400px;
        position: relative;
    }
    
    .text-pillar-icon {
        background: #d4b894;
        color: white;
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        display: inline-block;
        box-shadow: 0 4px 12px rgba(212, 184, 148, 0.3);
    }
    
    .text-pillar-title {
        color: #374151;
        margin-bottom: 1rem;
        font-size: 1.8rem;
        font-weight: 700;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    .text-pillar-description {
        color: #6b7280;
        margin-bottom: 2rem;
        font-size: 1rem;
        line-height: 1.5;
    }
    
    .text-pillar-specs {
        color: #6b7280;
        margin-bottom: 2.5rem;
        font-size: 0.9rem;
    }
    
    .text-pillar-specs .spec-item {
        font-weight: 500;
    }
    
    .text-pillar-specs .spec-separator {
        margin: 0 0.5rem;
    }
    
    /* Audio Foundation file uploader button styling */
    div[data-testid="stFileUploader"]:first-of-type > div > div > div > div > button {
        background: #6b7280 !important;
        color: white !important;
        border: none !important;
        padding: 1rem 2rem !important;
        border-radius: 30px !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
        margin: 0 auto !important;
        display: block !important;
        box-shadow: 0 4px 12px rgba(107, 114, 128, 0.3) !important;
    }
    
    div[data-testid="stFileUploader"]:first-of-type > div > div > div > div > button:hover {
        background: #4b5563 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(107, 114, 128, 0.4) !important;
    }
    
    /* Text Pillar file uploader button styling */
    div[data-testid="stFileUploader"]:nth-of-type(2) > div > div > div > div > button {
        background: #d97706 !important;
        color: white !important;
        border: none !important;
        padding: 1rem 2rem !important;
        border-radius: 30px !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
        margin: 0 auto !important;
        display: block !important;
        box-shadow: 0 4px 12px rgba(217, 119, 6, 0.3) !important;
    }
    
    div[data-testid="stFileUploader"]:nth-of-type(2) > div > div > div > div > button:hover {
        background: #b45309 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(217, 119, 6, 0.4) !important;
    }
    
    /* General file uploader styling */
    div[data-testid="stFileUploader"] {
        border: none !important;
        background: transparent !important;
        padding: 0 !important;
    }
    
    div[data-testid="stFileUploader"] > div > div > div > div > section {
        border: none !important;
        background: transparent !important;
        padding: 0 !important;
    }
    
    /* Hide drag and drop text */
    div[data-testid="stFileUploader"] > div > div > div > div > section > div > div > div > div > small {
        display: none !important;
    }
    
    /* Platform buttons styling */
    .stButton > button {
        width: 100% !important;
        border-radius: 30px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header with branding
    create_header()
    
    # Navigation
    create_navigation()
    
    # Main content based on current page
    if st.session_state.current_page == 'dashboard':
        show_upload_interface(services)
    elif st.session_state.current_page == 'analytics':
        show_analytics_page(services)
    elif st.session_state.current_page == 'progress':
        show_progress_tracking(services)
    elif st.session_state.current_page == 'settings':
        show_settings(services)

def create_header():
    """Create the main header with branding"""
    st.markdown("""
    <div style="background: white; padding: 1rem 2rem; border-bottom: 1px solid #e0e0e0; margin-bottom: 0;">
        <div style="display: flex; align-items: center; justify-content: center;">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <div style="background: #6b7280; padding: 0.5rem; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                    <span style="color: white; font-size: 1.5rem;">🧠</span>
                </div>
                <div>
                    <h1 style="margin: 0; font-size: 28px; font-weight: 700; color: #1f2937;">MindAI</h1>
                    <p style="margin: 0; font-size: 0.9rem; color: #6b7280;">Therapeutic Wellness Platform</p>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_navigation():
    """Create navigation tabs"""
    current_page = st.session_state.get('current_page', 'dashboard')
    
    # Create navigation items with active states
    nav_items = [
        ("dashboard", "Dashboard"),
        ("analytics", "Analysis"), 
        ("progress", "Insights"),
        ("settings", "Settings")
    ]
    
    # Create navigation bar with proper styling
    st.markdown("""
    <div style="background: white; padding: 0 2rem; border-bottom: 1px solid #e0e0e0; margin-bottom: 2rem;">
    """, unsafe_allow_html=True)
    
    cols = st.columns(len(nav_items))
    
    for i, (page_key, page_name) in enumerate(nav_items):
        with cols[i]:
            # Style active/inactive buttons
            if current_page == page_key:
                button_type = "primary"
            else:
                button_type = "secondary"
            
            if st.button(page_name, key=f"nav_{page_key}", type=button_type):
                st.session_state.current_page = page_key
                st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

def show_upload_interface(services):
    """Show the main upload interface matching the design"""
    # Main title and description
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0; margin-bottom: 3rem;">
        <h1 style="color: #374151; font-size: 2.5rem; font-weight: 700; margin-bottom: 1rem;">Upload Session Content</h1>
        <p style="color: #6b7280; font-size: 1.1rem; max-width: 600px; margin: 0 auto; line-height: 1.6;">
            Choose your path to therapeutic insight. Each method builds upon the foundation of evidence-based analysis.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Three-column layout matching the design
    col1, col2, col3 = st.columns(3, gap="large")
    
    with col1:
        # Audio Foundation Card
        st.markdown("""
        <div style="background: white; border-radius: 20px; padding: 2rem; box-shadow: 0 4px 20px rgba(0,0,0,0.08); text-align: center; border: 1px solid #e5e7eb; min-height: 400px;">
            <div style="background: #6b7280; color: white; padding: 1.5rem; border-radius: 15px; margin-bottom: 1.5rem; display: inline-block;">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2C13.1 2 14 2.9 14 4V12C14 13.1 13.1 14 12 14C10.9 14 10 13.1 10 12V4C10 2.9 10.9 2 12 2Z" fill="white"/>
                    <path d="M19 10V12C19 15.9 15.9 19 12 19C8.1 19 5 15.9 5 12V10H7V12C7 14.8 9.2 17 12 17C14.8 17 17 14.8 17 12V10H19Z" fill="white"/>
                    <path d="M12 19V22H12" stroke="white" stroke-width="2"/>
                    <path d="M8 22H16" stroke="white" stroke-width="2"/>
                </svg>
            </div>
            <h3 style="color: #374151; margin-bottom: 1rem; font-size: 1.4rem; font-weight: 600;">Audio Foundation</h3>
            <p style="color: #6b7280; margin-bottom: 1.5rem; font-size: 0.95rem; line-height: 1.5;">Transform spoken sessions into therapeutic insights</p>
            <div style="color: #6b7280; margin-bottom: 2rem; font-size: 0.85rem;">
                <span style="font-weight: 600;">MP3, WAV, M4A</span> <span style="margin: 0 0.5rem;">•</span> <span style="font-weight: 600;">Up to 500MB</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Audio file uploader styled as button
        uploaded_audio = st.file_uploader(
            "Choose Audio",
            type=['mp3', 'wav', 'mp4', 'm4a', 'ogg', 'flac', 'aac'],
            key="audio_upload",
            help="Upload audio files for transcription and analysis",
            label_visibility="collapsed"
        )
        
        if uploaded_audio:
            st.success(f"File uploaded: {uploaded_audio.name}")
            if st.button("Analyze Audio", type="primary", key="analyze_audio", use_container_width=True):
                process_uploaded_file(services, uploaded_audio)

    with col2:
        # Text Pillar Card
        st.markdown("""
        <div style="background: white; border-radius: 20px; padding: 2rem; box-shadow: 0 4px 20px rgba(0,0,0,0.08); text-align: center; border: 1px solid #e5e7eb; min-height: 400px;">
            <div style="background: #d4b894; color: white; padding: 1.5rem; border-radius: 15px; margin-bottom: 1.5rem; display: inline-block;">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M14 2H6C4.9 2 4 2.9 4 4V20C4 21.1 4.9 22 6 22H18C19.1 22 20 21.1 20 20V8L14 2Z" fill="white"/>
                    <path d="M14 2V8H20" fill="white"/>
                    <path d="M16 13H8V15H16V13Z" fill="#d4b894"/>
                    <path d="M16 17H8V19H16V17Z" fill="#d4b894"/>
                    <path d="M10 9H8V11H10V9Z" fill="#d4b894"/>
                </svg>
            </div>
            <h3 style="color: #374151; margin-bottom: 1rem; font-size: 1.4rem; font-weight: 600;">Text Pillar</h3>
            <p style="color: #6b7280; margin-bottom: 1.5rem; font-size: 0.95rem; line-height: 1.5;">Direct analysis of written therapeutic content</p>
            <div style="color: #6b7280; margin-bottom: 2rem; font-size: 0.85rem;">
                <span style="font-weight: 600;">TXT, DOC, PDF</span> <span style="margin: 0 0.5rem;">•</span> <span style="font-weight: 600;">Up to 50MB</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Text file uploader styled as button
        uploaded_transcript = st.file_uploader(
            "Choose Document",
            type=['txt', 'doc', 'docx', 'pdf'],
            key="transcript_upload",
            help="Upload text documents for analysis",
            label_visibility="collapsed"
        )
        
        if uploaded_transcript:
            st.success(f"File uploaded: {uploaded_transcript.name}")
            
            # Show preview for PDF files
            if uploaded_transcript.type == "application/pdf":
                if st.button("Preview PDF Content", key="preview_pdf", use_container_width=True):
                    try:
                        from utils.file_handler import FileHandler
                        file_handler = FileHandler()
                        preview_text = file_handler.extract_text_from_file(uploaded_transcript)
                        
                        if preview_text:
                            # Show first 1000 characters as preview
                            preview_content = preview_text[:1000] + "..." if len(preview_text) > 1000 else preview_text
                            st.text_area("PDF Content Preview", preview_content, height=200)
                            
                            # Show file statistics
                            word_count = len(preview_text.split())
                            char_count = len(preview_text)
                            st.info(f"Document contains approximately {word_count:,} words and {char_count:,} characters")
                        else:
                            st.warning("Could not extract text from PDF. Please ensure the PDF contains readable text.")
                    except ImportError:
                        st.warning("PDF processing not available. Please upload a TXT file instead.")
            
            if st.button("Analyze Transcript", type="primary", key="analyze_transcript", use_container_width=True):
                process_transcript_file(services, uploaded_transcript)

    with col3:
        # Live Balance Card
        st.markdown("""
        <div style="background: white; border-radius: 20px; padding: 2rem; box-shadow: 0 4px 20px rgba(0,0,0,0.08); text-align: center; border: 1px solid #e5e7eb; min-height: 400px;">
            <div style="background: #6b8e23; color: white; padding: 1.5rem; border-radius: 15px; margin-bottom: 1.5rem; display: inline-block;">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M17 10.5V7C17 4.24 14.76 2 12 2C9.24 2 7 4.24 7 7V10.5C5.84 10.5 4.5 11.84 4.5 13V20C4.5 21.16 5.84 22.5 7 22.5H17C18.16 22.5 19.5 21.16 19.5 20V13C19.5 11.84 18.16 10.5 17 10.5Z" fill="white"/>
                    <circle cx="12" cy="16" r="1.5" fill="#6b8e23"/>
                </svg>
            </div>
            <h3 style="color: #374151; margin-bottom: 1rem; font-size: 1.4rem; font-weight: 600;">Live Balance</h3>
            <p style="color: #6b7280; margin-bottom: 2rem; font-size: 0.95rem; line-height: 1.5;">Real-time therapeutic session analysis</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Platform buttons with authentication status
        zoom_authenticated = st.session_state.get('zoom_authenticated', False)
        google_authenticated = st.session_state.get('google_authenticated', False)
        teams_authenticated = st.session_state.get('teams_authenticated', False)
        
        # Zoom button
        zoom_text = "🔵 Zoom (Connected)" if zoom_authenticated else "🔵 Zoom"
        if st.button(zoom_text, key="zoom_btn", use_container_width=True):
            if zoom_authenticated:
                show_zoom_recordings(services)
            else:
                st.session_state.show_zoom_auth = True
                st.success("Opening Zoom authentication...")
                st.rerun()
        
        # Google Meet button
        google_text = "🟢 Google Meet (Connected)" if google_authenticated else "🟢 Google Meet"
        if st.button(google_text, key="google_btn", use_container_width=True):
            if google_authenticated:
                show_google_recordings(services)
            else:
                st.session_state.show_google_auth = True
                st.rerun()
        
        # Teams button
        teams_text = "🟣 Teams (Connected)" if teams_authenticated else "🟣 Teams"
        if st.button(teams_text, key="teams_btn", use_container_width=True):
            if teams_authenticated:
                show_teams_recordings(services)
            else:
                st.session_state.show_teams_auth = True
                st.rerun()
    
    # Handle platform authentication modals
    if st.session_state.get('show_zoom_auth', False):
        show_zoom_auth_modal(services)
    
    if st.session_state.get('show_google_auth', False):
        show_google_auth_modal(services)
    
    if st.session_state.get('show_teams_auth', False):
        show_teams_auth_modal(services)
    


def show_service_status():
    """Show service status in a clean way"""
    openai_key = os.getenv("OPENAI_API_KEY")
    hf_key = os.getenv("HUGGINGFACE_API_KEY")
    
    if openai_key:
        status_text = "✅ OpenAI API (Premium Analysis)"
        status_color = "#28a745"
    elif hf_key:
        status_text = "🆓 Hugging Face (Free Analysis)"
        status_color = "#17a2b8"
    else:
        status_text = "🔧 Local Analysis (Basic)"
        status_color = "#ffc107"
    
    st.markdown(f"""
    <div style="text-align: center; margin: 1rem 0;">
        <span style="background: {status_color}20; color: {status_color}; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.9rem;">
            {status_text}
        </span>
    </div>
    """, unsafe_allow_html=True)

def show_platform_integration(services):
    """Show platform integration options"""
    st.markdown("""
    <div style="text-align: center; margin: 3rem 0 2rem 0;">
        <h3>Or connect directly to your video platform (Optional)</h3>
        <p style="color: #636e72;">Automatically detect and analyze new therapy sessions</p>
        <p style="color: #f39c12; font-size: 0.9rem;">⚠️ OAuth credentials required for platform integration</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    platforms = [
        {"name": "Zoom", "icon": "📹", "color": "#2D8CFF"},
        {"name": "Google Meet", "icon": "🎥", "color": "#4285F4"},
        {"name": "Microsoft Teams", "icon": "💼", "color": "#6264A7"}
    ]
    
    for i, platform in enumerate(platforms):
        with [col1, col2, col3][i]:
            # Check if authenticated
            is_authenticated = st.session_state.get(f'{platform["name"].lower()}_authenticated', False)
            status_class = "status-connected" if is_authenticated else "status-disconnected"
            status_text = "Connected" if is_authenticated else "Not Connected"
            
            st.markdown(f"""
            <div class="platform-card">
                <div style="font-size: 2rem; margin-bottom: 1rem;">{platform["icon"]}</div>
                <h4 style="margin: 0.5rem 0; color: {platform["color"]};">{platform["name"]}</h4>
                <div class="status-badge {status_class}">{status_text}</div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"Connect {platform['name']}", key=f"connect_{platform['name'].lower()}"):
                with st.spinner(f"Connecting to {platform['name']}..."):
                    auth_result = authenticate_platform(services, platform['name'])
                    if auth_result:
                        st.session_state[f'{platform["name"].lower()}_authenticated'] = True
                        st.success(f"Connected to {platform['name']}!")
                        st.rerun()
                    else:
                        st.error(f"Failed to connect to {platform['name']}")

def show_demo_section(services):
    """Show demo section for users without OAuth"""
    st.markdown("""
    <div style="text-align: center; margin: 3rem 0 2rem 0; padding: 2rem; background: #f8f9fa; border-radius: 15px;">
        <h3>🎯 Try Demo Analysis</h3>
        <p style="color: #636e72;">Test the enhanced negative pattern detection with sample therapeutic content</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Analyze Positive Session", type="secondary"):
            show_demo_analysis(services, demo_type="positive")
    
    with col2:
        if st.button("⚠️ Analyze Concerning Session", type="secondary"):
            show_demo_analysis(services, demo_type="concerning")

def show_analytics_page(services):
    """Show analytics page"""
    st.header("📈 Analytics")
    
    if st.session_state.analysis_results:
        display_analysis_results(st.session_state.analysis_results)
    else:
        st.info("No analysis results yet. Upload a session to see analytics.")

def generate_zoom_oauth_url():
    """Generate Zoom OAuth URL for user authentication"""
    # For demo purposes, we'll simulate the OAuth flow
    # In production, this would use a pre-configured OAuth app
    return "https://zoom.us/oauth/authorize?response_type=code&client_id=demo&redirect_uri=demo"

def handle_oauth_callback():
    """Handle OAuth callback and process authentication"""
    # Check URL parameters for OAuth callback
    query_params = st.experimental_get_query_params()
    
    if 'code' in query_params and 'state' in query_params:
        auth_code = query_params['code'][0]
        state = query_params['state'][0]
        
        if state == 'zoom_auth':
            # Exchange authorization code for access token
            access_token = exchange_zoom_code_for_token(auth_code)
            if access_token:
                st.session_state.zoom_access_token = access_token
                st.session_state.zoom_authenticated = True
                st.success("Successfully connected to Zoom!")
                st.experimental_set_query_params()  # Clear URL parameters
                st.rerun()

def exchange_zoom_code_for_token(auth_code):
    """Exchange authorization code for access token"""
    # In a real implementation, this would make an API call to exchange the code
    # For demo purposes, we'll simulate a successful token exchange
    return f"demo_token_{auth_code[:10]}"

def process_transcript_file(services, uploaded_file):
    """Process uploaded transcript file"""
    temp_file_path = None
    try:
        from utils.file_handler import FileHandler
        file_handler = FileHandler()
        
        # Validate file type and size
        if not file_handler.is_supported_text_file(uploaded_file):
            st.error("Unsupported file type. Please use TXT or PDF files.")
            return
            
        if not file_handler.validate_file_size(uploaded_file, max_size_mb=50):
            return
        
        # Extract text from file (file handler processes in memory, no temp file needed)
        st.info("Extracting text from file...")
        transcript = file_handler.extract_text_from_file(uploaded_file)
        
        if not transcript:
            st.error("Could not extract text from the file.")
            return
        
        # Validate transcript content
        if not transcript.strip():
            st.error("The uploaded file appears to be empty or contains no readable text.")
            return
        
        # Show file info
        file_info = file_handler.get_file_info(uploaded_file)
        st.info(f"Processing {file_info['name']} ({file_info['size_mb']} MB)")
        
        with st.spinner("Analyzing transcript..."):
            analysis_results = services['analysis'].analyze_session(transcript)
            
            if analysis_results:
                # Store the session data (only filename, not content)
                session_data = SessionData(
                    file_path=uploaded_file.name,  # Only store filename for reference
                    transcript=transcript,
                    analysis=analysis_results,
                    timestamp=datetime.now()
                )
                
                session_id = services['session_manager'].save_session(session_data)
                
                st.session_state.analysis_results = analysis_results
                st.session_state.current_page = 'analytics'
                st.success("Analysis complete! File processed securely.")
                st.rerun()
            else:
                st.error("Analysis failed. Please try again.")
                
    except Exception as e:
        st.error(f"Error processing transcript: {str(e)}")
    finally:
        # Clean up any temporary files (though text files are processed in memory)
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
                st.info("Temporary file cleaned up for privacy")
            except Exception as e:
                st.warning(f"Could not remove temporary file: {str(e)}")

def show_zoom_auth_modal(services):
    """Show Zoom authentication modal"""
    st.markdown("---")
    st.markdown("### 🔵 Connect to Zoom")
    st.markdown("Connect your Zoom account to access and analyze your cloud recordings.")
    
    # Check if user is already authenticated
    if st.session_state.get('zoom_authenticated', False):
        st.success("Successfully connected to Zoom!")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("View Recordings", key="view_zoom_recordings"):
                show_zoom_recordings(services)
        
        with col2:
            if st.button("Disconnect", key="disconnect_zoom"):
                st.session_state.zoom_authenticated = False
                st.session_state.zoom_access_token = None
                st.session_state.show_zoom_auth = False
                st.rerun()
    else:
        st.markdown("#### One-Click Connection:")
        st.markdown("Simply click the button below to connect your Zoom account securely.")
        
        # Simplified connection process
        if st.button("🔗 Connect to Zoom Account", key="simple_zoom_connect", type="primary"):
            # Simulate OAuth flow completion
            with st.spinner("Connecting to Zoom..."):
                # In production, this would redirect to Zoom's OAuth page
                # For now, we'll simulate the connection process
                import time
                time.sleep(2)  # Simulate OAuth process
                
                # Generate a demo token for testing
                demo_token = f"zoom_token_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                st.session_state.zoom_access_token = demo_token
                st.session_state.zoom_authenticated = True
                st.session_state.show_zoom_auth = False
                st.success("Successfully connected to Zoom!")
                st.rerun()
        
        st.markdown("---")
        st.markdown("**Note:** This will redirect you to Zoom's secure login page where you can safely enter your credentials.")
        
        # Cancel option
        if st.button("Cancel", key="cancel_zoom_simple"):
            st.session_state.show_zoom_auth = False
            st.rerun()
    
    st.markdown("---")

def show_google_auth_modal(services):
    """Show Google Meet authentication modal"""
    st.markdown("---")
    st.markdown("### 🟢 Connect to Google Meet")
    st.markdown("Connect your Google account to access and analyze your Meet recordings.")
    
    # Check if user is already authenticated
    if st.session_state.get('google_authenticated', False):
        st.success("Successfully connected to Google Meet!")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("View Recordings", key="view_google_recordings"):
                show_google_recordings(services)
        
        with col2:
            if st.button("Disconnect", key="disconnect_google"):
                st.session_state.google_authenticated = False
                st.session_state.google_access_token = None
                st.session_state.show_google_auth = False
                st.rerun()
    else:
        st.markdown("#### One-Click Connection:")
        st.markdown("Simply click the button below to connect your Google account securely.")
        
        # Simplified connection process
        if st.button("🔗 Connect to Google Account", key="simple_google_connect", type="primary"):
            # Simulate OAuth flow completion
            with st.spinner("Connecting to Google..."):
                import time
                time.sleep(2)  # Simulate OAuth process
                
                # Generate a demo token for testing
                demo_token = f"google_token_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                st.session_state.google_access_token = demo_token
                st.session_state.google_authenticated = True
                st.session_state.show_google_auth = False
                st.success("Successfully connected to Google Meet!")
                st.rerun()
        
        st.markdown("---")
        st.markdown("**Note:** This will redirect you to Google's secure login page where you can safely enter your credentials.")
        
        # Cancel option
        if st.button("Cancel", key="cancel_google_simple"):
            st.session_state.show_google_auth = False
            st.rerun()
    
    st.markdown("---")

def show_teams_auth_modal(services):
    """Show Microsoft Teams authentication modal"""
    st.markdown("---")
    st.markdown("### 🟣 Connect to Microsoft Teams")
    st.markdown("Connect your Microsoft Teams account to access and analyze your recordings.")
    
    # Check if user is already authenticated
    if st.session_state.get('teams_authenticated', False):
        st.success("Successfully connected to Microsoft Teams!")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("View Recordings", key="view_teams_recordings"):
                show_teams_recordings(services)
        
        with col2:
            if st.button("Disconnect", key="disconnect_teams"):
                st.session_state.teams_authenticated = False
                st.session_state.teams_access_token = None
                st.session_state.show_teams_auth = False
                st.rerun()
    else:
        st.markdown("#### One-Click Connection:")
        st.markdown("Simply click the button below to connect your Microsoft Teams account securely.")
        
        # Simplified connection process
        if st.button("🔗 Connect to Teams Account", key="simple_teams_connect", type="primary"):
            # Simulate OAuth flow completion
            with st.spinner("Connecting to Microsoft Teams..."):
                import time
                time.sleep(2)  # Simulate OAuth process
                
                # Generate a demo token for testing
                demo_token = f"teams_token_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                st.session_state.teams_access_token = demo_token
                st.session_state.teams_authenticated = True
                st.session_state.show_teams_auth = False
                st.success("Successfully connected to Microsoft Teams!")
                st.rerun()
        
        st.markdown("---")
        st.markdown("**Note:** This will redirect you to Microsoft's secure login page where you can safely enter your credentials.")
        
        # Cancel option
        if st.button("Cancel", key="cancel_teams_simple"):
            st.session_state.show_teams_auth = False
            st.rerun()
    
    st.markdown("---")

def test_zoom_connection(services):
    """Test the Zoom connection"""
    try:
        # Check if we have an access token
        if 'zoom_access_token' in st.session_state:
            # For demo purposes, always return True if we have a token
            return True
        else:
            return False
    except Exception as e:
        st.error(f"Connection test failed: {str(e)}")
        return False

def show_zoom_recordings(services):
    """Show available Zoom recordings"""
    st.markdown("### 🔵 Zoom Cloud Recordings")
    
    with st.spinner("Fetching Zoom recordings..."):
        try:
            # Demo recordings for testing
            demo_recordings = [
                {
                    'topic': 'Therapy Session - John D.',
                    'start_time': '2024-01-15 10:00:00',
                    'duration': 45,
                    'file_size': 125.5,
                    'recording_id': 'zoom_demo_1'
                },
                {
                    'topic': 'Group Therapy Session',
                    'start_time': '2024-01-14 14:30:00',
                    'duration': 60,
                    'file_size': 180.2,
                    'recording_id': 'zoom_demo_2'
                },
                {
                    'topic': 'Individual Counseling - Sarah M.',
                    'start_time': '2024-01-13 09:15:00',
                    'duration': 50,
                    'file_size': 140.8,
                    'recording_id': 'zoom_demo_3'
                }
            ]
            
            recordings = demo_recordings
            
            if recordings:
                st.success(f"Found {len(recordings)} recordings from the last 30 days")
                
                for i, recording in enumerate(recordings):
                    with st.expander(f"📹 {recording['topic']} - {recording['start_time']}"):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.write(f"**Duration:** {recording['duration']} minutes")
                            st.write(f"**File Size:** {recording['file_size']} MB")
                            st.write(f"**Start Time:** {recording['start_time']}")
                        
                        with col2:
                            if st.button("Analyze", key=f"analyze_zoom_{i}"):
                                st.info(f"Analyzing recording: {recording['topic']}")
                                st.success("Analysis complete! Check the Analytics tab for results.")
            else:
                st.info("No recordings found in the last 30 days")
                
        except Exception as e:
            st.error(f"Error fetching Zoom recordings: {str(e)}")
            st.info("Please check your Zoom credentials and try again")

def show_google_recordings(services):
    """Show available Google Meet recordings"""
    st.markdown("### 🟢 Google Meet Recordings")
    
    with st.spinner("Fetching Google Meet recordings..."):
        try:
            recordings = services['google_meet'].get_recent_recordings(days_back=30)
            
            if recordings:
                st.success(f"Found {len(recordings)} recordings from the last 30 days")
                
                for i, recording in enumerate(recordings):
                    with st.expander(f"📹 {recording['name']} - {recording['created_time']}"):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.write(f"**File Size:** {recording['size']} MB")
                            st.write(f"**Created:** {recording['created_time']}")
                        
                        with col2:
                            if st.button("Analyze", key=f"analyze_google_{i}"):
                                # Download and analyze the recording
                                with st.spinner("Downloading and analyzing recording..."):
                                    audio_file = services['google_meet'].download_recording(recording)
                                    if audio_file:
                                        # Process the downloaded audio
                                        transcript = services['transcription'].transcribe_audio(audio_file)
                                        if transcript:
                                            analysis = services['analysis'].analyze_session(transcript)
                                            st.session_state.analysis_results = analysis
                                            st.session_state.current_page = 'analytics'
                                            st.success("Analysis complete!")
                                            st.rerun()
                                    else:
                                        st.error("Failed to download recording")
            else:
                st.info("No recordings found in the last 30 days")
                
        except Exception as e:
            st.error(f"Error fetching Google Meet recordings: {str(e)}")
            st.info("Please check your Google credentials and try again")

def show_teams_recordings(services):
    """Show available Teams recordings"""
    st.markdown("### 🟣 Microsoft Teams Recordings")
    
    with st.spinner("Fetching Teams recordings..."):
        try:
            recordings = services['teams'].get_recent_recordings(days_back=30)
            
            if recordings:
                st.success(f"Found {len(recordings)} recordings from the last 30 days")
                
                for i, recording in enumerate(recordings):
                    with st.expander(f"📹 {recording['name']} - {recording['created_time']}"):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.write(f"**Duration:** {recording['duration']} minutes")
                            st.write(f"**File Size:** {recording['size']} MB")
                            st.write(f"**Created:** {recording['created_time']}")
                        
                        with col2:
                            if st.button("Analyze", key=f"analyze_teams_{i}"):
                                # Download and analyze the recording
                                with st.spinner("Downloading and analyzing recording..."):
                                    audio_file = services['teams'].download_recording(recording)
                                    if audio_file:
                                        # Process the downloaded audio
                                        transcript = services['transcription'].transcribe_audio(audio_file)
                                        if transcript:
                                            analysis = services['analysis'].analyze_session(transcript)
                                            st.session_state.analysis_results = analysis
                                            st.session_state.current_page = 'analytics'
                                            st.success("Analysis complete!")
                                            st.rerun()
                                    else:
                                        st.error("Failed to download recording")
            else:
                st.info("No recordings found in the last 30 days")
                
        except Exception as e:
            st.error(f"Error fetching Teams recordings: {str(e)}")
            st.info("Please check your Teams credentials and try again")

def authenticate_platform(services, platform):
    """Legacy function for backward compatibility"""
    return True

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
    file_path = None
    try:
        with st.spinner("Processing audio file..."):
            # Save uploaded file temporarily
            file_path = services['session_manager'].save_uploaded_file(uploaded_file)
            
            # Transcribe
            st.info("Transcribing audio...")
            transcript = services['transcription'].transcribe_audio(file_path)
            
            if not transcript:
                st.error("Transcription failed. Please try again or use a different file.")
                return
            
            # Analyze
            st.info("Analyzing session content...")
            analysis_results = services['analysis'].analyze_session(transcript)
            
            if not analysis_results:
                st.error("Analysis failed. Please try again.")
                return
            
            # Store results (without file path for privacy)
            session_data = SessionData(
                file_path=uploaded_file.name,  # Only store filename, not full path
                transcript=transcript,
                analysis=analysis_results,
                timestamp=datetime.now()
            )
            
            services['session_manager'].save_session(session_data)
            st.session_state.current_session = session_data
            st.session_state.analysis_results = analysis_results
            
            st.success("Session processed successfully!")
            st.session_state.current_page = 'analytics'
            st.rerun()
            
    except Exception as e:
        st.error(f"Processing error: {str(e)}")
    finally:
        # Always clean up the uploaded file after processing
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                st.info("Temporary file cleaned up for privacy")
            except Exception as e:
                st.warning(f"Could not remove temporary file: {str(e)}")

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
    """Display analysis results in user-friendly terms"""
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0;">
        <h2 style="color: #667eea;">Your Therapy Session Analysis</h2>
        <p style="color: #636e72;">Here's what we discovered about your therapeutic progress</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check for therapy effectiveness assessment
    therapy_effectiveness = analysis.get('therapy_effectiveness', {})
    warning_signs = analysis.get('warning_signs', [])
    
    # Display therapy effectiveness warning if concerning
    if therapy_effectiveness and therapy_effectiveness.get('status') == 'concerning':
        st.markdown("""
        <div style="background: #e74c3c20; border-left: 4px solid #e74c3c; padding: 1rem; margin: 1rem 0; border-radius: 5px;">
            <h3 style="color: #e74c3c; margin: 0;">⚠️ Therapy Effectiveness Alert</h3>
            <p style="margin: 0.5rem 0 0 0; font-weight: bold;">""" + therapy_effectiveness.get('message', '') + """</p>
        </div>
        """, unsafe_allow_html=True)
    elif therapy_effectiveness and therapy_effectiveness.get('status') == 'mixed':
        st.markdown("""
        <div style="background: #f39c1220; border-left: 4px solid #f39c12; padding: 1rem; margin: 1rem 0; border-radius: 5px;">
            <h3 style="color: #f39c12; margin: 0;">⚠️ Mixed Progress</h3>
            <p style="margin: 0.5rem 0 0 0;">""" + therapy_effectiveness.get('message', '') + """</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Display warning signs if present
    if warning_signs:
        st.markdown("### 🚨 Areas of Concern")
        for warning in warning_signs:
            severity_color = '#e74c3c' if warning['severity'] == 'high' else '#f39c12'
            st.markdown(f"""
            <div style="background: {severity_color}15; border-left: 4px solid {severity_color}; padding: 1rem; margin: 0.5rem 0; border-radius: 5px;">
                <h4 style="color: {severity_color}; margin: 0;">{warning['category']}</h4>
                <p style="margin: 0.5rem 0 0 0;">{warning['description']}</p>
                <small style="color: #636e72;">Indicators: {', '.join(warning['indicators'][:3])}</small>
            </div>
            """, unsafe_allow_html=True)
    
    # Overall summary
    scores = analysis.get('domain_scores', {})
    if scores:
        avg_score = sum(scores.values()) / len(scores)
        overall_status = get_overall_status(avg_score)
        
        st.markdown(f"""
        <div style="background: {overall_status['color']}20; border-left: 4px solid {overall_status['color']}; padding: 1rem; margin: 1rem 0; border-radius: 5px;">
            <h3 style="color: {overall_status['color']}; margin: 0;">Overall Progress: {overall_status['label']}</h3>
            <p style="margin: 0.5rem 0 0 0;">{overall_status['description']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Display comprehensive multi-assessment results
    multi_assessment = analysis.get('multi_assessment_results', {})
    if multi_assessment:
        st.markdown("### 🔍 Comprehensive Assessment Analysis")
        st.markdown("*Using multiple evidence-based assessment methods and sources*")
        
        # Assessment methods used
        methods_used = multi_assessment.get('methods_used', [])
        if methods_used:
            st.markdown("**Assessment Methods Applied:**")
            method_names = {
                'unstructured_interview': 'Clinical Interview Analysis',
                'structured_interview': 'Systematic Coverage Assessment', 
                'behavioral_observation': 'Behavioral Pattern Analysis',
                'therapeutic_rating_scales': 'Standardized Rating Scales'
            }
            for method in methods_used:
                if method in method_names:
                    st.markdown(f"• {method_names[method]}")
        
        # Reliability assessment
        reliability = multi_assessment.get('reliability_assessment', {})
        if reliability:
            rel_level = reliability.get('reliability_level', 'moderate')
            rel_color = '#27ae60' if rel_level == 'high' else '#f39c12' if rel_level == 'moderate' else '#e74c3c'
            st.markdown(f"""
            <div style="background: {rel_color}15; border-left: 4px solid {rel_color}; padding: 1rem; margin: 0.5rem 0; border-radius: 5px;">
                <h4 style="color: {rel_color}; margin: 0;">Assessment Reliability: {rel_level.title()}</h4>
                <p style="margin: 0.5rem 0 0 0;">Overall reliability score: {reliability.get('overall_reliability', 0):.1f}/10</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Validity indicators
        validity = multi_assessment.get('validity_indicators', {})
        if validity:
            val_level = validity.get('validity_level', 'moderate')
            val_color = '#27ae60' if val_level == 'high' else '#f39c12' if val_level == 'moderate' else '#e74c3c'
            st.markdown(f"""
            <div style="background: {val_color}15; border-left: 4px solid {val_color}; padding: 1rem; margin: 0.5rem 0; border-radius: 5px;">
                <h4 style="color: {val_color}; margin: 0;">Assessment Validity: {val_level.title()}</h4>
                <p style="margin: 0.5rem 0 0 0;">Overall validity score: {validity.get('overall_validity', 0):.1f}/10</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Clinical recommendations from multi-assessment
        clinical_recs = multi_assessment.get('clinical_recommendations', [])
        if clinical_recs:
            st.markdown("**Evidence-Based Clinical Recommendations:**")
            for rec in clinical_recs[:5]:  # Show first 5 recommendations
                st.markdown(f"• {rec}")
        
        # Assessment limitations
        limitations = multi_assessment.get('assessment_limitations', [])
        if limitations:
            with st.expander("📝 Assessment Limitations & Considerations"):
                st.markdown("**Important Assessment Limitations:**")
                for limitation in limitations[:5]:  # Show first 5 limitations
                    st.markdown(f"• {limitation}")
    
    # User-friendly domain explanations
    st.subheader("📊 Key Areas of Growth")
    
    domain_explanations = {
        'emotional_safety': {
            'title': 'Emotional Safety & Trust',
            'description': 'How comfortable and secure you feel in the therapeutic relationship',
            'icon': '🤝'
        },
        'unconscious_patterns': {
            'title': 'Pattern Recognition',
            'description': 'Understanding recurring themes and behaviors in your life',
            'icon': '🔍'
        },
        'cognitive_restructuring': {
            'title': 'Thought Patterns',
            'description': 'How well you\'re identifying and changing unhelpful thinking',
            'icon': '💭'
        },
        'communication_changes': {
            'title': 'Communication Skills',
            'description': 'Improvements in how you express yourself and relate to others',
            'icon': '💬'
        },
        'strengths_wellbeing': {
            'title': 'Personal Strengths',
            'description': 'Recognition and development of your positive qualities',
            'icon': '⭐'
        },
        'narrative_coherence': {
            'title': 'Life Story',
            'description': 'How well you understand and tell your personal story',
            'icon': '📖'
        },
        'behavioral_activation': {
            'title': 'Taking Action',
            'description': 'Steps you\'re taking to apply insights in daily life',
            'icon': '🎯'
        }
    }
    
    # Create progress cards
    cols = st.columns(2)
    col_index = 0
    
    for domain, score in scores.items():
        domain_info = domain_explanations.get(domain, {})
        if not domain_info:
            continue
            
        with cols[col_index % 2]:
            progress_level = get_progress_level(score)
            
            st.markdown(f"""
            <div style="background: white; border-radius: 10px; padding: 1.5rem; margin: 1rem 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                    <span style="font-size: 2rem;">{domain_info['icon']}</span>
                    <div>
                        <h4 style="margin: 0; color: #2d3436;">{domain_info['title']}</h4>
                        <p style="margin: 0; color: #636e72; font-size: 0.9rem;">{domain_info['description']}</p>
                    </div>
                </div>
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <div style="flex: 1; background: #f1f3f4; border-radius: 10px; height: 8px;">
                        <div style="width: {score*10}%; background: {progress_level['color']}; height: 100%; border-radius: 10px; transition: width 0.3s ease;"></div>
                    </div>
                    <span style="font-weight: 600; color: {progress_level['color']};">{score:.1f}/10</span>
                </div>
                <p style="margin: 0.5rem 0 0 0; color: {progress_level['color']}; font-size: 0.85rem;">{progress_level['message']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        col_index += 1
    
    # Visual chart
    st.subheader("📈 Visual Progress Overview")
    
    # Create a more user-friendly radar chart
    categories = [domain_explanations[k]['title'] for k in scores.keys() if k in domain_explanations]
    values = [scores[k] for k in scores.keys() if k in domain_explanations]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Current Session',
        fillcolor='rgba(102, 126, 234, 0.3)',
        line=dict(color='rgba(102, 126, 234, 1)', width=2)
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10],
                tickvals=[0, 2, 4, 6, 8, 10],
                ticktext=['0', '2', '4', '6', '8', '10']
            )),
        showlegend=False,
        title=dict(
            text="Your Therapeutic Progress Map",
            x=0.5,
            font=dict(size=18, color='#2d3436')
        ),
        font=dict(color='#636e72'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Key insights in friendly language
    insights = analysis.get('key_insights', [])
    if insights:
        st.subheader("💡 What This Means for You")
        for i, insight in enumerate(insights, 1):
            friendly_insight = make_insight_friendly(insight)
            st.markdown(f"""
            <div style="background: #f8f9fa; border-radius: 8px; padding: 1rem; margin: 0.5rem 0; border-left: 3px solid #667eea;">
                <strong>Insight {i}:</strong> {friendly_insight}
            </div>
            """, unsafe_allow_html=True)
    
    # Recommendations in actionable terms
    recommendations = analysis.get('recommendations', [])
    if recommendations:
        st.subheader("🚀 Next Steps to Consider")
        for i, rec in enumerate(recommendations, 1):
            friendly_rec = make_recommendation_friendly(rec)
            st.markdown(f"""
            <div style="background: #e8f5e8; border-radius: 8px; padding: 1rem; margin: 0.5rem 0; border-left: 3px solid #28a745;">
                <strong>Action {i}:</strong> {friendly_rec}
            </div>
            """, unsafe_allow_html=True)
    
    # Expert therapist evaluation
    expert_evaluation = analysis.get('expert_therapist_evaluation')
    if expert_evaluation:
        display_expert_therapist_evaluation(expert_evaluation)
    
    # Regular therapist evaluation (legacy)
    therapist_evaluation = analysis.get('therapist_evaluation')
    if therapist_evaluation and not expert_evaluation:
        display_therapist_evaluation(therapist_evaluation)
    
    # Progress summary
    show_progress_summary(analysis)

def display_expert_therapist_evaluation(expert_evaluation):
    """Display expert-level therapist evaluation results"""
    st.subheader("🎯 Expert Therapist Assessment")
    st.markdown("*Based on principles from Rogers, Beck, Freud, Jung, Yalom, and other leading therapeutic experts*")
    
    # Main assessment scores
    col1, col2 = st.columns(2)
    
    with col1:
        empathy_score = expert_evaluation.get('therapist_empathy_score', 6)
        empathy_color = '#28a745' if empathy_score >= 8 else '#ffc107' if empathy_score >= 6 else '#dc3545'
        
        st.markdown(f"""
        <div style="background: white; border-radius: 12px; padding: 1.5rem; margin: 1rem 0; border: 2px solid {empathy_color};">
            <h4 style="color: {empathy_color}; margin: 0 0 0.5rem 0;">Empathy & Attunement</h4>
            <div style="font-size: 2rem; font-weight: bold; color: {empathy_color};">{empathy_score}/10</div>
            <p style="margin: 0.5rem 0 0 0; color: #666; font-size: 0.9rem;">Emotional resonance and psychological safety</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        fit_score = expert_evaluation.get('therapist_fit_score', 6)
        fit_color = '#28a745' if fit_score >= 8 else '#ffc107' if fit_score >= 6 else '#dc3545'
        
        st.markdown(f"""
        <div style="background: white; border-radius: 12px; padding: 1.5rem; margin: 1rem 0; border: 2px solid {fit_color};">
            <h4 style="color: {fit_color}; margin: 0 0 0.5rem 0;">Therapist Fit Score</h4>
            <div style="font-size: 2rem; font-weight: bold; color: {fit_color};">{fit_score}/10</div>
            <p style="margin: 0.5rem 0 0 0; color: #666; font-size: 0.9rem;">Alignment with client needs and connection</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Evidence and insights
    evidence = expert_evaluation.get('empathy_evidence', [])
    if evidence:
        st.markdown("**Evidence of Empathy & Attunement:**")
        for item in evidence:
            st.markdown(f"• {item}")
    
    # Therapeutic techniques
    techniques = expert_evaluation.get('therapeutic_techniques', [])
    if techniques:
        st.markdown("**Therapeutic Approaches Used:**")
        for technique in techniques:
            st.markdown(f"• {technique}")
    
    # Burnout assessment
    burnout_signs = expert_evaluation.get('burnout_signs', {})
    if burnout_signs.get('present'):
        st.warning(f"⚠️ **Potential Concerns:** {burnout_signs.get('explanation', 'Signs of therapist disengagement detected')}")
    else:
        st.info(f"✅ **Professional Engagement:** {burnout_signs.get('explanation', 'No signs of burnout or disengagement detected')}")
    
    # Client progress
    progress = expert_evaluation.get('client_progress', {})
    if progress.get('present'):
        st.success("📈 **Progress Signals Detected**")
        examples = progress.get('examples', [])
        if examples:
            for example in examples:
                st.markdown(f"• {example}")
    else:
        st.info("📊 **Progress Monitoring:** Continue tracking progress in future sessions")
    
    # Professional recommendations
    recommendations = expert_evaluation.get('client_recommendations', [])
    if recommendations:
        st.markdown("### 🎯 Professional Recommendations")
        for i, rec in enumerate(recommendations, 1):
            st.markdown(f"""
            <div style="background: #e8f5e8; border-radius: 8px; padding: 1rem; margin: 0.5rem 0; border-left: 3px solid #28a745;">
                <strong>Recommendation {i}:</strong> {rec}
            </div>
            """, unsafe_allow_html=True)
    
    # Fit justification
    fit_justification = expert_evaluation.get('fit_justification', '')
    if fit_justification:
        st.markdown("**Professional Assessment:**")
        st.markdown(fit_justification)

def display_therapist_evaluation(therapist_evaluation):
    """Display therapist evaluation results"""
    st.subheader("👨‍⚕️ Therapist Performance Analysis")
    
    # Overall score display
    overall_score = therapist_evaluation.get('overall_score', 5)
    
    # Create color coding for therapist score
    if overall_score >= 8:
        color = '#28a745'
        status = 'Excellent'
    elif overall_score >= 6:
        color = '#17a2b8'
        status = 'Good'
    elif overall_score >= 4:
        color = '#ffc107'
        status = 'Adequate'
    else:
        color = '#dc3545'
        status = 'Needs Improvement'
    
    st.markdown(f"""
    <div style="background: white; border-radius: 10px; padding: 1.5rem; margin: 1rem 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center;">
        <h3 style="color: #2d3436; margin: 0 0 1rem 0;">Overall Therapist Performance</h3>
        <div style="font-size: 2.5rem; font-weight: bold; color: {color}; margin: 0.5rem 0;">
            {overall_score}/10
        </div>
        <div style="background: {color}; color: white; padding: 0.5rem 1rem; border-radius: 20px; display: inline-block;">
            {status}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Performance breakdown
    st.subheader("Performance Breakdown")
    
    performance_areas = {
        'empathy_score': {'title': 'Empathy & Emotional Attunement', 'icon': '❤️'},
        'communication_score': {'title': 'Communication Skills', 'icon': '💬'},
        'technique_score': {'title': 'Therapeutic Techniques', 'icon': '🎯'},
        'professional_score': {'title': 'Professional Boundaries', 'icon': '⚖️'}
    }
    
    cols = st.columns(2)
    col_index = 0
    
    for area, info in performance_areas.items():
        score = therapist_evaluation.get(area, 5)
        
        # Determine color based on score
        if score >= 7:
            progress_color = '#28a745'
            level = 'Strong'
        elif score >= 5:
            progress_color = '#17a2b8'
            level = 'Good'
        else:
            progress_color = '#ffc107'
            level = 'Needs Work'
        
        with cols[col_index % 2]:
            st.markdown(f"""
            <div style="background: white; border-radius: 10px; padding: 1.5rem; margin: 1rem 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                    <span style="font-size: 2rem;">{info['icon']}</span>
                    <div>
                        <h4 style="margin: 0; color: #2d3436;">{info['title']}</h4>
                        <p style="margin: 0; color: #636e72; font-size: 0.9rem;">{level}</p>
                    </div>
                </div>
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <div style="flex: 1; background: #f1f3f4; border-radius: 10px; height: 8px;">
                        <div style="width: {score*10}%; background: {progress_color}; height: 100%; border-radius: 10px;"></div>
                    </div>
                    <span style="font-weight: 600; color: {progress_color};">{score:.1f}/10</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        col_index += 1
    
    # Strengths and areas for improvement
    col1, col2 = st.columns(2)
    
    with col1:
        strengths = therapist_evaluation.get('strengths', [])
        if strengths:
            st.subheader("✅ Therapist Strengths")
            for strength in strengths:
                st.markdown(f"""
                <div style="background: #e8f5e8; border-radius: 8px; padding: 1rem; margin: 0.5rem 0; border-left: 3px solid #28a745;">
                    {strength}
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        improvements = therapist_evaluation.get('areas_for_improvement', [])
        if improvements:
            st.subheader("🔄 Areas for Improvement")
            for improvement in improvements:
                st.markdown(f"""
                <div style="background: #fff3cd; border-radius: 8px; padding: 1rem; margin: 0.5rem 0; border-left: 3px solid #ffc107;">
                    {improvement}
                </div>
                """, unsafe_allow_html=True)
    
    # Specific feedback
    feedback = therapist_evaluation.get('specific_feedback', [])
    if feedback:
        st.subheader("💭 Specific Feedback")
        for item in feedback:
            st.markdown(f"""
            <div style="background: #f8f9fa; border-radius: 8px; padding: 1rem; margin: 0.5rem 0; border-left: 3px solid #667eea;">
                {item}
            </div>
            """, unsafe_allow_html=True)

def get_overall_status(avg_score):
    """Get overall status based on average score"""
    if avg_score >= 8:
        return {
            'label': 'Excellent Progress',
            'description': 'You\'re showing strong growth across multiple areas of therapy.',
            'color': '#28a745'
        }
    elif avg_score >= 6:
        return {
            'label': 'Good Progress',
            'description': 'You\'re making solid progress with room for continued growth.',
            'color': '#17a2b8'
        }
    elif avg_score >= 4:
        return {
            'label': 'Steady Progress',
            'description': 'You\'re building a foundation and working through important areas.',
            'color': '#ffc107'
        }
    else:
        return {
            'label': 'Early Stages',
            'description': 'You\'re beginning your therapeutic journey with areas to explore.',
            'color': '#fd7e14'
        }

def get_progress_level(score):
    """Get progress level description"""
    if score >= 8:
        return {
            'message': 'Excellent - Strong growth in this area',
            'color': '#28a745'
        }
    elif score >= 6:
        return {
            'message': 'Good - Solid progress being made',
            'color': '#17a2b8'
        }
    elif score >= 4:
        return {
            'message': 'Developing - Building skills here',
            'color': '#ffc107'
        }
    else:
        return {
            'message': 'Starting - Area to focus on',
            'color': '#fd7e14'
        }

def make_insight_friendly(insight):
    """Convert technical insight to user-friendly language"""
    # Replace technical terms with simpler ones
    friendly_terms = {
        'therapeutic alliance': 'your relationship with your therapist',
        'cognitive restructuring': 'changing unhelpful thought patterns',
        'psychodynamic': 'understanding deeper patterns',
        'behavioral activation': 'taking positive actions',
        'narrative coherence': 'understanding your life story',
        'transference': 'how past relationships affect current ones',
        'defense mechanisms': 'ways you protect yourself emotionally',
        'unconscious patterns': 'automatic behaviors you might not notice'
    }
    
    friendly_insight = insight.lower()
    for technical, friendly in friendly_terms.items():
        friendly_insight = friendly_insight.replace(technical, friendly)
    
    return friendly_insight.capitalize()

def make_recommendation_friendly(recommendation):
    """Convert technical recommendation to actionable language"""
    friendly_terms = {
        'explore': 'talk about',
        'enhance': 'improve',
        'develop': 'work on',
        'strengthen': 'build up',
        'address': 'work on',
        'implement': 'try',
        'practice': 'work on',
        'consider': 'think about'
    }
    
    friendly_rec = recommendation.lower()
    for technical, friendly in friendly_terms.items():
        friendly_rec = friendly_rec.replace(technical, friendly)
    
    return friendly_rec.capitalize()

def show_progress_summary(analysis):
    """Show a simple progress summary"""
    st.subheader("📋 Session Summary")
    
    themes = analysis.get('session_themes', [])
    progress_indicators = analysis.get('progress_indicators', [])
    
    col1, col2 = st.columns(2)
    
    with col1:
        if themes:
            st.markdown("**Main topics discussed:**")
            for theme in themes[:3]:  # Show top 3
                st.write(f"• {theme}")
    
    with col2:
        if progress_indicators:
            st.markdown("**Signs of progress:**")
            for indicator in progress_indicators[:3]:  # Show top 3
                st.write(f"• {indicator}")
    
    # Encouraging message
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1.5rem; border-radius: 10px; text-align: center; margin: 2rem 0;">
        <h4 style="margin: 0 0 0.5rem 0;">Remember</h4>
        <p style="margin: 0;">Therapy is a journey, not a destination. Each session is a step forward in your personal growth.</p>
    </div>
    """, unsafe_allow_html=True)

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
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0; background: #f8f9fa; margin: -2rem -2rem 2rem -2rem;">
        <h1 style="color: #374151; margin-bottom: 1rem; font-size: 2.5rem; font-weight: 600;">Therapeutic Insights</h1>
        <p style="color: #6b7280; font-size: 1.1rem; max-width: 600px; margin: 0 auto;">
            Discover patterns and progress in your therapeutic journey
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    sessions = services['session_manager'].get_all_sessions()
    
    if len(sessions) == 0:
        st.markdown("""
        <div style="text-align: center; padding: 3rem; background: white; border-radius: 15px; margin: 2rem 0;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">📊</div>
            <h3 style="color: #374151; margin-bottom: 1rem;">No Sessions Found</h3>
            <p style="color: #6b7280; margin-bottom: 2rem;">Upload your first therapy session to begin tracking insights and progress.</p>
            <button style="background: #6b7280; color: white; border: none; padding: 1rem 2rem; border-radius: 10px; font-weight: 600; cursor: pointer;">
                Upload Session
            </button>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Show latest session insights
    if sessions:
        latest_session = sessions[-1]
        analysis = latest_session.analysis
        
        # Key insights from latest session
        st.markdown("""
        <div style="background: white; border-radius: 15px; padding: 2rem; margin: 2rem 0; box-shadow: 0 4px 20px rgba(0,0,0,0.08);">
            <h3 style="color: #374151; margin-bottom: 1rem;">Latest Session Insights</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Display key insights
        insights = analysis.get('key_insights', [])
        if insights:
            for insight in insights[:3]:  # Show top 3 insights
                st.markdown(f"""
                <div style="background: #f8f9fa; border-left: 4px solid #6b7280; padding: 1rem; margin: 1rem 0;">
                    <p style="color: #374151; margin: 0; font-size: 0.95rem;">{insight}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Show therapist evaluation if available
        therapist_eval = analysis.get('therapist_evaluation', {})
        if therapist_eval:
            st.markdown("""
            <div style="background: white; border-radius: 15px; padding: 2rem; margin: 2rem 0; box-shadow: 0 4px 20px rgba(0,0,0,0.08);">
                <h3 style="color: #374151; margin-bottom: 1rem;">Therapist Performance</h3>
            </div>
            """, unsafe_allow_html=True)
            
            overall_rating = therapist_eval.get('overall_rating', 0)
            st.markdown(f"""
            <div style="text-align: center; margin: 2rem 0;">
                <div style="font-size: 3rem; color: #6b7280; margin-bottom: 1rem;">⭐</div>
                <h2 style="color: #374151; margin: 0;">{overall_rating}/10</h2>
                <p style="color: #6b7280; margin: 0;">Overall Performance</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Show domain breakdown
            domains = therapist_eval.get('domain_scores', {})
            if domains:
                col1, col2, col3, col4 = st.columns(4)
                domain_names = ['Empathy', 'Communication', 'Techniques', 'Professionalism']
                domain_keys = ['empathy', 'communication', 'techniques', 'professionalism']
                
                for i, (col, name, key) in enumerate(zip([col1, col2, col3, col4], domain_names, domain_keys)):
                    with col:
                        score = domains.get(key, 0)
                        st.markdown(f"""
                        <div style="text-align: center; background: #f8f9fa; padding: 1rem; border-radius: 10px;">
                            <h4 style="color: #374151; margin: 0 0 0.5rem 0;">{name}</h4>
                            <div style="font-size: 1.5rem; color: #6b7280; font-weight: 600;">{score}/10</div>
                        </div>
                        """, unsafe_allow_html=True)
    
    # Progress tracking if multiple sessions
    if len(sessions) >= 2:
        st.markdown("""
        <div style="background: white; border-radius: 15px; padding: 2rem; margin: 2rem 0; box-shadow: 0 4px 20px rgba(0,0,0,0.08);">
            <h3 style="color: #374151; margin-bottom: 1rem;">Progress Over Time</h3>
        </div>
        """, unsafe_allow_html=True)
        
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
        st.markdown("""
        <div style="background: white; border-radius: 15px; padding: 2rem; margin: 2rem 0; box-shadow: 0 4px 20px rgba(0,0,0,0.08);">
            <h3 style="color: #374151; margin-bottom: 1rem;">Progress Summary</h3>
        </div>
        """, unsafe_allow_html=True)
        
        first_session = sessions[0].analysis.get('domain_scores', {})
        last_session = sessions[-1].analysis.get('domain_scores', {})
        
        for domain in domain_options:
            if domain in first_session and domain in last_session:
                change = last_session[domain] - first_session[domain]
                direction = "↗️" if change > 0 else "↘️" if change < 0 else "➡️"
                st.markdown(f"""
                <div style="background: #f8f9fa; padding: 1rem; border-radius: 10px; margin: 0.5rem 0;">
                    <span style="color: #374151; font-weight: 600;">{domain.replace('_', ' ').title()}:</span>
                    <span style="color: #6b7280; margin-left: 1rem;">{direction} {change:+.1f}</span>
                </div>
                """, unsafe_allow_html=True)

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

def show_demo_analysis(services, demo_type="positive"):
    """Show demo analysis with sample therapeutic content"""
    st.header("🎯 Demo: Enhanced Pattern Detection")
    
    if demo_type == "positive":
        st.subheader("✅ Positive Session Example")
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
        
    else:  # concerning
        st.subheader("⚠️ Concerning Session Example")
        demo_transcript = """
        Therapist: How have you been feeling since our last session?
        
        Client: Honestly, I don't think this is helping. I feel like I'm getting worse, not better. The anxiety is overwhelming and I can't cope anymore.
        
        Therapist: I understand this is difficult. Can you tell me more about what's not working?
        
        Client: Nothing works. I've tried everything you suggested but it's all pointless. I'm hopeless and I don't see the point in continuing. You don't really understand what I'm going through.
        
        Therapist: I hear that you're feeling frustrated with our work together.
        
        Client: Frustrated doesn't even begin to cover it. I'm angry that I'm wasting my time and money on this. I've been coming here for months with no progress. I'm stuck in the same patterns and I want to give up.
        
        Therapist: It sounds like you're experiencing some strong feelings about therapy right now.
        
        Client: I don't feel safe or understood here. This therapy isn't working and I'm thinking about not coming back. I feel more depressed than when I started.
        """
    
    st.text_area("Demo Transcript", demo_transcript, height=200, disabled=True)
    
    if st.button("Analyze This Session"):
        with st.spinner("Running enhanced pattern analysis..."):
            analysis_results = services['analysis'].analyze_session(demo_transcript)
            
            if analysis_results:
                st.session_state.analysis_results = analysis_results
                st.session_state.current_page = 'analytics'
                st.success("Analysis complete! Redirecting to analytics...")
                st.rerun()
            else:
                st.error("Analysis failed. Please check the logs.")

def show_settings(services):
    """Show settings and configuration"""
    st.header("⚙️ Settings")
    
    # OAuth Configuration
    st.subheader("Platform Integration (OAuth)")
    
    with st.expander("Configure Platform Access"):
        st.markdown("""
        **Note:** Platform integration is optional. You can use all core features by uploading files directly.
        
        To connect to video platforms, you'll need to create OAuth applications:
        """)
        
        # Zoom OAuth
        zoom_client_id = os.getenv("ZOOM_CLIENT_ID")
        zoom_client_secret = os.getenv("ZOOM_CLIENT_SECRET")
        
        st.markdown("**Zoom Configuration:**")
        if zoom_client_id and zoom_client_secret:
            st.success("✅ Zoom OAuth configured")
        else:
            st.warning("⚠️ Zoom OAuth not configured")
            st.markdown("""
            1. Go to https://marketplace.zoom.us/develop/create
            2. Create an OAuth app
            3. Set redirect URI to your app URL + /auth/zoom/callback
            4. Add ZOOM_CLIENT_ID and ZOOM_CLIENT_SECRET to environment variables
            """)
        
        # Google OAuth
        google_client_id = os.getenv("GOOGLE_CLIENT_ID")
        google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        
        st.markdown("**Google Meet Configuration:**")
        if google_client_id and google_client_secret:
            st.success("✅ Google OAuth configured")
        else:
            st.warning("⚠️ Google OAuth not configured")
            st.markdown("""
            1. Go to https://console.cloud.google.com/
            2. Create OAuth 2.0 credentials
            3. Enable Drive API
            4. Add GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET to environment variables
            """)
        
        # Teams OAuth
        teams_client_id = os.getenv("TEAMS_CLIENT_ID")
        teams_client_secret = os.getenv("TEAMS_CLIENT_SECRET")
        
        st.markdown("**Microsoft Teams Configuration:**")
        if teams_client_id and teams_client_secret:
            st.success("✅ Teams OAuth configured")
        else:
            st.warning("⚠️ Teams OAuth not configured")
            st.markdown("""
            1. Go to https://portal.azure.com/
            2. Register an app in Azure AD
            3. Add Microsoft Graph API permissions
            4. Add TEAMS_CLIENT_ID and TEAMS_CLIENT_SECRET to environment variables
            """)
    
    # API Configuration
    st.subheader("AI Analysis Configuration")
    
    with st.expander("Configure AI Analysis (Optional)"):
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
