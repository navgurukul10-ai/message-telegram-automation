"""
Resume Fetcher Utility
Fetches resume text from Google Drive links, PDF URLs, or local files
"""
import os
import sys
import re
import requests
from typing import Optional
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.logger import get_logger

logger = get_logger('resume_fetcher')

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logger.warning("PyPDF2 not installed. PDF text extraction will be limited. Install with: pip install PyPDF2")

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False


class ResumeFetcher:
    """Fetch and extract text from resume URLs or files"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_resume_text(self, resume_url: str) -> Optional[str]:
        """
        Fetch resume text from URL
        
        Supports:
        - Google Drive links (converts to direct download)
        - Direct PDF URLs
        - Other document URLs
        
        Returns:
            Extracted text or None if failed
        """
        if not resume_url:
            return None
        
        try:
            # Clean URL
            resume_url = resume_url.strip()
            
            # Handle Google Drive links
            if 'drive.google.com' in resume_url:
                resume_url = self._convert_google_drive_link(resume_url)
            
            # Fetch the file
            response = self.session.get(resume_url, timeout=30, allow_redirects=True)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('Content-Type', '').lower()
            
            if 'pdf' in content_type or resume_url.lower().endswith('.pdf'):
                # Extract text from PDF
                return self._extract_pdf_text(response.content)
            elif 'text' in content_type or 'html' in content_type:
                # Plain text or HTML
                return response.text[:50000]  # Limit to 50KB
            else:
                # Try to extract as PDF anyway
                return self._extract_pdf_text(response.content)
                
        except Exception as e:
            logger.error(f"Error fetching resume from {resume_url}: {e}")
            return None
    
    def _convert_google_drive_link(self, url: str) -> str:
        """
        Convert Google Drive share link to direct download link
        
        Formats supported:
        - https://drive.google.com/file/d/FILE_ID/view
        - https://drive.google.com/open?id=FILE_ID
        """
        try:
            # Extract file ID
            file_id = None
            
            # Pattern 1: /file/d/FILE_ID/
            match = re.search(r'/file/d/([a-zA-Z0-9_-]+)', url)
            if match:
                file_id = match.group(1)
            
            # Pattern 2: ?id=FILE_ID
            if not file_id:
                parsed = urlparse(url)
                file_id = parse_qs(parsed.query).get('id', [None])[0]
            
            if file_id:
                # Convert to direct download link
                return f"https://drive.google.com/uc?export=download&id={file_id}"
            else:
                return url
                
        except Exception as e:
            logger.warning(f"Could not convert Google Drive link: {e}")
            return url
    
    def _extract_pdf_text(self, pdf_content: bytes) -> Optional[str]:
        """Extract text from PDF content"""
        try:
            import io
            
            # Try pdfplumber first (better extraction)
            if PDFPLUMBER_AVAILABLE:
                try:
                    pdf_file = io.BytesIO(pdf_content)
                    with pdfplumber.open(pdf_file) as pdf:
                        text_parts = []
                        for page in pdf.pages:
                            text = page.extract_text()
                            if text:
                                text_parts.append(text)
                        return '\n\n'.join(text_parts)
                except Exception as e:
                    logger.warning(f"pdfplumber extraction failed: {e}, trying PyPDF2")
            
            # Fallback to PyPDF2
            if PDF_AVAILABLE:
                pdf_file = io.BytesIO(pdf_content)
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                text_parts = []
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
                return '\n\n'.join(text_parts)
            else:
                logger.warning("No PDF library available. Install PyPDF2 or pdfplumber")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            return None
    
    def extract_from_local_file(self, file_path: str) -> Optional[str]:
        """Extract text from local PDF file"""
        try:
            if not os.path.exists(file_path):
                return None
            
            with open(file_path, 'rb') as f:
                content = f.read()
                return self._extract_pdf_text(content)
        except Exception as e:
            logger.error(f"Error reading local file {file_path}: {e}")
            return None

