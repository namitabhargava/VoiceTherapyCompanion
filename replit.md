# Therapeutic Assessment AI

## Overview

This is a full-stack Python application that provides voice-based therapeutic assessment using VAPI (Voice AI). The application allows users to upload therapy session audio files, transcribes them, analyzes the content using multiple therapeutic frameworks, and provides interactive voice-based insights about therapy progress.

## User Preferences

Preferred communication style: Simple, everyday language.
Free alternatives preferred: User requested free alternatives to OpenAI for transcription and analysis.

## System Architecture

### Frontend Architecture
- **Streamlit-based web interface**: Main application built with Streamlit for rapid prototyping and deployment
- **Responsive design**: Uses Streamlit's native components with custom CSS styling
- **File upload interface**: Supports multiple audio formats (MP3, WAV, MP4, M4A, OGG, FLAC, AAC)
- **Interactive dashboard**: Displays analysis results with charts and visualizations using Plotly

### Backend Architecture
- **Service-oriented architecture**: Modular design with separate services for different functionalities
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
2. **AnalysisService**: Performs therapeutic analysis using multiple psychological frameworks
3. **VAPIService**: Manages voice interactions for asking questions about sessions
4. **SessionManager**: Handles session persistence and retrieval
5. **PDFService**: Generates downloadable progress reports

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

### Configuration Management
- **Environment-based config**: Uses environment variables for all sensitive data
- **Flexible settings**: Configurable analysis depth, retention policies, and feature toggles
- **Debug mode**: Configurable logging and error handling

The application is designed to be privacy-focused with local processing options and encrypted storage, making it suitable for therapeutic use cases while maintaining professional standards for healthcare data handling.