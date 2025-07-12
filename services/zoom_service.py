import requests
import json
from datetime import datetime, timedelta
import streamlit as st
from services.auth_service import AuthService

class ZoomService:
    def __init__(self):
        self.auth_service = AuthService()
        self.base_url = "https://api.zoom.us/v2"
        
    def get_recent_recordings(self, days_back=7):
        """Get recent cloud recordings from Zoom"""
        try:
            token = self.auth_service.get_token('zoom')
            if not token:
                st.error("Not authenticated with Zoom")
                return []
                
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            # Get recordings from the last N days
            from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            to_date = datetime.now().strftime('%Y-%m-%d')
            
            url = f"{self.base_url}/users/me/recordings"
            params = {
                'from': from_date,
                'to': to_date,
                'page_size': 100
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                recordings = []
                
                for meeting in data.get('meetings', []):
                    for recording in meeting.get('recording_files', []):
                        if recording.get('file_type') == 'M4A':  # Audio only
                            recordings.append({
                                'id': recording.get('id'),
                                'topic': meeting.get('topic'),
                                'start_time': meeting.get('start_time'),
                                'duration': meeting.get('duration'),
                                'download_url': recording.get('download_url'),
                                'file_size': recording.get('file_size'),
                                'platform': 'zoom'
                            })
                
                return recordings
            else:
                st.error(f"Failed to fetch Zoom recordings: {response.status_code}")
                return []
                
        except Exception as e:
            st.error(f"Zoom service error: {str(e)}")
            return []
    
    def download_recording(self, recording_info):
        """Download a specific recording"""
        try:
            token = self.auth_service.get_token('zoom')
            if not token:
                return None
                
            headers = {
                'Authorization': f'Bearer {token}'
            }
            
            response = requests.get(
                recording_info['download_url'], 
                headers=headers, 
                stream=True
            )
            
            if response.status_code == 200:
                # Generate filename
                filename = f"zoom_recording_{recording_info['id']}.m4a"
                filepath = f"recordings/{filename}"
                
                # Create directory if it doesn't exist
                import os
                os.makedirs('recordings', exist_ok=True)
                
                # Save file
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                return filepath
            else:
                st.error(f"Failed to download recording: {response.status_code}")
                return None
                
        except Exception as e:
            st.error(f"Download error: {str(e)}")
            return None
    
    def get_meeting_details(self, meeting_id):
        """Get detailed information about a specific meeting"""
        try:
            token = self.auth_service.get_token('zoom')
            if not token:
                return None
                
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            url = f"{self.base_url}/meetings/{meeting_id}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            st.error(f"Failed to get meeting details: {str(e)}")
            return None
    
    def schedule_webhook(self, webhook_url):
        """Schedule webhook for automatic recording processing"""
        try:
            token = self.auth_service.get_token('zoom')
            if not token:
                return False
                
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            webhook_data = {
                'url': webhook_url,
                'auth_user': '',
                'auth_password': '',
                'events': ['recording.completed']
            }
            
            url = f"{self.base_url}/webhooks"
            response = requests.post(url, headers=headers, json=webhook_data)
            
            return response.status_code == 201
            
        except Exception as e:
            st.error(f"Webhook setup error: {str(e)}")
            return False
