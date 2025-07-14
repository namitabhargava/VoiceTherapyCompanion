# Therapeutic Assessment AI

## Overview

This is a full-stack Python application that provides voice-based therapeutic assessment using VAPI (Voice AI). The application allows users to upload therapy session audio files, transcribes them, analyzes the content using multiple therapeutic frameworks based on the expertise of 7 renowned psychologists, and provides interactive voice-based insights about therapy progress.

### Psychological Expertise Integration

The analysis system incorporates the combined expertise of:
- **Carl Rogers (1902-1987)**: Person-centered therapy focusing on empathy, unconditional positive regard, and genuineness
- **Sigmund Freud (1856-1939)**: Psychoanalysis exploring unconscious patterns and defense mechanisms
- **Albert Ellis (1913-2007)**: Rational Emotive Behavior Therapy (REBT) addressing irrational beliefs
- **Melanie Klein (1882-1960)**: Child therapy and object relations theory
- **Virginia Satir (1916-1988)**: Family systems therapy and communication patterns
- **Martin Seligman (b. 1942)**: Positive psychology and PERMA-V model for well-being
- **Aaron Beck (1921-2021)**: Cognitive therapy and cognitive behavioral therapy (CBT)

## User Preferences

Preferred communication style: Simple, everyday language.
Free alternatives preferred: User requested free alternatives to OpenAI for transcription and analysis.
User-friendly analysis: User requested analysis results in more user-friendly terms instead of technical jargon.
PDF upload support: User requested ability to upload PDF files for transcript analysis.
Enhanced negative detection: User requested better detection of when therapy is not working well, especially negative outcomes.
Privacy-focused: User requested uploaded files be deleted after analysis to ensure no sensitive data is permanently stored.
Expert therapist evaluation: User requested more accurate therapist analysis based on comprehensive therapeutic principles from leading psychologists.

## System Architecture

### Frontend Architecture
- **Streamlit-based web interface**: Main application built with Streamlit for rapid prototyping and deployment
- **Responsive design**: Uses Streamlit's native components with custom CSS styling
- **File upload interface**: Supports multiple audio formats (MP3, WAV, MP4, M4A, OGG, FLAC, AAC) and text formats (TXT, PDF)
- **PDF processing**: Automatic text extraction from PDF documents with preview functionality
- **Interactive dashboard**: Displays analysis results with charts and visualizations using Plotly
- **Multi-assessment display**: Shows comprehensive assessment results with reliability and validity indicators

### Backend Architecture
- **Service-oriented architecture**: Modular design with separate services for different functionalities
- **Multi-assessment framework**: Implements evidence-based assessment using multiple methods and sources
- **OpenAI integration**: Uses GPT-4 for analysis and Whisper for transcription
- **VAPI integration**: Voice AI service for interactive conversations about therapy sessions
- **OAuth integration**: Supports Zoom, Google Meet, and Microsoft Teams for direct recording access

### Data Storage Solutions
- **Local file system**: Sessions stored locally with encryption
- **JSON-based data**: Session metadata and analysis results stored as JSON
- **Encrypted storage**: Uses Fernet encryption for sensitive data protection
- **Session management**: Tracks therapy sessions over time with unique identifiers

## Key Components

### Core Services
1. **TranscriptionService**: Handles audio-to-text conversion using OpenAI Whisper
2. **AnalysisService**: Performs therapeutic analysis using multiple psychological frameworks with enhanced negative pattern detection and expert-level therapist evaluation
3. **MultiAssessmentService**: Implements evidence-based assessment using multiple methods and sources (unstructured interviews, structured interviews, behavioral observations, rating scales)
4. **VAPIService**: Manages voice interactions for asking questions about sessions
5. **SessionManager**: Handles session persistence and retrieval
6. **PDFService**: Generates downloadable progress reports
7. **FileHandler**: Processes different file types including PDF text extraction

