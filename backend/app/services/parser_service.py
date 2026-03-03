"""
Resume Parser Service
Handles PDF and DOCX parsing without external APIs
"""
import re
import io
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class ResumeParser:
    """Parse resume from PDF or DOCX files"""
    
    SECTION_HEADERS = {
        "skills": ["skills", "technical skills", "technologies", "tools", "competencies", "expertise"],
        "experience": ["experience", "work experience", "employment", "professional experience", "work history"],
        "education": ["education", "academic", "qualifications", "degrees", "schooling"],
        "certifications": ["certifications", "certificates", "credentials", "licenses"],
        "projects": ["projects", "personal projects", "portfolio", "work samples"],
        "summary": ["summary", "objective", "profile", "about", "professional summary"]
    }
    
    def __init__(self):
        self.text = ""
        self.sections = {}
    
    def extract_text_from_pdf(self, file_bytes: bytes) -> str:
        """Extract text from PDF using multiple parsers as fallback"""
        import traceback
        print(f"[DEBUG] Extracting PDF text. File size: {len(file_bytes)} bytes")
        
        text = ""
        
        # Method 1: pdfminer.six
        try:
            from pdfminer.high_level import extract_text
            from pdfminer.pdfparser import PDFSyntaxError
            
            text = extract_text(io.BytesIO(file_bytes))
            print(f"[DEBUG] pdfminer extraction: {len(text)} chars")
            if text and len(text.strip()) > 50:
                print(f"[DEBUG] Using pdfminer result")
                return text.strip()
        except Exception as e:
            print(f"[WARN] pdfminer failed: {e}")
        
        # Method 2: pypdf
        try:
            from pypdf import PdfReader
            
            reader = PdfReader(io.BytesIO(file_bytes))
            pages_text = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    pages_text.append(page_text)
            text = "\n".join(pages_text)
            print(f"[DEBUG] pypdf extraction: {len(text)} chars")
            if text and len(text.strip()) > 50:
                print(f"[DEBUG] Using pypdf result")
                return text.strip()
        except Exception as e:
            print(f"[WARN] pypdf failed: {e}")
        
        # Method 3: pdfplumber
        try:
            import pdfplumber
            
            pages_text = []
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        pages_text.append(page_text)
            text = "\n".join(pages_text)
            print(f"[DEBUG] pdfplumber extraction: {len(text)} chars")
            if text and len(text.strip()) > 50:
                print(f"[DEBUG] Using pdfplumber result")
                return text.strip()
        except Exception as e:
            print(f"[WARN] pdfplumber failed: {e}")
        
        print(f"[ERROR] All PDF parsers failed or returned minimal text")
        return text.strip() if text else ""
    
    def extract_text_from_docx(self, file_bytes: bytes) -> str:
        """Extract text from DOCX using python-docx"""
        import traceback
        print(f"[DEBUG] Extracting DOCX text. File size: {len(file_bytes)} bytes")
        
        try:
            from docx import Document
            
            doc = Document(io.BytesIO(file_bytes))
            paragraphs = [para.text for para in doc.paragraphs]
            text = "\n".join(paragraphs).strip()
            print(f"[DEBUG] DOCX extraction successful. Text length: {len(text)} chars")
            print(f"[DEBUG] First 200 chars: {text[:200] if text else 'EMPTY'}")
            return text
        except Exception as e:
            print(f"[ERROR] Error extracting DOCX text: {e}")
            print(traceback.format_exc())
            return ""
    
    def parse(self, file_bytes: bytes, file_extension: str) -> Dict:
        """Parse resume and extract sections"""
        print(f"[DEBUG] Parsing resume. Extension: {file_extension}, Size: {len(file_bytes)} bytes")
        print(f"[DEBUG] First 20 bytes (hex): {file_bytes[:20].hex() if file_bytes else 'EMPTY'}")
        
        # Extract text based on file type
        if file_extension.lower() == "pdf":
            self.text = self.extract_text_from_pdf(file_bytes)
        elif file_extension.lower() in ["docx", "doc"]:
            self.text = self.extract_text_from_docx(file_bytes)
        else:
            print(f"[ERROR] Unsupported file type: {file_extension}")
            raise ValueError(f"Unsupported file type: {file_extension}")
        
        print(f"[DEBUG] Extracted text length: {len(self.text)} chars")
        
        if not self.text:
            print("[ERROR] Could not extract text from resume - text is empty")
            return {"error": "Could not extract text from resume"}
        
        # Extract sections
        self.sections = self._extract_sections()
        
        # Extract contact info
        contact = self._extract_contact_info()
        
        return {
            "text": self.text,
            "sections": self.sections,
            "contact": contact,
            "word_count": len(self.text.split())
        }
    
    def _extract_sections(self) -> Dict[str, str]:
        """Extract sections from resume text"""
        sections = {}
        lines = self.text.split("\n")
        
        current_section = "summary"
        current_content = []
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Check if line is a section header
            found_section = None
            for section_type, headers in self.SECTION_HEADERS.items():
                for header in headers:
                    if line_lower == header or line_lower.startswith(header + ":"):
                        found_section = section_type
                        break
                if found_section:
                    break
            
            if found_section:
                # Save previous section
                if current_content:
                    sections[current_section] = "\n".join(current_content).strip()
                
                current_section = found_section
                current_content = []
            else:
                current_content.append(line)
        
        # Save last section
        if current_content:
            sections[current_section] = "\n".join(current_content).strip()
        
        return sections
    
    def _extract_contact_info(self) -> Dict[str, Optional[str]]:
        """Extract contact information from resume"""
        contact = {
            "email": None,
            "phone": None,
            "linkedin": None,
            "github": None,
            "name": None
        }
        
        # Email pattern
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        email_match = re.search(email_pattern, self.text)
        if email_match:
            contact["email"] = email_match.group()
        
        # Phone pattern
        phone_pattern = r'[\+]?[(]?[0-9]{1,3}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}'
        phone_match = re.search(phone_pattern, self.text)
        if phone_match:
            contact["phone"] = phone_match.group()
        
        # LinkedIn
        linkedin_pattern = r'linkedin\.com/in/([a-zA-Z0-9-]+)'
        linkedin_match = re.search(linkedin_pattern, self.text, re.IGNORECASE)
        if linkedin_match:
            contact["linkedin"] = f"linkedin.com/in/{linkedin_match.group(1)}"
        
        # GitHub
        github_pattern = r'github\.com/([a-zA-Z0-9-]+)'
        github_match = re.search(github_pattern, self.text, re.IGNORECASE)
        if github_match:
            contact["github"] = f"github.com/{github_match.group(1)}"
        
        # Name (usually first line or first non-empty line)
        lines = [l.strip() for l in self.text.split("\n") if l.strip()]
        if lines:
            # First line is usually the name
            first_line = lines[0]
            # Check if it looks like a name (2-4 words, no special chars)
            if re.match(r'^[A-Za-z\s]{2,50}$', first_line):
                contact["name"] = first_line
        
        return contact


