import os
import tempfile
import streamlit as st
from pydub import AudioSegment
from pydub.utils import which
import subprocess

class AudioUtils:
    """Audio processing utilities for therapy session recordings"""
    
    def __init__(self):
        self.supported_formats = ['mp3', 'wav', 'mp4', 'm4a', 'ogg', 'flac', 'aac']
        self.target_format = 'wav'  # Best for transcription
        self.target_sample_rate = 16000  # Optimal for Whisper
        self.target_channels = 1  # Mono for transcription
    
    def convert_to_supported_format(self, input_path: str) -> str:
        """Convert audio file to supported format for transcription"""
        try:
            # Check if file exists
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"Audio file not found: {input_path}")
            
            # Get file extension
            file_extension = input_path.lower().split('.')[-1]
            
            # If already in optimal format, check if conversion is needed
            if file_extension == self.target_format:
                audio = AudioSegment.from_file(input_path)
                if (audio.frame_rate == self.target_sample_rate and 
                    audio.channels == self.target_channels):
                    return input_path
            
            # Load audio file
            audio = AudioSegment.from_file(input_path)
            
            # Convert to optimal settings
            audio = audio.set_frame_rate(self.target_sample_rate)
            audio = audio.set_channels(self.target_channels)
            
            # Generate output path
            output_path = input_path.rsplit('.', 1)[0] + '_converted.wav'
            
            # Export converted audio
            audio.export(output_path, format=self.target_format)
            
            st.info(f"Audio converted to optimal format: {output_path}")
            return output_path
            
        except Exception as e:
            st.error(f"Audio conversion error: {str(e)}")
            return input_path  # Return original if conversion fails
    
    def get_audio_info(self, file_path: str) -> dict:
        """Get audio file information"""
        try:
            audio = AudioSegment.from_file(file_path)
            
            return {
                'duration': len(audio) / 1000.0,  # Duration in seconds
                'sample_rate': audio.frame_rate,
                'channels': audio.channels,
                'format': file_path.split('.')[-1].lower(),
                'file_size': os.path.getsize(file_path),
                'bitrate': audio.frame_rate * audio.frame_width * 8 * audio.channels
            }
            
        except Exception as e:
            st.error(f"Audio info extraction error: {str(e)}")
            return {}
    
    def validate_audio_file(self, file_path: str) -> bool:
        """Validate audio file format and quality"""
        try:
            # Check file extension
            file_extension = file_path.lower().split('.')[-1]
            if file_extension not in self.supported_formats:
                st.error(f"Unsupported audio format: {file_extension}")
                return False
            
            # Try to load audio file
            audio = AudioSegment.from_file(file_path)
            
            # Check minimum duration (5 seconds)
            if len(audio) < 5000:
                st.error("Audio file too short (minimum 5 seconds required)")
                return False
            
            # Check maximum duration (2 hours)
            if len(audio) > 7200000:  # 2 hours in milliseconds
                st.error("Audio file too long (maximum 2 hours)")
                return False
            
            # Check if audio has content (not silent)
            if audio.max_possible_amplitude == 0:
                st.error("Audio file appears to be silent")
                return False
            
            return True
            
        except Exception as e:
            st.error(f"Audio validation error: {str(e)}")
            return False
    
    def enhance_audio_quality(self, file_path: str) -> str:
        """Enhance audio quality for better transcription"""
        try:
            audio = AudioSegment.from_file(file_path)
            
            # Normalize audio levels
            audio = audio.normalize()
            
            # Apply high-pass filter to reduce low-frequency noise
            audio = audio.high_pass_filter(80)
            
            # Apply low-pass filter to reduce high-frequency noise
            audio = audio.low_pass_filter(8000)
            
            # Compress dynamic range slightly
            audio = audio.compress_dynamic_range()
            
            # Generate output path
            output_path = file_path.rsplit('.', 1)[0] + '_enhanced.wav'
            
            # Export enhanced audio
            audio.export(output_path, format='wav')
            
            st.info("Audio quality enhanced for better transcription")
            return output_path
            
        except Exception as e:
            st.error(f"Audio enhancement error: {str(e)}")
            return file_path  # Return original if enhancement fails
    
    def split_audio_by_size(self, file_path: str, max_size_mb: int = 25) -> list:
        """Split audio file into smaller chunks if it exceeds size limit"""
        try:
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            
            if file_size_mb <= max_size_mb:
                return [file_path]
            
            audio = AudioSegment.from_file(file_path)
            
            # Calculate chunk duration based on size
            chunk_duration = (max_size_mb / file_size_mb) * len(audio)
            chunk_duration = int(chunk_duration * 0.9)  # 10% safety margin
            
            chunks = []
            chunk_paths = []
            
            # Split audio into chunks
            for i in range(0, len(audio), chunk_duration):
                chunk = audio[i:i + chunk_duration]
                chunks.append(chunk)
            
            # Export chunks
            base_name = file_path.rsplit('.', 1)[0]
            for i, chunk in enumerate(chunks):
                chunk_path = f"{base_name}_chunk_{i+1}.wav"
                chunk.export(chunk_path, format='wav')
                chunk_paths.append(chunk_path)
            
            st.info(f"Audio split into {len(chunk_paths)} chunks for processing")
            return chunk_paths
            
        except Exception as e:
            st.error(f"Audio splitting error: {str(e)}")
            return [file_path]
    
    def remove_silence(self, file_path: str, silence_threshold: int = -40) -> str:
        """Remove silence from audio file"""
        try:
            audio = AudioSegment.from_file(file_path)
            
            # Split audio by silence
            chunks = AudioSegment.split_on_silence(
                audio,
                min_silence_len=1000,  # 1 second
                silence_thresh=silence_threshold,
                keep_silence=200  # Keep 200ms of silence
            )
            
            # Combine non-silent chunks
            if chunks:
                combined = AudioSegment.empty()
                for chunk in chunks:
                    combined += chunk
                
                # Generate output path
                output_path = file_path.rsplit('.', 1)[0] + '_no_silence.wav'
                
                # Export processed audio
                combined.export(output_path, format='wav')
                
                st.info("Silence removed from audio")
                return output_path
            else:
                st.warning("No audio content found after silence removal")
                return file_path
                
        except Exception as e:
            st.error(f"Silence removal error: {str(e)}")
            return file_path
    
    def extract_audio_from_video(self, video_path: str) -> str:
        """Extract audio from video file"""
        try:
            # Load video file
            video = AudioSegment.from_file(video_path)
            
            # Generate output path
            output_path = video_path.rsplit('.', 1)[0] + '_extracted_audio.wav'
            
            # Export audio
            video.export(output_path, format='wav')
            
            st.info("Audio extracted from video file")
            return output_path
            
        except Exception as e:
            st.error(f"Audio extraction error: {str(e)}")
            return video_path
    
    def get_audio_segments(self, file_path: str, segment_duration: int = 30) -> list:
        """Split audio into segments of specified duration"""
        try:
            audio = AudioSegment.from_file(file_path)
            segment_duration_ms = segment_duration * 1000
            
            segments = []
            for i in range(0, len(audio), segment_duration_ms):
                segment = audio[i:i + segment_duration_ms]
                segments.append(segment)
            
            return segments
            
        except Exception as e:
            st.error(f"Audio segmentation error: {str(e)}")
            return []
    
    def create_audio_thumbnail(self, file_path: str, duration: int = 30) -> str:
        """Create short audio thumbnail for preview"""
        try:
            audio = AudioSegment.from_file(file_path)
            
            # Take first 30 seconds
            thumbnail = audio[:duration * 1000]
            
            # Generate output path
            output_path = file_path.rsplit('.', 1)[0] + '_thumbnail.wav'
            
            # Export thumbnail
            thumbnail.export(output_path, format='wav')
            
            return output_path
            
        except Exception as e:
            st.error(f"Thumbnail creation error: {str(e)}")
            return file_path
    
    def cleanup_temp_files(self, file_paths: list):
        """Clean up temporary audio files"""
        try:
            for file_path in file_paths:
                if os.path.exists(file_path) and '_temp' in file_path:
                    os.remove(file_path)
                    
        except Exception as e:
            st.error(f"Cleanup error: {str(e)}")
    
    def get_audio_fingerprint(self, file_path: str) -> str:
        """Generate audio fingerprint for duplicate detection"""
        try:
            import hashlib
            
            # Read audio file in chunks and hash
            hasher = hashlib.md5()
            
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            
            return hasher.hexdigest()
            
        except Exception as e:
            st.error(f"Fingerprint generation error: {str(e)}")
            return ""