### Expert Therapist Evaluation System
The system now includes comprehensive therapist assessment based on principles from 15+ leading therapeutic experts including:
- **Empathy & Attunement Assessment**: Measures active listening, emotional resonance, and psychological safety
- **Therapeutic Technique Analysis**: Identifies and evaluates specific therapeutic approaches (CBT, DBT, person-centered, etc.)
- **Burnout Detection**: Screens for signs of therapist disengagement, hopelessness, or lack of structure
- **Client Progress Monitoring**: Detects meaningful cognitive, emotional, and behavioral shifts
- **Therapist Fit Scoring**: Rates alignment with client needs and relational connection (1-10 scale)
- **Professional Recommendations**: Provides actionable guidance for clients about continuing or changing therapy

### Multi-Assessment Methodology
Following evidence-based practices from counseling assessment literature (Leppma & Jones), the system implements:
- **Multiple Assessment Methods**: Unstructured interviews, structured interviews, behavioral observations, therapeutic rating scales
- **Convergent Validity**: Cross-validation of findings across different assessment approaches
- **Reliability & Validity Indicators**: Systematic evaluation of assessment quality and trustworthiness
- **Clinical Recommendations**: Evidence-based guidance derived from comprehensive assessment
- **Assessment Limitations**: Transparent identification of methodological constraints and biases

### Authentication Services
- **AuthService**: Manages OAuth flows for video conferencing platforms
- **ZoomService**: Integrates with Zoom cloud recordings
- **GoogleMeetService**: Accesses Google Meet recordings via Drive API
- **TeamsService**: Retrieves Microsoft Teams recordings via Graph API

### Utility Components
- **AudioUtils**: Handles audio format conversion and optimization
- **SecurityUtils**: Provides encryption/decryption for sensitive data
- **Settings**: Manages application configuration and environment variables

## Data Flow

1. **Audio Input**: User uploads audio file or connects to video platform
2. **Audio Processing**: File is converted to optimal format for transcription
3. **Transcription**: Audio is transcribed using OpenAI Whisper API
4. **Analysis**: Transcript is analyzed using 7 therapeutic frameworks:
   - Emotional safety & relational depth (Rogers)
   - Unconscious pattern emergence (Freud, Klein)
   - Cognitive restructuring (Ellis, Beck)
   - Communication/family role changes (Satir)
   - Strengths and well-being (Seligman)
   - Narrative/identity coherence
   - Behavioral activation
5. **Storage**: Session data is encrypted and stored locally
6. **Voice Interaction**: User can ask questions via VAPI about their session
7. **Report Generation**: PDF reports can be generated for progress tracking

## External Dependencies

### APIs and Services (with Free Alternatives)
- **OpenAI API**: GPT-4 for analysis, Whisper for transcription (premium)
- **Hugging Face API**: Free tier available for both transcription and analysis
- **Google Speech Recognition**: Free transcription service (no API key needed)
- **Local Analysis**: Basic keyword-based analysis (completely free)
- **VAPI**: Voice AI service for interactive conversations (optional)
- **AssemblyAI**: Alternative transcription service (configurable)

### Platform Integrations
- **Zoom API**: Access to cloud recordings
- **Google Drive API**: Access to Google Meet recordings
- **Microsoft Graph API**: Access to Teams recordings

### Python Libraries
- **Streamlit**: Web application framework
- **OpenAI**: API client for OpenAI services
- **Plotly**: Data visualization and charts
- **ReportLab**: PDF generation
- **Cryptography**: Data encryption
- **PyDub**: Audio processing
- **Pandas**: Data manipulation

## Deployment Strategy

### Replit Deployment
- **Environment variables**: All API keys and secrets configured as Replit secrets
- **File persistence**: Uses Replit's file system for session storage
- **Auto-scaling**: Leverages Replit's automatic scaling capabilities

### Security Considerations
- **Data encryption**: All session data encrypted at rest
- **HIPAA compliance**: Follows healthcare data protection practices
- **OAuth security**: Secure token management for platform integrations
- **Session timeouts**: Configurable session expiration for security
- **File privacy**: Uploaded files automatically deleted after analysis to prevent sensitive data storage
- **Temporary processing**: Audio files saved to temp directory and cleaned up immediately after transcription

### Configuration Management
- **Environment-based config**: Uses environment variables for all sensitive data
- **Flexible settings**: Configurable analysis depth, retention policies, and feature toggles
- **Debug mode**: Configurable logging and error handling

The application is designed to be privacy-focused with local processing options and encrypted storage, making it suitable for therapeutic use cases while maintaining professional standards for healthcare data handling.