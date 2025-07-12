import requests
import json
from datetime import datetime, timedelta
import streamlit as st
from services.auth_service import AuthService

class TeamsService:
    def __init__(self):
        self.auth_service = AuthService()
        self.base_url = "https://graph.microsoft.com/v1.0"
        
    def get_recent_recordings(self, days_back=7):
        """Get recent Teams recordings via Graph API"""
        try:
            token = self.auth_service.get_token('teams')
            if not token:
                st.error("Not authenticated with Teams")
                return []
                
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            # Get recordings from OneDrive/SharePoint
            # Teams recordings are typically stored in the "Recordings" folder
            
            # First, get the user's OneDrive
            url = f"{self.base_url}/me/drive/root/children"
            params = {
                '$filter': "name eq 'Recordings'"
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                recordings_folder = None
                
                for item in data.get('value', []):
                    if item.get('name') == 'Recordings':
                        recordings_folder = item
                        break
                
                if recordings_folder:
                    return self._get_recordings_from_folder(recordings_folder['id'], days_back)
                else:
                    st.info("No Teams recordings folder found")
                    return []
            else:
                st.error(f"Failed to access OneDrive: {response.status_code}")
                return []
                
        except Exception as e:
            st.error(f"Teams service error: {str(e)}")
            return []
    
    def _get_recordings_from_folder(self, folder_id, days_back):
        """Get recordings from specific folder"""
        try:
            token = self.auth_service.get_token('teams')
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            url = f"{self.base_url}/me/drive/items/{folder_id}/children"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                recordings = []
                
                cutoff_date = datetime.now() - timedelta(days=days_back)
                
                for item in data.get('value', []):
                    if item.get('file') and any(ext in item.get('name', '').lower() 
                                              for ext in ['.mp4', '.m4v', '.mov']):
                        created_time = datetime.fromisoformat(
                            item.get('createdDateTime', '').replace('Z', '+00:00')
                        )
                        
                        if created_time >= cutoff_date:
                            recordings.append({
                                'id': item.get('id'),
                                'name': item.get('name'),
                                'created_time': item.get('createdDateTime'),
                                'size': item.get('size'),
                                'download_url': item.get('@microsoft.graph.downloadUrl'),
                                'platform': 'teams'
                            })
                
                return recordings
            else:
                return []
                
        except Exception as e:
            st.error(f"Folder access error: {str(e)}")
            return []
    
    def download_recording(self, recording_info):
        """Download a specific Teams recording"""
        try:
            if not recording_info.get('download_url'):
                st.error("No download URL available")
                return None
                
            response = requests.get(recording_info['download_url'], stream=True)
            
            if response.status_code == 200:
                # Generate filename
                filename = f"teams_recording_{recording_info['id']}.mp4"
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
        """Get meeting details from Teams"""
        try:
            token = self.auth_service.get_token('teams')
            if not token:
                return None
                
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            url = f"{self.base_url}/me/onlineMeetings/{meeting_id}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            st.error(f"Failed to get meeting details: {str(e)}")
            return None
    
    def setup_webhook(self, webhook_url):
        """Setup webhook for Teams recording notifications"""
        try:
            token = self.auth_service.get_token('teams')
            if not token:
                return False
                
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            subscription_data = {
                'changeType': 'created,updated',
                'notificationUrl': webhook_url,
                'resource': '/me/drive/root/children',
                'expirationDateTime': (datetime.now() + timedelta(hours=1)).isoformat(),
                'clientState': 'teams-recordings-webhook'
            }
            
            url = f"{self.base_url}/subscriptions"
            response = requests.post(url, headers=headers, json=subscription_data)
            
            return response.status_code == 201
            
        except Exception as e:
            st.error(f"Webhook setup error: {str(e)}")
            return False
