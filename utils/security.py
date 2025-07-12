import os
import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import streamlit as st

class SecurityUtils:
    """Security utilities for data encryption and HIPAA compliance"""
    
    def __init__(self):
        self.encryption_key = self._get_or_create_key()
        self.fernet = Fernet(self.encryption_key)
    
    def _get_or_create_key(self):
        """Get or create encryption key"""
        try:
            # Try to load existing key
            key_file = 'encryption.key'
            if os.path.exists(key_file):
                with open(key_file, 'rb') as f:
                    return f.read()
            
            # Generate new key if none exists
            password = os.getenv('ENCRYPTION_PASSWORD', 'default_therapeutic_key_2024').encode()
            salt = os.getenv('ENCRYPTION_SALT', 'therapeutic_salt_2024').encode()
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password))
            
            # Save key for future use
            with open(key_file, 'wb') as f:
                f.write(key)
            
            return key
            
        except Exception as e:
            st.error(f"Encryption key generation error: {str(e)}")
            # Fallback to simple key generation
            return Fernet.generate_key()
    
    def encrypt_data(self, data: str) -> bytes:
        """Encrypt sensitive data"""
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            return self.fernet.encrypt(data)
        except Exception as e:
            st.error(f"Encryption error: {str(e)}")
            return data.encode('utf-8') if isinstance(data, str) else data
    
    def decrypt_data(self, encrypted_data: bytes) -> str:
        """Decrypt sensitive data"""
        try:
            decrypted = self.fernet.decrypt(encrypted_data)
            return decrypted.decode('utf-8')
        except Exception as e:
            st.error(f"Decryption error: {str(e)}")
            return encrypted_data.decode('utf-8') if isinstance(encrypted_data, bytes) else str(encrypted_data)
    
    def hash_data(self, data: str) -> str:
        """Create hash for data integrity"""
        try:
            return hashlib.sha256(data.encode('utf-8')).hexdigest()
        except Exception as e:
            st.error(f"Hashing error: {str(e)}")
            return data
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for secure storage"""
        try:
            # Remove potentially dangerous characters
            import re
            sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
            # Limit length
            sanitized = sanitized[:100]
            # Ensure it's not empty
            if not sanitized:
                sanitized = 'unnamed_file'
            return sanitized
        except Exception as e:
            st.error(f"Filename sanitization error: {str(e)}")
            return 'safe_filename'
    
    def validate_file_type(self, filename: str, allowed_types: list) -> bool:
        """Validate file type for security"""
        try:
            file_extension = filename.lower().split('.')[-1]
            return file_extension in allowed_types
        except Exception as e:
            st.error(f"File validation error: {str(e)}")
            return False
    
    def secure_delete_file(self, filepath: str):
        """Securely delete file (overwrite before deletion)"""
        try:
            if os.path.exists(filepath):
                # Get file size
                file_size = os.path.getsize(filepath)
                
                # Overwrite with random data
                with open(filepath, 'rb+') as f:
                    f.write(os.urandom(file_size))
                    f.flush()
                    os.fsync(f.fileno())
                
                # Delete file
                os.remove(filepath)
                
        except Exception as e:
            st.error(f"Secure deletion error: {str(e)}")
            # Fallback to regular deletion
            try:
                os.remove(filepath)
            except:
                pass
    
    def check_data_integrity(self, data: str, expected_hash: str) -> bool:
        """Check data integrity using hash"""
        try:
            actual_hash = self.hash_data(data)
            return actual_hash == expected_hash
        except Exception as e:
            st.error(f"Integrity check error: {str(e)}")
            return False
    
    def generate_session_token(self, user_id: str = None) -> str:
        """Generate secure session token"""
        try:
            import secrets
            import time
            
            # Create token with timestamp and random data
            timestamp = str(int(time.time()))
            random_data = secrets.token_hex(16)
            user_part = user_id[:8] if user_id else 'anonymous'
            
            token_data = f"{timestamp}:{user_part}:{random_data}"
            return base64.urlsafe_b64encode(token_data.encode()).decode()
            
        except Exception as e:
            st.error(f"Token generation error: {str(e)}")
            return base64.urlsafe_b64encode(os.urandom(32)).decode()
    
    def validate_session_token(self, token: str, max_age_hours: int = 24) -> bool:
        """Validate session token"""
        try:
            import time
            
            # Decode token
            token_data = base64.urlsafe_b64decode(token).decode()
            parts = token_data.split(':')
            
            if len(parts) != 3:
                return False
            
            timestamp = int(parts[0])
            current_time = int(time.time())
            
            # Check if token is expired
            if current_time - timestamp > max_age_hours * 3600:
                return False
            
            return True
            
        except Exception as e:
            st.error(f"Token validation error: {str(e)}")
            return False
    
    def audit_log(self, action: str, details: dict = None):
        """Create audit log entry for HIPAA compliance"""
        try:
            import json
            from datetime import datetime
            
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'action': action,
                'details': details or {},
                'session_id': st.session_state.get('session_id', 'unknown')
            }
            
            # Create logs directory if it doesn't exist
            os.makedirs('logs', exist_ok=True)
            
            # Append to audit log
            log_file = f"logs/audit_{datetime.now().strftime('%Y%m')}.log"
            with open(log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
                
        except Exception as e:
            st.error(f"Audit logging error: {str(e)}")
    
    def clean_sensitive_data(self, data: str) -> str:
        """Remove or mask sensitive information from data"""
        try:
            import re
            
            # Remove potential phone numbers
            data = re.sub(r'\b\d{3}-\d{3}-\d{4}\b', '[PHONE]', data)
            data = re.sub(r'\b\(\d{3}\)\s*\d{3}-\d{4}\b', '[PHONE]', data)
            
            # Remove potential email addresses
            data = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', data)
            
            # Remove potential SSNs
            data = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', data)
            
            # Remove potential credit card numbers
            data = re.sub(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', '[CARD]', data)
            
            return data
            
        except Exception as e:
            st.error(f"Data cleaning error: {str(e)}")
            return data
    
    def get_security_headers(self) -> dict:
        """Get security headers for API requests"""
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
        }
