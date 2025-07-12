import os
import json
import requests
import streamlit as st
from pydub import AudioSegment
from utils.audio_utils import AudioUtils

class TranscriptionService:
    def __init__(self):
        # Try OpenAI first, then fall back to free alternatives
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY")
        
        # Initialize OpenAI client only if API key exists
        self.openai_client = None
        if self.openai_api_key:
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=self.openai_api_key)
            except Exception as e:
                st.warning(f"OpenAI initialization failed: {str(e)}")
        
        self.audio_utils = AudioUtils()
        
        # Available transcription providers
        self.providers = {
            'openai': self._transcribe_with_openai,
            'huggingface': self._transcribe_with_huggingface,
            'local': self._transcribe_with_local_model
        }
        
    def transcribe_audio(self, audio_file_path):
        """Transcribe audio file using available providers"""
        try:
            # Convert audio to supported format if needed
            converted_path = self.audio_utils.convert_to_supported_format(audio_file_path)
            
            # Try providers in order of preference
            if self.openai_client:
                st.info("Using OpenAI Whisper for transcription...")
                result = self._transcribe_with_openai(converted_path)
                if result:
                    self._cleanup_temp_file(converted_path, audio_file_path)
                    return result
            
            if self.huggingface_api_key:
                st.info("Using Hugging Face for transcription...")
                result = self._transcribe_with_huggingface(converted_path)
                if result:
                    self._cleanup_temp_file(converted_path, audio_file_path)
                    return result
            
            # Fall back to local model
            st.info("Using local transcription model...")
            result = self._transcribe_with_local_model(converted_path)
            if result:
                self._cleanup_temp_file(converted_path, audio_file_path)
                return result
            
            st.error("All transcription methods failed. Please check your API keys or try a different audio file.")
            return None
            
        except Exception as e:
            st.error(f"Transcription error: {str(e)}")
            return None
    
    def _cleanup_temp_file(self, converted_path, original_path):
        """Clean up temporary converted file"""
        if converted_path != original_path and os.path.exists(converted_path):
            os.remove(converted_path)
    
    def _transcribe_with_openai(self, audio_file_path):
        """Transcribe using OpenAI Whisper"""
        try:
            if not self.openai_client:
                return None
                
            # Check file size (OpenAI has 25MB limit)
            file_size = os.path.getsize(audio_file_path)
            if file_size > 25 * 1024 * 1024:  # 25MB
                st.info("Large file detected, splitting into chunks...")
                return self._transcribe_large_file_openai(audio_file_path)
            
            # Transcribe with Whisper
            with open(audio_file_path, 'rb') as audio_file:
                response = self.openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="json",
                    language="en"
                )
            
            return response.text
            
        except Exception as e:
            st.warning(f"OpenAI transcription failed: {str(e)}")
            return None
    
    def _transcribe_with_huggingface(self, audio_file_path):
        """Transcribe using Hugging Face Whisper API (free tier available)"""
        try:
            if not self.huggingface_api_key:
                return None
                
            API_URL = "https://api-inference.huggingface.co/models/openai/whisper-large-v3"
            headers = {"Authorization": f"Bearer {self.huggingface_api_key}"}
            
            with open(audio_file_path, "rb") as f:
                data = f.read()
            
            # Send request to Hugging Face
            response = requests.post(API_URL, headers=headers, data=data)
            
            if response.status_code == 200:
                result = response.json()
                if 'text' in result:
                    return result['text']
                else:
                    st.warning("Unexpected response format from Hugging Face")
                    return None
            else:
                st.warning(f"Hugging Face API error: {response.status_code}")
                return None
                
        except Exception as e:
            st.warning(f"Hugging Face transcription failed: {str(e)}")
            return None
    
    def _transcribe_with_local_model(self, audio_file_path):
        """Transcribe using local speech recognition (completely free)"""
        try:
            import speech_recognition as sr
            
            # Initialize recognizer
            r = sr.Recognizer()
            
            # Convert audio to WAV if needed
            audio = AudioSegment.from_file(audio_file_path)
            wav_path = audio_file_path.rsplit('.', 1)[0] + '_temp.wav'
            audio.export(wav_path, format='wav')
            
            # Transcribe using Google's free API
            with sr.AudioFile(wav_path) as source:
                audio_data = r.record(source)
                
            # Try Google's free service first
            try:
                text = r.recognize_google(audio_data)
                os.remove(wav_path)
                return text
            except sr.UnknownValueError:
                st.warning("Could not understand audio")
                os.remove(wav_path)
                return None
            except sr.RequestError as e:
                st.warning(f"Google Speech Recognition service error: {e}")
                # Try offline recognition as fallback
                try:
                    text = r.recognize_sphinx(audio_data)
                    os.remove(wav_path)
                    return text
                except:
                    os.remove(wav_path)
                    return None
                    
        except ImportError:
            st.warning("Local transcription requires 'SpeechRecognition' package. Installing...")
            try:
                import subprocess
                subprocess.check_call(['pip', 'install', 'SpeechRecognition', 'pocketsphinx'])
                st.info("Please restart the application to use local transcription")
                return None
            except:
                st.error("Failed to install required packages for local transcription")
                return None
        except Exception as e:
            st.warning(f"Local transcription failed: {str(e)}")
            return None
    
    def _transcribe_large_file_openai(self, audio_file_path):
        """Transcribe large audio file by splitting it into chunks (OpenAI)"""
        try:
            # Load audio file
            audio = AudioSegment.from_file(audio_file_path)
            
            # Split into 10-minute chunks
            chunk_length = 10 * 60 * 1000  # 10 minutes in milliseconds
            chunks = []
            
            for i in range(0, len(audio), chunk_length):
                chunk = audio[i:i + chunk_length]
                chunks.append(chunk)
            
            # Transcribe each chunk
            transcriptions = []
            
            for i, chunk in enumerate(chunks):
                st.info(f"Transcribing chunk {i+1}/{len(chunks)}")
                
                # Save chunk temporarily
                chunk_path = f"temp_chunk_{i}.wav"
                chunk.export(chunk_path, format="wav")
                
                # Transcribe chunk
                with open(chunk_path, 'rb') as audio_file:
                    response = self.openai_client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        response_format="json"
                    )
                
                transcriptions.append(response.text)
                
                # Clean up chunk file
                os.remove(chunk_path)
            
            # Combine transcriptions
            full_transcription = " ".join(transcriptions)
            
            return full_transcription
            
        except Exception as e:
            st.error(f"Large file transcription error: {str(e)}")
            return None
    
    def transcribe_with_speaker_diarization(self, audio_file_path):
        """Transcribe with speaker identification (using AssemblyAI as alternative)"""
        try:
            assembly_api_key = os.getenv("ASSEMBLYAI_API_KEY")
            if not assembly_api_key:
                st.warning("AssemblyAI API key not configured, using standard transcription")
                return self.transcribe_audio(audio_file_path)
            
            # Upload file to AssemblyAI
            headers = {
                "authorization": assembly_api_key,
                "content-type": "application/json"
            }
            
            # Upload audio file
            with open(audio_file_path, 'rb') as f:
                response = requests.post(
                    "https://api.assemblyai.com/v2/upload",
                    headers={"authorization": assembly_api_key},
                    data=f
                )
            
            if response.status_code != 200:
                st.error("Failed to upload audio to AssemblyAI")
                return self.transcribe_audio(audio_file_path)
            
            audio_url = response.json()["upload_url"]
            
            # Request transcription with speaker diarization
            transcript_request = {
                "audio_url": audio_url,
                "speaker_labels": True,
                "auto_chapters": True,
                "sentiment_analysis": True
            }
            
            response = requests.post(
                "https://api.assemblyai.com/v2/transcript",
                json=transcript_request,
                headers=headers
            )
            
            if response.status_code != 200:
                st.error("Failed to request transcription")
                return self.transcribe_audio(audio_file_path)
            
            transcript_id = response.json()["id"]
            
            # Poll for completion
            while True:
                response = requests.get(
                    f"https://api.assemblyai.com/v2/transcript/{transcript_id}",
                    headers=headers
                )
                
                transcript = response.json()
                
                if transcript["status"] == "completed":
                    return self._format_diarized_transcript(transcript)
                elif transcript["status"] == "error":
                    st.error(f"Transcription failed: {transcript['error']}")
                    return self.transcribe_audio(audio_file_path)
                else:
                    st.info("Transcription in progress...")
                    import time
                    time.sleep(5)
                    
        except Exception as e:
            st.error(f"Diarization error: {str(e)}")
            return self.transcribe_audio(audio_file_path)
    
    def _format_diarized_transcript(self, transcript_data):
        """Format diarized transcript with speaker labels"""
        try:
            formatted_transcript = []
            
            for utterance in transcript_data.get('utterances', []):
                speaker = utterance.get('speaker', 'Unknown')
                text = utterance.get('text', '')
                confidence = utterance.get('confidence', 0)
                
                formatted_transcript.append(f"Speaker {speaker}: {text}")
            
            return "\n".join(formatted_transcript)
            
        except Exception as e:
            st.error(f"Transcript formatting error: {str(e)}")
            return transcript_data.get('text', '')
    
    def get_transcript_summary(self, transcript):
        """Generate a summary of the transcript"""
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional therapy session summarizer. "
                                 "Create a concise summary of the key topics, themes, and "
                                 "important moments from this therapy session transcript."
                    },
                    {
                        "role": "user",
                        "content": f"Please summarize this therapy session transcript:\n\n{transcript}"
                    }
                ],
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            st.error(f"Summary generation error: {str(e)}")
            return None
