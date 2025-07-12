import os
from typing import Dict, Any
import streamlit as st

class Settings:
    """Application settings and configuration"""
    
    def __init__(self):
        self.load_settings()
    
    def load_settings(self):
        """Load application settings from environment and defaults"""
        
        # API Configuration
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
        self.VAPI_API_KEY = os.getenv("VAPI_API_KEY", "")
        self.ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY", "")
        
        # OAuth Configuration
        self.ZOOM_CLIENT_ID = os.getenv("ZOOM_CLIENT_ID", "")
        self.ZOOM_CLIENT_SECRET = os.getenv("ZOOM_CLIENT_SECRET", "")
        self.GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
        self.GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
        self.TEAMS_CLIENT_ID = os.getenv("TEAMS_CLIENT_ID", "")
        self.TEAMS_CLIENT_SECRET = os.getenv("TEAMS_CLIENT_SECRET", "")
        
        # Application Configuration
        self.APP_NAME = os.getenv("APP_NAME", "Therapeutic Assessment AI")
        self.APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
        self.DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"
        
        # File Storage Configuration
        self.MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "100"))
        self.SUPPORTED_AUDIO_FORMATS = os.getenv("SUPPORTED_AUDIO_FORMATS", "mp3,wav,mp4,m4a,ogg,flac,aac").split(",")
        self.AUTO_DELETE_AUDIO = os.getenv("AUTO_DELETE_AUDIO", "False").lower() == "true"
        self.RETENTION_DAYS = int(os.getenv("RETENTION_DAYS", "30"))
        
        # Analysis Configuration
        self.ANALYSIS_DEPTH = os.getenv("ANALYSIS_DEPTH", "detailed")  # standard, detailed, comprehensive
        self.ENABLE_SPEAKER_DIARIZATION = os.getenv("ENABLE_SPEAKER_DIARIZATION", "True").lower() == "true"
        self.TRANSCRIPTION_LANGUAGE = os.getenv("TRANSCRIPTION_LANGUAGE", "en")
        
        # Voice Configuration
        self.VOICE_PROVIDER = os.getenv("VOICE_PROVIDER", "11labs")
        self.VOICE_ID = os.getenv("VOICE_ID", "rachel")
        self.VOICE_SESSION_TIMEOUT = int(os.getenv("VOICE_SESSION_TIMEOUT", "600"))  # 10 minutes
        
        # Security Configuration
        self.ENABLE_ENCRYPTION = os.getenv("ENABLE_ENCRYPTION", "True").lower() == "true"
        self.SESSION_TIMEOUT_HOURS = int(os.getenv("SESSION_TIMEOUT_HOURS", "24"))
        self.ENABLE_AUDIT_LOGGING = os.getenv("ENABLE_AUDIT_LOGGING", "True").lower() == "true"
        
        # HIPAA Compliance Configuration
        self.HIPAA_COMPLIANCE_MODE = os.getenv("HIPAA_COMPLIANCE_MODE", "True").lower() == "true"
        self.LOCAL_PROCESSING_ONLY = os.getenv("LOCAL_PROCESSING_ONLY", "False").lower() == "true"
        self.AUTOMATIC_DATA_PURGE = os.getenv("AUTOMATIC_DATA_PURGE", "True").lower() == "true"
        
        # Therapeutic Framework Configuration
        self.ENABLED_FRAMEWORKS = os.getenv("ENABLED_FRAMEWORKS", "rogers,freud,beck,satir,seligman,narrative,behavioral").split(",")
        self.SCORING_SCALE = int(os.getenv("SCORING_SCALE", "10"))
        self.MINIMUM_SESSION_DURATION = int(os.getenv("MINIMUM_SESSION_DURATION", "300"))  # 5 minutes
        
        # Notification Configuration
        self.ENABLE_NOTIFICATIONS = os.getenv("ENABLE_NOTIFICATIONS", "True").lower() == "true"
        self.NOTIFICATION_EMAIL = os.getenv("NOTIFICATION_EMAIL", "")
        
        # Report Configuration
        self.DEFAULT_REPORT_FORMAT = os.getenv("DEFAULT_REPORT_FORMAT", "pdf")
        self.INCLUDE_TRANSCRIPT_IN_REPORT = os.getenv("INCLUDE_TRANSCRIPT_IN_REPORT", "False").lower() == "true"
        self.REPORT_BRANDING = os.getenv("REPORT_BRANDING", "True").lower() == "true"
        
        # Performance Configuration
        self.CONCURRENT_PROCESSING_LIMIT = int(os.getenv("CONCURRENT_PROCESSING_LIMIT", "5"))
        self.CACHE_DURATION_HOURS = int(os.getenv("CACHE_DURATION_HOURS", "24"))
        
        # Webhook Configuration
        self.WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
        self.WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")
        
        # Platform-specific Configuration
        self.ZOOM_WEBHOOK_URL = os.getenv("ZOOM_WEBHOOK_URL", "")
        self.GOOGLE_WEBHOOK_URL = os.getenv("GOOGLE_WEBHOOK_URL", "")
        self.TEAMS_WEBHOOK_URL = os.getenv("TEAMS_WEBHOOK_URL", "")
        
        # Development Configuration
        self.MOCK_APIS = os.getenv("MOCK_APIS", "False").lower() == "true"
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        
    def get_api_status(self) -> Dict[str, bool]:
        """Get status of required APIs"""
        return {
            "OpenAI": bool(self.OPENAI_API_KEY),
            "VAPI": bool(self.VAPI_API_KEY),
            "AssemblyAI": bool(self.ASSEMBLYAI_API_KEY),
            "Zoom": bool(self.ZOOM_CLIENT_ID and self.ZOOM_CLIENT_SECRET),
            "Google": bool(self.GOOGLE_CLIENT_ID and self.GOOGLE_CLIENT_SECRET),
            "Teams": bool(self.TEAMS_CLIENT_ID and self.TEAMS_CLIENT_SECRET)
        }
    
    def get_therapeutic_frameworks(self) -> Dict[str, Dict[str, Any]]:
        """Get therapeutic framework configurations"""
        frameworks = {
            "rogers": {
                "name": "Person-Centered Approach",
                "theorist": "Carl Rogers",
                "description": "Empathy, genuineness, and unconditional positive regard",
                "enabled": "rogers" in self.ENABLED_FRAMEWORKS
            },
            "freud": {
                "name": "Psychodynamic Approach",
                "theorist": "Freud & Klein",
                "description": "Unconscious patterns and symbolic processing",
                "enabled": "freud" in self.ENABLED_FRAMEWORKS
            },
            "beck": {
                "name": "Cognitive Behavioral Approach",
                "theorist": "Ellis & Beck",
                "description": "Cognitive restructuring and irrational thought detection",
                "enabled": "beck" in self.ENABLED_FRAMEWORKS
            },
            "satir": {
                "name": "Family Systems Approach",
                "theorist": "Virginia Satir",
                "description": "Family dynamics and communication patterns",
                "enabled": "satir" in self.ENABLED_FRAMEWORKS
            },
            "seligman": {
                "name": "Positive Psychology",
                "theorist": "Martin Seligman",
                "description": "Strengths, well-being, and PERMA model",
                "enabled": "seligman" in self.ENABLED_FRAMEWORKS
            },
            "narrative": {
                "name": "Narrative Therapy",
                "theorist": "Narrative Approach",
                "description": "Life story coherence and identity development",
                "enabled": "narrative" in self.ENABLED_FRAMEWORKS
            },
            "behavioral": {
                "name": "Behavioral Activation",
                "theorist": "Behavioral Therapy",
                "description": "Real-world application and behavior change",
                "enabled": "behavioral" in self.ENABLED_FRAMEWORKS
            }
        }
        
        return frameworks
    
    def get_file_storage_config(self) -> Dict[str, Any]:
        """Get file storage configuration"""
        return {
            "max_file_size_mb": self.MAX_FILE_SIZE_MB,
            "supported_formats": self.SUPPORTED_AUDIO_FORMATS,
            "auto_delete": self.AUTO_DELETE_AUDIO,
            "retention_days": self.RETENTION_DAYS,
            "local_processing_only": self.LOCAL_PROCESSING_ONLY
        }
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration"""
        return {
            "encryption_enabled": self.ENABLE_ENCRYPTION,
            "session_timeout_hours": self.SESSION_TIMEOUT_HOURS,
            "audit_logging": self.ENABLE_AUDIT_LOGGING,
            "hipaa_compliance": self.HIPAA_COMPLIANCE_MODE,
            "automatic_purge": self.AUTOMATIC_DATA_PURGE
        }
    
    def get_analysis_config(self) -> Dict[str, Any]:
        """Get analysis configuration"""
        return {
            "depth": self.ANALYSIS_DEPTH,
            "speaker_diarization": self.ENABLE_SPEAKER_DIARIZATION,
            "language": self.TRANSCRIPTION_LANGUAGE,
            "frameworks": self.ENABLED_FRAMEWORKS,
            "scoring_scale": self.SCORING_SCALE,
            "minimum_duration": self.MINIMUM_SESSION_DURATION
        }
    
    def get_voice_config(self) -> Dict[str, Any]:
        """Get voice interaction configuration"""
        return {
            "provider": self.VOICE_PROVIDER,
            "voice_id": self.VOICE_ID,
            "session_timeout": self.VOICE_SESSION_TIMEOUT,
            "enabled": bool(self.VAPI_API_KEY)
        }
    
    def validate_configuration(self) -> Dict[str, str]:
        """Validate configuration and return any issues"""
        issues = []
        
        # Check required API keys
        if not self.OPENAI_API_KEY:
            issues.append("OpenAI API key is required for transcription and analysis")
        
        if not self.VAPI_API_KEY:
            issues.append("VAPI API key is required for voice interactions")
        
        # Check OAuth configuration
        if not (self.ZOOM_CLIENT_ID and self.ZOOM_CLIENT_SECRET):
            issues.append("Zoom OAuth credentials are incomplete")
        
        # Check file storage limits
        if self.MAX_FILE_SIZE_MB < 1:
            issues.append("Maximum file size must be at least 1MB")
        
        if self.RETENTION_DAYS < 1:
            issues.append("Retention period must be at least 1 day")
        
        # Check analysis configuration
        if self.ANALYSIS_DEPTH not in ["standard", "detailed", "comprehensive"]:
            issues.append("Analysis depth must be 'standard', 'detailed', or 'comprehensive'")
        
        if not self.ENABLED_FRAMEWORKS:
            issues.append("At least one therapeutic framework must be enabled")
        
        # Check voice configuration
        if self.VOICE_SESSION_TIMEOUT < 60:
            issues.append("Voice session timeout must be at least 60 seconds")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }
    
    def get_environment_info(self) -> Dict[str, Any]:
        """Get environment information for debugging"""
        return {
            "app_name": self.APP_NAME,
            "app_version": self.APP_VERSION,
            "debug_mode": self.DEBUG_MODE,
            "python_version": os.sys.version,
            "streamlit_version": st.__version__,
            "api_status": self.get_api_status(),
            "configuration_valid": self.validate_configuration()["valid"]
        }
    
    def export_config(self) -> Dict[str, Any]:
        """Export non-sensitive configuration for backup"""
        return {
            "app_settings": {
                "name": self.APP_NAME,
                "version": self.APP_VERSION,
                "debug_mode": self.DEBUG_MODE
            },
            "file_storage": self.get_file_storage_config(),
            "analysis": self.get_analysis_config(),
            "voice": {
                "provider": self.VOICE_PROVIDER,
                "voice_id": self.VOICE_ID,
                "session_timeout": self.VOICE_SESSION_TIMEOUT
            },
            "security": {
                "encryption_enabled": self.ENABLE_ENCRYPTION,
                "session_timeout_hours": self.SESSION_TIMEOUT_HOURS,
                "audit_logging": self.ENABLE_AUDIT_LOGGING,
                "hipaa_compliance": self.HIPAA_COMPLIANCE_MODE
            },
            "frameworks": self.get_therapeutic_frameworks(),
            "reports": {
                "default_format": self.DEFAULT_REPORT_FORMAT,
                "include_transcript": self.INCLUDE_TRANSCRIPT_IN_REPORT,
                "branding": self.REPORT_BRANDING
            }
        }
    
    def update_setting(self, key: str, value: Any):
        """Update a configuration setting"""
        if hasattr(self, key):
            setattr(self, key, value)
            return True
        return False
    
    def get_display_settings(self) -> Dict[str, Any]:
        """Get settings for display in the UI"""
        return {
            "API Configuration": {
                "OpenAI API": "✅ Configured" if self.OPENAI_API_KEY else "❌ Not configured",
                "VAPI API": "✅ Configured" if self.VAPI_API_KEY else "❌ Not configured",
                "AssemblyAI API": "✅ Configured" if self.ASSEMBLYAI_API_KEY else "❌ Not configured"
            },
            "Platform Integration": {
                "Zoom": "✅ Configured" if (self.ZOOM_CLIENT_ID and self.ZOOM_CLIENT_SECRET) else "❌ Not configured",
                "Google Meet": "✅ Configured" if (self.GOOGLE_CLIENT_ID and self.GOOGLE_CLIENT_SECRET) else "❌ Not configured",
                "Microsoft Teams": "✅ Configured" if (self.TEAMS_CLIENT_ID and self.TEAMS_CLIENT_SECRET) else "❌ Not configured"
            },
            "Analysis Settings": {
                "Analysis Depth": self.ANALYSIS_DEPTH.title(),
                "Speaker Diarization": "✅ Enabled" if self.ENABLE_SPEAKER_DIARIZATION else "❌ Disabled",
                "Enabled Frameworks": len(self.ENABLED_FRAMEWORKS)
            },
            "Security & Privacy": {
                "Encryption": "✅ Enabled" if self.ENABLE_ENCRYPTION else "❌ Disabled",
                "HIPAA Compliance": "✅ Enabled" if self.HIPAA_COMPLIANCE_MODE else "❌ Disabled",
                "Audit Logging": "✅ Enabled" if self.ENABLE_AUDIT_LOGGING else "❌ Disabled"
            }
        }