def check_ats_format(text: str, file_bytes: bytes = None) -> Dict[str, any]:
    """
    Check resume format for ATS compatibility
    Returns format score and issues
    """
    issues = []
    score = 10  # Start with perfect score
    
    # Check 1: Text extractable
    if not text or len(text.strip()) < 100:
        issues.append("PDF text is not extractable or too short")
        score -= 3
    
    # Check 2: Has section headers
    section_keywords = ["experience", "education", "skills", "summary"]
    text_lower = text.lower()
    found_sections = sum(1 for kw in section_keywords if kw in text_lower)
    if found_sections < 2:
        issues.append("Missing clear section headings")
        score -= 2
    
    # Check 3: Reasonable length
    word_count = len(text.split())
    if word_count < 100:
        issues.append("Resume is too short")
        score -= 2
    elif word_count > 2000:
        issues.append("Resume is too long (consider condensing)")
        score -= 1
    
    # Check 4: Contact info present
    if not re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text):
        issues.append("Email address not found")
        score -= 1
    
    # Check 5: No excessive special characters (might indicate tables/graphics)
    special_char_ratio = len(re.findall(r'[│├┼┤┌┐└┘─]', text)) / max(len(text), 1)
    if special_char_ratio > 0.01:
        issues.append("Contains table characters that may confuse ATS")
        score -= 2
    
    return {
        "format_score": max(0, score),
        "max_score": 10,
        "is_ats_friendly": score >= 7,
        "issues": issues
    }
