import os
import json
import pickle
from datetime import datetime
from typing import List, Dict, Any
import streamlit as st
from models.session_data import SessionData
from utils.security import SecurityUtils

class SessionManager:
    def __init__(self):
        self.security = SecurityUtils()
        self.sessions_dir = "sessions"
        self.settings_file = "settings.json"
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure required directories exist"""
        directories = [self.sessions_dir, "recordings", "reports", "temp"]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def save_session(self, session_data: SessionData) -> str:
        """Save session data securely"""
        try:
            # Generate unique session ID
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Prepare session data for storage
            session_dict = {
                'id': session_id,
                'timestamp': session_data.timestamp.isoformat(),
                'file_path': session_data.file_path,
                'transcript': session_data.transcript,
                'analysis': session_data.analysis,
                'platform': getattr(session_data, 'platform', 'manual'),
                'metadata': getattr(session_data, 'metadata', {})
            }
            
            # Encrypt sensitive data
            encrypted_data = self.security.encrypt_data(json.dumps(session_dict))
            
            # Save to file
            session_file = os.path.join(self.sessions_dir, f"{session_id}.enc")
            with open(session_file, 'wb') as f:
                f.write(encrypted_data)
            
            # Update session index
            self._update_session_index(session_id, session_data.timestamp)
            
            st.success(f"Session saved successfully: {session_id}")
            return session_id
            
        except Exception as e:
            st.error(f"Failed to save session: {str(e)}")
            return None
    
    def load_session(self, session_id: str) -> SessionData:
        """Load session data"""
        try:
            session_file = os.path.join(self.sessions_dir, f"{session_id}.enc")
            
            if not os.path.exists(session_file):
                st.error(f"Session not found: {session_id}")
                return None
            
            # Read and decrypt data
            with open(session_file, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self.security.decrypt_data(encrypted_data)
            session_dict = json.loads(decrypted_data)
            
            # Reconstruct SessionData object
            session_data = SessionData(
                file_path=session_dict['file_path'],
                transcript=session_dict['transcript'],
                analysis=session_dict['analysis'],
                timestamp=datetime.fromisoformat(session_dict['timestamp'])
            )
            
            # Add additional attributes
            session_data.id = session_dict['id']
            session_data.platform = session_dict.get('platform', 'manual')
            session_data.metadata = session_dict.get('metadata', {})
            
            return session_data
            
        except Exception as e:
            st.error(f"Failed to load session: {str(e)}")
            return None
    
    def get_recent_sessions(self, limit: int = 10) -> List[SessionData]:
        """Get recent sessions"""
        try:
            session_index = self._load_session_index()
            
            # Sort by timestamp (most recent first)
            sorted_sessions = sorted(
                session_index.items(),
                key=lambda x: x[1]['timestamp'],
                reverse=True
            )
            
            sessions = []
            for session_id, _ in sorted_sessions[:limit]:
                session_data = self.load_session(session_id)
                if session_data:
                    sessions.append(session_data)
            
            return sessions
            
        except Exception as e:
            st.error(f"Failed to load recent sessions: {str(e)}")
            return []
    
    def get_all_sessions(self) -> List[SessionData]:
        """Get all sessions"""
        try:
            session_index = self._load_session_index()
            
            sessions = []
            for session_id in session_index.keys():
                session_data = self.load_session(session_id)
                if session_data:
                    sessions.append(session_data)
            
            # Sort by timestamp
            sessions.sort(key=lambda x: x.timestamp)
            
            return sessions
            
        except Exception as e:
            st.error(f"Failed to load all sessions: {str(e)}")
            return []
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        try:
            session_file = os.path.join(self.sessions_dir, f"{session_id}.enc")
            
            if os.path.exists(session_file):
                os.remove(session_file)
            
            # Remove from index
            session_index = self._load_session_index()
            if session_id in session_index:
                del session_index[session_id]
                self._save_session_index(session_index)
            
            st.success(f"Session deleted: {session_id}")
            return True
            
        except Exception as e:
            st.error(f"Failed to delete session: {str(e)}")
            return False
    
    def save_uploaded_file(self, uploaded_file) -> str:
        """Save uploaded audio file temporarily"""
        try:
            # Generate unique filename in temp directory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"temp_{timestamp}_{uploaded_file.name}"
            filepath = os.path.join("temp", filename)
            
            # Save file temporarily
            with open(filepath, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            
            return filepath
            
        except Exception as e:
            st.error(f"Failed to save uploaded file: {str(e)}")
            return None
    
    def cleanup_old_files(self, days_old: int = 30):
        """Clean up old session files"""
        try:
            cutoff_date = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
            
            session_index = self._load_session_index()
            sessions_to_delete = []
            
            for session_id, session_info in session_index.items():
                session_timestamp = datetime.fromisoformat(session_info['timestamp']).timestamp()
                if session_timestamp < cutoff_date:
                    sessions_to_delete.append(session_id)
            
            for session_id in sessions_to_delete:
                self.delete_session(session_id)
            
            st.info(f"Cleaned up {len(sessions_to_delete)} old sessions")
            
        except Exception as e:
            st.error(f"Cleanup error: {str(e)}")
    
    def cleanup_temp_files(self):
        """Clean up all temporary files"""
        try:
            temp_dir = "temp"
            if os.path.exists(temp_dir):
                for filename in os.listdir(temp_dir):
                    filepath = os.path.join(temp_dir, filename)
                    if os.path.isfile(filepath):
                        os.remove(filepath)
            
            st.info("Temporary files cleaned up for privacy")
            
        except Exception as e:
            st.warning(f"Could not clean up temporary files: {str(e)}")
    
    def export_sessions(self, session_ids: List[str] = None) -> str:
        """Export sessions to JSON file"""
        try:
            if session_ids is None:
                sessions = self.get_all_sessions()
            else:
                sessions = [self.load_session(sid) for sid in session_ids]
                sessions = [s for s in sessions if s is not None]
            
            export_data = []
            for session in sessions:
                export_data.append({
                    'id': getattr(session, 'id', 'unknown'),
                    'timestamp': session.timestamp.isoformat(),
                    'analysis': session.analysis,
                    'platform': getattr(session, 'platform', 'manual'),
                    'metadata': getattr(session, 'metadata', {})
                    # Note: transcript excluded for privacy
                })
            
            # Save export file
            export_filename = f"sessions_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            export_path = os.path.join("reports", export_filename)
            
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            return export_path
            
        except Exception as e:
            st.error(f"Export error: {str(e)}")
            return None
    
    def get_session_statistics(self) -> Dict[str, Any]:
        """Get session statistics"""
        try:
            sessions = self.get_all_sessions()
            
            if not sessions:
                return {}
            
            # Calculate statistics
            total_sessions = len(sessions)
            
            # Average scores by domain
            domain_scores = {}
            for session in sessions:
                scores = session.analysis.get('domain_scores', {})
                for domain, score in scores.items():
                    if domain not in domain_scores:
                        domain_scores[domain] = []
                    domain_scores[domain].append(score)
            
            avg_domain_scores = {
                domain: sum(scores) / len(scores)
                for domain, scores in domain_scores.items()
            }
            
            # Platform distribution
            platform_counts = {}
            for session in sessions:
                platform = getattr(session, 'platform', 'manual')
                platform_counts[platform] = platform_counts.get(platform, 0) + 1
            
            # Date range
            timestamps = [session.timestamp for session in sessions]
            date_range = {
                'earliest': min(timestamps).isoformat(),
                'latest': max(timestamps).isoformat()
            }
            
            return {
                'total_sessions': total_sessions,
                'average_domain_scores': avg_domain_scores,
                'platform_distribution': platform_counts,
                'date_range': date_range,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            st.error(f"Statistics error: {str(e)}")
            return {}
    
    def save_settings(self, settings: Dict[str, Any]):
        """Save application settings"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            
        except Exception as e:
            st.error(f"Settings save error: {str(e)}")
    
    def load_settings(self) -> Dict[str, Any]:
        """Load application settings"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            return {}
            
        except Exception as e:
            st.error(f"Settings load error: {str(e)}")
            return {}
    
    def _update_session_index(self, session_id: str, timestamp: datetime):
        """Update session index"""
        try:
            session_index = self._load_session_index()
            session_index[session_id] = {
                'timestamp': timestamp.isoformat(),
                'created': datetime.now().isoformat()
            }
            self._save_session_index(session_index)
            
        except Exception as e:
            st.error(f"Index update error: {str(e)}")
    
    def _load_session_index(self) -> Dict[str, Any]:
        """Load session index"""
        try:
            index_file = os.path.join(self.sessions_dir, "index.json")
            if os.path.exists(index_file):
                with open(index_file, 'r') as f:
                    return json.load(f)
            return {}
            
        except Exception as e:
            return {}
    
    def _save_session_index(self, session_index: Dict[str, Any]):
        """Save session index"""
        try:
            index_file = os.path.join(self.sessions_dir, "index.json")
            with open(index_file, 'w') as f:
                json.dump(session_index, f, indent=2)
                
        except Exception as e:
            st.error(f"Index save error: {str(e)}")
