import os
import json
import requests
import streamlit as st
from datetime import datetime

class VAPIService:
    def __init__(self):
        self.api_key = os.getenv("VAPI_API_KEY")
        self.base_url = "https://api.vapi.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
    def start_voice_session(self, session_data):
        """Start a voice interaction session with VAPI"""
        try:
            if not self.api_key:
                st.error("VAPI API key not configured")
                return False
                
            # Prepare session context for the AI assistant
            context = self._prepare_session_context(session_data)
            
            # Create VAPI assistant configuration
            assistant_config = {
                "model": {
                    "provider": "openai",
                    "model": "gpt-4o",
                    "systemMessage": self._get_system_message(context)
                },
                "voice": {
                    "provider": "11labs",
                    "voiceId": "rachel"  # Professional, warm voice
                },
                "firstMessage": "Hello! I'm here to help you reflect on your therapy session. You can ask me questions like 'Am I making progress?' or 'What themes came up today?' How can I assist you?",
                "endCallMessage": "Thank you for reflecting on your session. Take care!",
                "recordingEnabled": False,  # Privacy compliance
                "silenceTimeoutSeconds": 10,
                "maxDurationSeconds": 600  # 10 minutes max
            }
            
            # Create assistant
            response = requests.post(
                f"{self.base_url}/assistants",
                headers=self.headers,
                json=assistant_config
            )
            
            if response.status_code == 201:
                assistant_id = response.json()["id"]
                
                # Start call
                call_config = {
                    "assistantId": assistant_id,
                    "customer": {
                        "number": "+1234567890"  # This would be user's number in production
                    }
                }
                
                call_response = requests.post(
                    f"{self.base_url}/calls",
                    headers=self.headers,
                    json=call_config
                )
                
                if call_response.status_code == 201:
                    call_id = call_response.json()["id"]
                    st.success(f"Voice session started! Call ID: {call_id}")
                    return True
                else:
                    st.error(f"Failed to start call: {call_response.status_code}")
                    return False
                    
            else:
                st.error(f"Failed to create assistant: {response.status_code}")
                return False
                
        except Exception as e:
            st.error(f"VAPI service error: {str(e)}")
            return False
    
    def _prepare_session_context(self, session_data):
        """Prepare session context for the AI assistant"""
        try:
            # Extract key information from session analysis
            analysis = session_data.analysis
            
            context = {
                "session_date": session_data.timestamp.strftime("%Y-%m-%d"),
                "domain_scores": analysis.get("domain_scores", {}),
                "key_insights": analysis.get("key_insights", []),
                "recommendations": analysis.get("recommendations", []),
                "session_themes": analysis.get("session_themes", []),
                "progress_indicators": analysis.get("progress_indicators", [])
            }
            
            return context
            
        except Exception as e:
            st.error(f"Context preparation error: {str(e)}")
            return {}
    
    def _get_system_message(self, context):
        """Generate system message for the AI assistant"""
        system_message = f"""
        You are a compassionate therapeutic assistant helping a client reflect on their therapy session.
        
        Session Context:
        - Session Date: {context.get('session_date', 'Unknown')}
        - Domain Scores: {json.dumps(context.get('domain_scores', {}), indent=2)}
        - Key Insights: {json.dumps(context.get('key_insights', []), indent=2)}
        - Recommendations: {json.dumps(context.get('recommendations', []), indent=2)}
        - Session Themes: {json.dumps(context.get('session_themes', []), indent=2)}
        - Progress Indicators: {json.dumps(context.get('progress_indicators', []), indent=2)}
        
        Guidelines:
        1. Be warm, empathetic, and supportive
        2. Use therapeutic language informed by multiple approaches (Rogers, Freud, Beck, etc.)
        3. Focus on the client's strengths and progress
        4. Encourage self-reflection and insight
        5. Avoid giving direct advice; instead, guide the client to their own insights
        6. Keep responses concise but meaningful
        7. If asked about specific scores, explain them in accessible terms
        8. Maintain professional boundaries while being caring
        
        Common questions you might receive:
        - "Am I making progress in therapy?"
        - "What themes came up in today's session?"
        - "How am I doing with my emotional safety?"
        - "What should I focus on next?"
        
        Always respond with empathy and refer to the specific session data when relevant.
        """
        
        return system_message
    
    def get_call_transcript(self, call_id):
        """Get transcript of a voice interaction"""
        try:
            response = requests.get(
                f"{self.base_url}/calls/{call_id}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                call_data = response.json()
                return call_data.get("transcript", "")
            else:
                st.error(f"Failed to get call transcript: {response.status_code}")
                return ""
                
        except Exception as e:
            st.error(f"Transcript retrieval error: {str(e)}")
            return ""
    
    def create_phone_number_assistant(self, session_data):
        """Create a phone number that clients can call for voice queries"""
        try:
            if not self.api_key:
                st.error("VAPI API key not configured")
                return None
                
            # Prepare context
            context = self._prepare_session_context(session_data)
            
            # Create phone number with assistant
            phone_config = {
                "provider": "twilio",
                "assistant": {
                    "model": {
                        "provider": "openai",
                        "model": "gpt-4o",
                        "systemMessage": self._get_system_message(context)
                    },
                    "voice": {
                        "provider": "11labs",
                        "voiceId": "rachel"
                    },
                    "firstMessage": "Hello! I'm your therapeutic reflection assistant. I'm here to help you think about your recent therapy session. What would you like to explore?",
                    "recordingEnabled": False,
                    "silenceTimeoutSeconds": 10,
                    "maxDurationSeconds": 600
                }
            }
            
            response = requests.post(
                f"{self.base_url}/phone-numbers",
                headers=self.headers,
                json=phone_config
            )
            
            if response.status_code == 201:
                phone_data = response.json()
                return phone_data.get("number")
            else:
                st.error(f"Failed to create phone number: {response.status_code}")
                return None
                
        except Exception as e:
            st.error(f"Phone number creation error: {str(e)}")
            return None
    
    def get_voice_analytics(self, call_id):
        """Get analytics from a voice interaction"""
        try:
            response = requests.get(
                f"{self.base_url}/calls/{call_id}/analytics",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {}
                
        except Exception as e:
            st.error(f"Analytics retrieval error: {str(e)}")
            return {}
    
    def end_voice_session(self, call_id):
        """End an active voice session"""
        try:
            response = requests.post(
                f"{self.base_url}/calls/{call_id}/end",
                headers=self.headers
            )
            
            return response.status_code == 200
            
        except Exception as e:
            st.error(f"Session ending error: {str(e)}")
            return False
