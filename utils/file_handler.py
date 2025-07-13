import os
import tempfile
from typing import Optional
import streamlit as st

class FileHandler:
    """Handle different file types for MindAI"""
    
    def __init__(self):
        self.supported_text_types = [
            'text/plain',
            'application/pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/msword'
        ]
        
    def extract_text_from_file(self, uploaded_file) -> Optional[str]:
        """Extract text content from various file types"""
        try:
            if uploaded_file.type == "text/plain":
                return str(uploaded_file.read(), "utf-8")
            
            elif uploaded_file.type == "application/pdf":
                return self._extract_text_from_pdf(uploaded_file)
            
            elif uploaded_file.type in [
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "application/msword"
            ]:
                st.error("Word document support coming soon. Please convert to PDF or TXT format.")
                return None
                
            else:
                st.error(f"Unsupported file type: {uploaded_file.type}")
                return None
                
        except Exception as e:
            st.error(f"Error extracting text from file: {str(e)}")
            return None
    
    def _extract_text_from_pdf(self, uploaded_file) -> Optional[str]:
        """Extract text from PDF file using PyPDF2"""
        try:
            from PyPDF2 import PdfReader
            
            # Reset file pointer
            uploaded_file.seek(0)
            
            pdf_reader = PdfReader(uploaded_file)
            text_content = []
            
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text.strip():
                        text_content.append(f"=== Page {page_num + 1} ===\n{page_text}")
                except Exception as e:
                    st.warning(f"Could not extract text from page {page_num + 1}: {str(e)}")
                    continue
            
            if not text_content:
                st.error("Could not extract any readable text from the PDF.")
                return None
                
            return "\n\n".join(text_content)
            
        except Exception as e:
            st.error(f"Error processing PDF: {str(e)}")
            return None
    
    def get_file_info(self, uploaded_file) -> dict:
        """Get information about the uploaded file"""
        return {
            'name': uploaded_file.name,
            'type': uploaded_file.type,
            'size': uploaded_file.size,
            'size_mb': round(uploaded_file.size / (1024 * 1024), 2)
        }
    
    def validate_file_size(self, uploaded_file, max_size_mb: int = 50) -> bool:
        """Validate file size"""
        file_size_mb = uploaded_file.size / (1024 * 1024)
        
        if file_size_mb > max_size_mb:
            st.error(f"File size ({file_size_mb:.2f} MB) exceeds maximum allowed size ({max_size_mb} MB)")
            return False
            
        return True
    
    def is_supported_text_file(self, uploaded_file) -> bool:
        """Check if file type is supported for text extraction"""
        return uploaded_file.type in self.supported_text_types