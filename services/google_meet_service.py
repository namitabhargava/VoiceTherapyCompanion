import requests
import json
from datetime import datetime, timedelta
import streamlit as st
from services.auth_service import AuthService

class GoogleMeetService:
    def __init__(self):
        self.auth_service = AuthService()
        self.base_url = "https://www.googleapis.com/drive/v3"
        
    def get_recent_recordings(self, days_back=7):
        """Get recent Google Meet recordings from Drive"""
        try:
            token = self.auth_service.get_token('google')
            if not token:
                st.error("Not authenticated with Google")
                return []
                
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            # Search for Meet recordings in Drive
            # Google Meet recordings are typically stored in a "Meet Recordings" folder
            query = "name contains 'Meet' and mimeType contains 'video' or mimeType contains 'audio'"
            
            url = f"{self.base_url}/files"
            params = {
                'q': query,
                'pageSize': 100,
                'fields': 'files(id,name,size,createdTime,webContentLink,mimeType)'
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                recordings = []
                
                cutoff_date = datetime.now() - timedelta(days=days_back)
                
                for file in data.get('files', []):
                    created_time = datetime.fromisoformat(
                        file.get('createdTime', '').replace('Z', '+00:00')
                    )
                    
                    if created_time >= cutoff_date:
                        recordings.append({
                            'id': file.get('id'),
                            'name': file.get('name'),
                            'created_time': file.get('createdTime'),
                            'size': file.get('size'),
                            'download_url': file.get('webContentLink'),
                            'mime_type': file.get('mimeType'),
                            'platform': 'google_meet'
                        })
                
                return recordings
            else:
                st.error(f"Failed to fetch Google Meet recordings: {response.status_code}")
                return []
                
        except Exception as e:
            st.error(f"Google Meet service error: {str(e)}")
            return []
    
    def download_recording(self, recording_info):
        """Download a specific Google Meet recording"""
        try:
            token = self.auth_service.get_token('google')
            if not token:
                return None
                
            headers = {
                'Authorization': f'Bearer {token}'
            }
            
            # Get file content
            url = f"{self.base_url}/files/{recording_info['id']}"
            params = {'alt': 'media'}
            
            response = requests.get(url, headers=headers, params=params, stream=True)
            
            if response.status_code == 200:
                # Generate filename
                filename = f"meet_recording_{recording_info['id']}.mp4"
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
    
    def get_folder_recordings(self, folder_id):
        """Get recordings from a specific folder"""
        try:
            token = self.auth_service.get_token('google')
            if not token:
                return []
                
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            query = f"'{folder_id}' in parents and (mimeType contains 'video' or mimeType contains 'audio')"
            
            url = f"{self.base_url}/files"
            params = {
                'q': query,
                'pageSize': 100,
                'fields': 'files(id,name,size,createdTime,webContentLink,mimeType)'
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('files', [])
            else:
                return []
                
        except Exception as e:
            st.error(f"Folder search error: {str(e)}")
            return []
    
    def create_webhook(self, webhook_url):
        """Create webhook for Drive changes (for automatic detection)"""
        try:
            token = self.auth_service.get_token('google')
            if not token:
                return False
                
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            webhook_data = {
                'id': 'meet-recordings-webhook',
                'type': 'web_hook',
                'address': webhook_url,
                'payload': True
            }
            
            url = f"{self.base_url}/files/watch"
            response = requests.post(url, headers=headers, json=webhook_data)
            
            return response.status_code == 200
            
        except Exception as e:
            st.error(f"Webhook creation error: {str(e)}")
            return False
