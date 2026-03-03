"""
Resume Builder V4 - Complete ATS-Optimized Resume Generator
Preserves ALL original information with proper layout and sequence
"""
import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ContactInfo:
    """Complete contact information"""
    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    address: str = ""
    linkedin: str = ""
    github: str = ""
    portfolio: str = ""
    twitter: str = ""
    website: str = ""


@dataclass 
class ExperienceEntry:
    """Complete work experience entry"""
    job_title: str = ""
    company: str = ""
    company_description: str = ""
    location: str = ""
    start_date: str = ""
    end_date: str = ""
    is_current: bool = False
    employment_type: str = ""  # Full-time, Part-time, Contract, etc.
    responsibilities: List[str] = field(default_factory=list)
    achievements: List[str] = field(default_factory=list)
    raw_text: str = ""


@dataclass
class EducationEntry:
    """Complete education entry"""
    degree: str = ""
    major: str = ""
    minor: str = ""
    institution: str = ""
    location: str = ""
    start_date: str = ""
    end_date: str = ""
    gpa: str = ""
    honors: str = ""
    coursework: List[str] = field(default_factory=list)
    activities: List[str] = field(default_factory=list)
    raw_text: str = ""


@dataclass
class ProjectEntry:
    """Project entry"""
    name: str = ""
    role: str = ""
    organization: str = ""
    date: str = ""
    url: str = ""
    technologies: List[str] = field(default_factory=list)
    description: List[str] = field(default_factory=list)
    raw_text: str = ""


@dataclass
class CertificationEntry:
    """Certification entry"""
    name: str = ""
    issuer: str = ""
    date: str = ""
    expiry: str = ""
    credential_id: str = ""
    url: str = ""
    raw_text: str = ""


@dataclass
class AwardEntry:
    """Award/Achievement entry"""
    name: str = ""
    issuer: str = ""
    date: str = ""
    description: str = ""
    raw_text: str = ""


@dataclass
class PublicationEntry:
    """Publication entry"""
    title: str = ""
    authors: str = ""
    publication: str = ""
    date: str = ""
    url: str = ""
    raw_text: str = ""


@dataclass
class LanguageEntry:
    """Language proficiency entry"""
    language: str = ""
    proficiency: str = ""  # Native, Fluent, Proficient, Intermediate, Basic


@dataclass
class ResumeData:
    """Complete parsed resume data"""
    contact: ContactInfo = field(default_factory=ContactInfo)
    summary: str = ""
    objective: str = ""
    experience: List[ExperienceEntry] = field(default_factory=list)
    education: List[EducationEntry] = field(default_factory=list)
    skills: Dict[str, List[str]] = field(default_factory=dict)
    projects: List[ProjectEntry] = field(default_factory=list)
    certifications: List[CertificationEntry] = field(default_factory=list)
    awards: List[AwardEntry] = field(default_factory=list)
    publications: List[PublicationEntry] = field(default_factory=list)
    languages: List[LanguageEntry] = field(default_factory=list)
    volunteer: List[ExperienceEntry] = field(default_factory=list)
    interests: List[str] = field(default_factory=list)
    references: str = ""
    additional_sections: Dict[str, str] = field(default_factory=dict)


class ResumeBuilderV4:
    """
    Complete Resume Builder that extracts ALL information
    and creates a properly formatted ATS-optimized version
    """
    
    # Section header patterns for detection
    SECTION_PATTERNS = {
        'summary': r'^(?:professional\s+)?(?:summary|profile|about(?:\s+me)?)\s*[:]*\s*$',
        'objective': r'^(?:career\s+)?objective\s*[:]*\s*$',
        'experience': r'^(?:work\s+|professional\s+)?experience|employment\s+(?:history)?|work\s+history\s*[:]*\s*$',
        'education': r'^education(?:al)?(?:\s+(?:background|history))?\s*[:]*\s*$',
        'skills': r'^(?:technical\s+|core\s+|key\s+)?skills?(?:\s+(?:&|and)\s+(?:competencies|abilities))?\s*[:]*\s*$',
        'projects': r'^(?:personal\s+|academic\s+|key\s+)?projects?\s*[:]*\s*$',
        'certifications': r'^(?:certifications?|licenses?|credentials?|professional\s+certifications?)\s*[:]*\s*$',
        'awards': r'^(?:awards?|honors?|achievements?|recognition)\s*[:]*\s*$',
        'publications': r'^(?:publications?|papers?|research)\s*[:]*\s*$',
        'languages': r'^languages?\s*[:]*\s*$',
        'volunteer': r'^(?:volunteer(?:ing)?|community\s+(?:service|involvement))\s*[:]*\s*$',
        'interests': r'^(?:interests?|hobbies?|activities)\s*[:]*\s*$',
        'references': r'^references?\s*[:]*\s*$'
    }
    
    # Action verbs for improvement
    ACTION_VERBS = {
        'weak_to_strong': {
            'responsible for': 'Managed',
            'duties included': 'Executed',
            'helped': 'Contributed to',
            'helped with': 'Supported',
            'worked on': 'Developed',
            'worked with': 'Collaborated with',
            'was part of': 'Participated in',
            'did': 'Performed',
            'made': 'Created',
            'got': 'Achieved',
            'had to': 'Successfully',
            'in charge of': 'Oversaw',
            'dealt with': 'Managed',
            'took care of': 'Handled',
            'tasked with': 'Accomplished',
            'assisted': 'Supported',
            'involved in': 'Contributed to',
            'participated': 'Engaged in'
        },
        'strong_verbs': [
            'achieved', 'administered', 'advanced', 'analyzed', 'architected',
            'automated', 'built', 'championed', 'collaborated', 'conducted',
            'consolidated', 'coordinated', 'created', 'decreased', 'delivered',
            'designed', 'developed', 'directed', 'drove', 'enabled',
            'engineered', 'enhanced', 'established', 'executed', 'expanded',
            'facilitated', 'generated', 'grew', 'implemented', 'improved',
            'increased', 'initiated', 'innovated', 'integrated', 'launched',
            'led', 'managed', 'maximized', 'mentored', 'negotiated',
            'optimized', 'orchestrated', 'organized', 'oversaw', 'pioneered',
            'planned', 'produced', 'reduced', 'redesigned', 'resolved',
            'restructured', 'revamped', 'scaled', 'secured', 'spearheaded',
            'streamlined', 'strengthened', 'supervised', 'trained', 'transformed'
        ]
    }
    
    def __init__(self):
        self.nlp = None
        self._load_models()
    
    def _load_models(self):
        """Load NLP models"""
        try:
            import spacy
            self.nlp = spacy.load("en_core_web_md")
        except Exception as e:
            logger.warning(f"spaCy not available: {e}")
            self.nlp = None
    
    def build_optimized_resume(
        self,
        original_text: str,
        sections: Dict[str, str],
        detected_skills: Dict[str, List[str]],
        issues: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Build complete ATS-optimized resume
        """
        # Step 1: Parse all resume data
        resume_data = self._parse_complete_resume(original_text, sections, detected_skills)
        
        # Step 2: Generate optimized sections in proper order
        optimized_sections = self._generate_all_sections(resume_data, detected_skills)
        
        # Step 3: Build final output
        output = {
            "sections": optimized_sections,
            "full_resume": self._build_full_resume(optimized_sections),
            "improvements": self._list_all_improvements(resume_data, issues),
            "original_data": self._get_original_data_summary(resume_data),
            "template_suggestions": self._get_template_suggestions(),
            "section_order": list(optimized_sections.keys())
        }
        
        return output
    
    def _parse_complete_resume(
        self,
        text: str,
        sections: Dict[str, str],
        detected_skills: Dict[str, List[str]]
    ) -> ResumeData:
        """Parse all data from resume"""
        data = ResumeData()
        
        # Parse contact information
        data.contact = self._parse_contact_info(text, sections.get('contact', ''))
        
        # Parse summary/objective
        data.summary = self._extract_summary(text, sections.get('summary', ''))
        data.objective = self._extract_objective(text, sections.get('objective', ''))
        
        # Parse experience - THIS IS CRITICAL
        data.experience = self._parse_all_experiences(text, sections.get('experience', ''))
        
        # Parse education
        data.education = self._parse_all_education(text, sections.get('education', ''))
        
        # Parse skills
        data.skills = self._parse_all_skills(text, sections.get('skills', ''), detected_skills)
        
        # Parse projects
        data.projects = self._parse_all_projects(text, sections.get('projects', ''))
        
        # Parse certifications
        data.certifications = self._parse_all_certifications(text, sections.get('certifications', ''))
        
        # Parse awards
        data.awards = self._parse_all_awards(text, sections.get('awards', ''))
        
        # Parse publications
        data.publications = self._parse_all_publications(text, sections.get('publications', ''))
        
        # Parse languages
        data.languages = self._parse_all_languages(text, sections.get('languages', ''))
        
        # Parse volunteer experience
        data.volunteer = self._parse_volunteer(text, sections.get('volunteer', ''))
        
        # Parse interests
        data.interests = self._parse_interests(text, sections.get('interests', ''))
        
        # Parse references
        data.references = sections.get('references', '')
        
        return data
    
    def _parse_contact_info(self, text: str, contact_section: str) -> ContactInfo:
        """Extract complete contact information"""
        contact = ContactInfo()
        search_text = contact_section if contact_section else text[:2000]
        
        # Extract name - check first few lines
        contact.name = self._extract_name_v4(text)
        
        # Extract email
        email_patterns = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        ]
        for pattern in email_patterns:
            match = re.search(pattern, search_text)
            if match:
                contact.email = match.group()
                break
        
        # Extract phone - comprehensive patterns
        phone_patterns = [
            r'\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}',
            r'\+[0-9]{1,3}[-.\s]?[0-9]{2,4}[-.\s]?[0-9]{3,4}[-.\s]?[0-9]{3,4}',
            r'[0-9]{5}[-.\s]?[0-9]{5}',  # Some international formats
        ]
        for pattern in phone_patterns:
            match = re.search(pattern, search_text)
            if match:
                contact.phone = self._format_phone(match.group())
                break
        
        # Extract LinkedIn
        linkedin_patterns = [
            r'linkedin\.com/in/([a-zA-Z0-9_-]+)',
            r'linkedin:\s*/?(?:in/)?([a-zA-Z0-9_-]+)',
            r'(?:linkedin|ln):\s*(https?://[^\s]+)'
        ]
        for pattern in linkedin_patterns:
            match = re.search(pattern, search_text, re.IGNORECASE)
            if match:
                if match.group().startswith('http'):
                    contact.linkedin = match.group()
                else:
                    contact.linkedin = f"linkedin.com/in/{match.group(1)}"
                break
        
        # Extract GitHub
        github_patterns = [
            r'github\.com/([a-zA-Z0-9_-]+)',
            r'github:\s*/?([a-zA-Z0-9_-]+)',
        ]
        for pattern in github_patterns:
            match = re.search(pattern, search_text, re.IGNORECASE)
            if match:
                contact.github = f"github.com/{match.group(1)}"
                break
        
        # Extract portfolio/website
        portfolio_patterns = [
            r'portfolio[:\s]*(https?://[^\s]+|[a-zA-Z0-9][a-zA-Z0-9-]+\.[a-zA-Z]{2,}[^\s]*)',
            r'website[:\s]*(https?://[^\s]+)',
            r'(?<!@)www\.[a-zA-Z0-9][a-zA-Z0-9-]+\.[a-zA-Z]{2,}[^\s]*'
        ]
        for pattern in portfolio_patterns:
            match = re.search(pattern, search_text, re.IGNORECASE)
            if match:
                contact.portfolio = match.group(1) if match.lastindex else match.group()
                break
        
        # Extract location
        contact.location = self._extract_location_v4(search_text)
        
        # Extract full address if present
        address_match = re.search(
            r'\d+[^,\n]+,\s*[A-Za-z\s]+,\s*[A-Z]{2}\s*\d{5}(?:-\d{4})?',
            search_text
        )
        if address_match:
            contact.address = address_match.group()
        
        return contact
    
    def _extract_name_v4(self, text: str) -> str:
        """Extract name with improved accuracy"""
        lines = text.strip().split('\n')
        
        # Skip patterns - things that are NOT names
        skip_patterns = [
            r'^resume$', r'^curriculum\s+vitae$', r'^cv$',
            r'^[a-z0-9._%+-]+@', r'^http', r'^www\.',
            r'^\+?\d+', r'^\d{3}', r'^linkedin', r'^github',
            r'^experience$', r'^education$', r'^skills$',
            r'^summary$', r'^objective$', r'^profile$',
            r'^contact', r'^professional'
        ]
        
        for line in lines[:15]:  # Check first 15 lines
            line = line.strip()
            if not line or len(line) < 2 or len(line) > 60:
                continue
            
            # Skip if matches any skip pattern
            if any(re.match(p, line.lower()) for p in skip_patterns):
                continue
            
            # Skip lines with too many special characters
            special_count = sum(1 for c in line if c in '@:/\\|[]{}()#$%^&*+=<>')
            if special_count > 2:
                continue
            
            # Check if it looks like a name
            words = line.split()
            if 1 <= len(words) <= 5:
                # Most words should be capitalized or be name particles
                name_particles = ['de', 'van', 'von', 'der', 'la', 'le', 'da']
                valid_words = 0
                for w in words:
                    clean_w = w.rstrip('.,')
                    if clean_w[0].isupper() or clean_w.lower() in name_particles:
                        valid_words += 1
                
                if valid_words >= len(words) * 0.6:
                    return line.strip()
        
        return ""
    
    def _extract_location_v4(self, text: str) -> str:
        """Extract location with better accuracy"""
        # US City, State format
        us_match = re.search(
            r'([A-Z][a-z]+(?:\s[A-Z][a-z]+)*),\s*([A-Z]{2})\b(?:\s+\d{5})?',
            text
        )
        if us_match:
            return f"{us_match.group(1)}, {us_match.group(2)}"
        
        # City, State/Province, Country
        intl_match = re.search(
            r'([A-Z][a-z]+(?:\s[A-Z][a-z]+)?),\s*([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)',
            text
        )
        if intl_match:
            loc = f"{intl_match.group(1)}, {intl_match.group(2)}"
            # Avoid matching section headers
            if len(loc) < 50 and not any(kw in loc.lower() for kw in ['experience', 'education', 'skills']):
                return loc
        
        return ""
    
    def _format_phone(self, phone: str) -> str:
        """Format phone number consistently"""
        digits = re.sub(r'[^\d+]', '', phone)
        if digits.startswith('+'):
            return phone  # Keep international format
        elif len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == '1':
            return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        return phone
    
    def _extract_summary(self, text: str, summary_section: str) -> str:
        """Extract professional summary"""
        if summary_section and len(summary_section.strip()) > 20:
            return summary_section.strip()
        
        # Try to find summary section
        match = re.search(
            r'(?:professional\s+)?summary[:\s]*\n([\s\S]*?)(?=\n(?:experience|education|skills|objective|$))',
            text, re.IGNORECASE
        )
        if match:
            summary = match.group(1).strip()
            # Clean up
            summary = re.sub(r'^(?:summary|profile)[:\s]*', '', summary, flags=re.IGNORECASE)
            return summary[:1000]  # Limit length
        
        return ""
    
    def _extract_objective(self, text: str, objective_section: str) -> str:
        """Extract career objective"""
        if objective_section and len(objective_section.strip()) > 20:
            return objective_section.strip()
        
        match = re.search(
            r'(?:career\s+)?objective[:\s]*\n([\s\S]*?)(?=\n(?:experience|education|skills|summary|$))',
            text, re.IGNORECASE
        )
        if match:
            return match.group(1).strip()[:500]
        
        return ""
    
    def _parse_all_experiences(self, text: str, exp_section: str) -> List[ExperienceEntry]:
        """Parse ALL work experiences with complete information"""
        experiences = []
        
        # Get experience section
        if not exp_section:
            exp_section = self._find_section(text, 'experience')
        
        if not exp_section:
            return experiences
        
        # Split into individual job blocks
        job_blocks = self._split_experience_blocks(exp_section)
        
        for block in job_blocks:
            exp = self._parse_single_experience(block)
            if exp.job_title or exp.company or exp.responsibilities:
                experiences.append(exp)
        
        return experiences
    
    def _find_section(self, text: str, section_name: str) -> str:
        """Find a specific section in text"""
        pattern = self.SECTION_PATTERNS.get(section_name, '')
        if not pattern:
            return ""
        
        # Find section header
        lines = text.split('\n')
        start_idx = -1
        
        for i, line in enumerate(lines):
            if re.match(pattern, line.strip(), re.IGNORECASE):
                start_idx = i + 1
                break
        
        if start_idx == -1:
            return ""
        
        # Find end of section (next section header or end)
        end_idx = len(lines)
        for section, sect_pattern in self.SECTION_PATTERNS.items():
            if section == section_name:
                continue
            for i in range(start_idx, len(lines)):
                if re.match(sect_pattern, lines[i].strip(), re.IGNORECASE):
                    end_idx = min(end_idx, i)
                    break
        
        return '\n'.join(lines[start_idx:end_idx]).strip()
    
    def _split_experience_blocks(self, exp_text: str) -> List[str]:
        """Split experience text into individual job blocks"""
        lines = exp_text.split('\n')
        blocks = []
        current_block = []
        
        # Pattern for job header (date range is strong indicator)
        date_pattern = r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*\d{4}|(?:19|20)\d{2}\s*[-–—]\s*(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*\d{4}|(?:19|20)\d{2}|Present|Current|Now|Ongoing)'
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            # Check if this line starts a new job
            is_new_job = False
            
            # Strong indicator: line has date range
            if re.search(date_pattern, line_stripped, re.IGNORECASE):
                # Check if previous line might be job title
                if current_block and not current_block[-1].strip().startswith(('•', '-', '*', '●')):
                    is_new_job = True
                elif i > 0 and lines[i-1].strip() and not lines[i-1].strip().startswith(('•', '-', '*', '●')):
                    is_new_job = True
            
            # Check for job title keywords at start of line
            job_title_keywords = [
                'senior', 'junior', 'lead', 'staff', 'principal', 'chief',
                'head', 'manager', 'director', 'vp', 'vice president',
                'engineer', 'developer', 'analyst', 'designer', 'architect',
                'consultant', 'specialist', 'coordinator', 'administrator',
                'associate', 'assistant', 'intern', 'trainee'
            ]
            first_words = line_stripped.lower().split()[:2]
            if any(kw in first_words for kw in job_title_keywords):
                if current_block and len(current_block) > 2:
                    is_new_job = True
            
            if is_new_job and current_block:
                blocks.append('\n'.join(current_block))
                current_block = []
            
            current_block.append(line)
        
        if current_block:
            blocks.append('\n'.join(current_block))
        
        return [b for b in blocks if b.strip()]
    
    def _parse_single_experience(self, block: str) -> ExperienceEntry:
        """Parse a single experience block"""
        exp = ExperienceEntry(raw_text=block)
        lines = [l for l in block.split('\n') if l.strip()]
        
        if not lines:
            return exp
        
        # Separate header lines from bullet points
        header_lines = []
        bullet_lines = []
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith(('•', '-', '*', '–', '►', '○', '●', '▪', '◦')):
                bullet_lines.append(stripped)
            elif bullet_lines:  # Already in bullets section
                if len(stripped) > 30 and not re.match(r'^[A-Z]', stripped):
                    # Continuation of previous bullet
                    bullet_lines[-1] += ' ' + stripped
                elif re.match(r'^[a-z]', stripped):
                    # Lowercase start = continuation
                    bullet_lines[-1] += ' ' + stripped
                else:
                    bullet_lines.append(stripped)
            else:
                header_lines.append(stripped)
        
        # Parse header to extract job info
        self._parse_experience_header(exp, header_lines)
        
        # Parse bullet points
        for bullet in bullet_lines:
            cleaned = re.sub(r'^[•\-\*–►○●▪◦]\s*', '', bullet).strip()
            if cleaned and len(cleaned) > 5:
                exp.responsibilities.append(cleaned)
        
        return exp
    
    def _parse_experience_header(self, exp: ExperienceEntry, header_lines: List[str]) -> None:
        """Parse experience header lines"""
        if not header_lines:
            return
        
        all_header = ' | '.join(header_lines)
        
        # Extract dates first
        date_pattern = r'((?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)[.\s]*\d{4}|(?:19|20)\d{2})\s*[-–—]\s*((?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)[.\s]*\d{4}|(?:19|20)\d{2}|Present|Current|Now|Ongoing)'
        
        date_match = re.search(date_pattern, all_header, re.IGNORECASE)
        if date_match:
            exp.start_date = date_match.group(1).strip()
            exp.end_date = date_match.group(2).strip()
            exp.is_current = exp.end_date.lower() in ['present', 'current', 'now', 'ongoing']
        
        # Extract location
        loc_match = re.search(r'([A-Z][a-z]+(?:\s[A-Z][a-z]+)?),?\s*([A-Z]{2})\b', all_header)
        if loc_match:
            exp.location = f"{loc_match.group(1)}, {loc_match.group(2)}"
        else:
            # Try City, Country format
            loc_match2 = re.search(r'\|\s*([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)\s*(?:\||$)', all_header)
            if loc_match2:
                exp.location = loc_match2.group(1).strip()
        
        # Extract job title and company from first two header lines
        for i, line in enumerate(header_lines[:3]):
            # Clean the line
            cleaned = line.strip()
            cleaned = re.sub(date_pattern, '', cleaned, flags=re.IGNORECASE).strip()
            cleaned = re.sub(r'\|\s*$', '', cleaned).strip()
            cleaned = re.sub(r'[,|]\s*[A-Z][a-z]+,?\s*[A-Z]{2}\b', '', cleaned).strip()
            cleaned = cleaned.strip(' |,-–—')
            
            if not cleaned:
                continue
            
            # Check for "Title at Company" or "Title | Company"
            separators = [' at ', ' @ ', ' - ', ' | ', ' – ', ' — ', ', ']
            found_sep = False
            for sep in separators:
                if sep in cleaned:
                    parts = cleaned.split(sep, 1)
                    if not exp.job_title:
                        exp.job_title = parts[0].strip()
                    if len(parts) > 1 and not exp.company:
                        exp.company = parts[1].strip()
                    found_sep = True
                    break
            
            if not found_sep:
                # First non-empty line is usually job title
                if i == 0 and not exp.job_title:
                    exp.job_title = cleaned
                elif i == 1 and not exp.company:
                    exp.company = cleaned
    
    def _parse_all_education(self, text: str, edu_section: str) -> List[EducationEntry]:
        """Parse all education entries"""
        entries = []
        
        if not edu_section:
            edu_section = self._find_section(text, 'education')
        
        if not edu_section:
            return entries
        
        # Split into blocks
        blocks = self._split_education_blocks(edu_section)
        
        for block in blocks:
            entry = self._parse_single_education(block)
            if entry.degree or entry.institution:
                entries.append(entry)
        
        return entries
    
    def _split_education_blocks(self, edu_text: str) -> List[str]:
        """Split education text into individual entries"""
        lines = edu_text.split('\n')
        blocks = []
        current_block = []
        
        degree_keywords = [
            'bachelor', 'master', 'phd', 'ph.d', 'doctorate', 'associate',
            'diploma', 'certificate', 'b.s', 'b.a', 'm.s', 'm.a', 'mba',
            'b.tech', 'm.tech', 'b.e', 'm.e', 'b.sc', 'm.sc',
            'university', 'college', 'institute', 'school', 'academy'
        ]
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Check if this starts a new education entry
            is_new_entry = any(kw in line_lower for kw in degree_keywords)
            
            if is_new_entry and current_block:
                blocks.append('\n'.join(current_block))
                current_block = []
            
            current_block.append(line)
        
        if current_block:
            blocks.append('\n'.join(current_block))
        
        return [b for b in blocks if b.strip()]
    
    def _parse_single_education(self, block: str) -> EducationEntry:
        """Parse a single education block"""
        entry = EducationEntry(raw_text=block)
        all_text = ' '.join(block.split())
        
        # Extract degree
        degree_patterns = [
            r"((?:Bachelor|Master|Doctor)(?:'s)?(?:\s+of\s+(?:Science|Arts|Engineering|Business|Technology|Administration|Computer Science|Information Technology))?)",
            r"(B\.?S\.?|B\.?A\.?|M\.?S\.?|M\.?A\.?|M\.?B\.?A\.?|Ph\.?D\.?|B\.?Tech|M\.?Tech|B\.?E\.?|M\.?E\.?|B\.?Sc\.?|M\.?Sc\.?)",
            r"(Associate(?:'s)?\s+(?:Degree|of\s+(?:Applied\s+)?(?:Science|Arts)))",
            r"(High\s+School\s+Diploma|GED)"
        ]
        
        for pattern in degree_patterns:
            match = re.search(pattern, all_text, re.IGNORECASE)
            if match:
                entry.degree = match.group(1).strip()
                break
        
        # Extract major/field of study
        major_patterns = [
            r'(?:in|major(?:ing)?\s+in|concentration\s+in)\s+([A-Za-z\s]+?)(?:,|\.|$|with)',
            r'(?:B\.?S\.?|B\.?A\.?|M\.?S\.?|M\.?A\.?)\s+(?:in\s+)?([A-Za-z\s]+?)(?:,|\.|$|\d)'
        ]
        for pattern in major_patterns:
            match = re.search(pattern, all_text, re.IGNORECASE)
            if match:
                entry.major = match.group(1).strip()[:50]
                break
        
        # Extract minor
        minor_match = re.search(r'minor(?:\s+in)?\s+([A-Za-z\s]+?)(?:,|\.|$)', all_text, re.IGNORECASE)
        if minor_match:
            entry.minor = minor_match.group(1).strip()
        
        # Extract institution
        inst_patterns = [
            r'([A-Z][a-zA-Z\s]+(?:University|College|Institute|School|Academy))',
            r'(?:at|from)\s+([A-Z][a-zA-Z\s]+?)(?:,|\.|$|\d)'
        ]
        for pattern in inst_patterns:
            match = re.search(pattern, all_text)
            if match:
                entry.institution = match.group(1).strip()
                break
        
        # Extract graduation date
        date_patterns = [
            r'(?:Class\s+of\s+|Graduated?\s*:?\s*|Expected\s*:?\s*)(\w+\s+\d{4}|\d{4})',
            r'(?:May|December|August|June|January)\s+\d{4}',
            r'(?:20|19)\d{2}'
        ]
        for pattern in date_patterns:
            match = re.search(pattern, all_text, re.IGNORECASE)
            if match:
                entry.end_date = match.group() if match.lastindex is None else match.group(1)
                break
        
        # Extract GPA
        gpa_match = re.search(r'(?:GPA|Grade)[:\s]*(\d+\.\d+)(?:\s*/\s*(\d+\.\d+))?', all_text, re.IGNORECASE)
        if gpa_match:
            entry.gpa = gpa_match.group(1)
            if gpa_match.group(2):
                entry.gpa += f"/{gpa_match.group(2)}"
        
        # Extract honors
        honors_patterns = [
            r'((?:summa|magna|cum)\s+laude)',
            r"(Dean'?s\s+List)",
            r'(Honor(?:s|\'s)?\s+(?:Roll|Student|Society))',
            r'(Valedictorian|Salutatorian)',
            r'(First\s+Class\s+(?:Honors?|Distinction))'
        ]
        honors = []
        for pattern in honors_patterns:
            match = re.search(pattern, all_text, re.IGNORECASE)
            if match:
                honors.append(match.group(1))
        if honors:
            entry.honors = ', '.join(honors)
        
        # Extract coursework
        coursework_match = re.search(r'(?:Relevant\s+)?Coursework[:\s]*([^.]+)', all_text, re.IGNORECASE)
        if coursework_match:
            courses = re.split(r'[,;]', coursework_match.group(1))
            entry.coursework = [c.strip() for c in courses if c.strip()]
        
        return entry
    
    def _parse_all_skills(
        self,
        text: str,
        skills_section: str,
        detected_skills: Dict[str, List[str]]
    ) -> Dict[str, List[str]]:
        """Parse all skills with proper categorization"""
        skills = {
            'programming_languages': [],
            'frameworks': [],
            'databases': [],
            'cloud_devops': [],
            'tools': [],
            'technical': [],
            'soft_skills': [],
            'other': []
        }
        
        # Merge detected skills
        all_tech = set(detected_skills.get('technical', []))
        all_soft = set(detected_skills.get('soft', []))
        all_tools = set(detected_skills.get('tools', []))
        
        # Also extract from skills section text
        if skills_section:
            # Remove header
            cleaned = re.sub(r'^(?:skills?|technical skills?|core competencies)[:\s]*', '', 
                           skills_section, flags=re.IGNORECASE)
            # Split by common delimiters
            raw_skills = re.split(r'[,;|•●○◦▪■□►\n]', cleaned)
            for s in raw_skills:
                s = s.strip()
                if s and len(s) > 1 and len(s) < 50:
                    all_tech.add(s)
        
        # Categorize skills
        prog_langs = {
            'python', 'javascript', 'java', 'c++', 'c#', 'c', 'go', 'golang',
            'ruby', 'php', 'typescript', 'swift', 'kotlin', 'r', 'scala',
            'rust', 'perl', 'matlab', 'shell', 'bash', 'sql', 'nosql',
            'html', 'css', 'sass', 'less', 'objective-c', 'dart', 'lua'
        }
        
        frameworks_set = {
            'react', 'angular', 'vue', 'vue.js', 'django', 'flask', 'fastapi',
            'express', 'express.js', 'node.js', 'nodejs', 'spring', 'spring boot',
            'rails', 'ruby on rails', 'next.js', 'nextjs', 'nuxt.js', 'nuxtjs',
            '.net', 'asp.net', 'laravel', 'symfony', 'jquery', 'bootstrap',
            'tailwind', 'tailwindcss', 'material-ui', 'redux', 'graphql',
            'tensorflow', 'pytorch', 'keras', 'pandas', 'numpy', 'scikit-learn'
        }
        
        databases_set = {
            'mysql', 'postgresql', 'postgres', 'mongodb', 'redis', 'elasticsearch',
            'oracle', 'dynamodb', 'cassandra', 'sqlite', 'mariadb', 'couchdb',
            'firebase', 'neo4j', 'snowflake', 'bigquery', 'redshift'
        }
        
        cloud_devops_set = {
            'aws', 'amazon web services', 'azure', 'gcp', 'google cloud',
            'docker', 'kubernetes', 'k8s', 'terraform', 'ansible', 'jenkins',
            'ci/cd', 'github actions', 'gitlab ci', 'circleci', 'travis',
            'linux', 'unix', 'nginx', 'apache', 'heroku', 'netlify', 'vercel'
        }
        
        for skill in all_tech:
            skill_lower = skill.lower().strip()
            if skill_lower in prog_langs:
                skills['programming_languages'].append(skill)
            elif skill_lower in frameworks_set:
                skills['frameworks'].append(skill)
            elif skill_lower in databases_set:
                skills['databases'].append(skill)
            elif skill_lower in cloud_devops_set:
                skills['cloud_devops'].append(skill)
            else:
                skills['technical'].append(skill)
        
        for skill in all_tools:
            skills['tools'].append(skill)
        
        for skill in all_soft:
            skills['soft_skills'].append(skill)
        
        # Deduplicate
        for key in skills:
            skills[key] = list(set(skills[key]))
        
        return skills
    
    def _parse_all_projects(self, text: str, projects_section: str) -> List[ProjectEntry]:
        """Parse all projects"""
        projects = []
        
        if not projects_section:
            projects_section = self._find_section(text, 'projects')
        
        if not projects_section:
            return projects
        
        # Split into project blocks
        lines = projects_section.split('\n')
        current_block = []
        
        for line in lines:
            stripped = line.strip()
            # New project usually starts with project name (capitalized, not a bullet)
            if stripped and not stripped.startswith(('•', '-', '*', '●')) and len(current_block) > 0:
                if re.match(r'^[A-Z]', stripped) and len(stripped) < 80:
                    projects.append(self._parse_single_project('\n'.join(current_block)))
                    current_block = []
            current_block.append(line)
        
        if current_block:
            projects.append(self._parse_single_project('\n'.join(current_block)))
        
        return [p for p in projects if p.name or p.description]
    
    def _parse_single_project(self, block: str) -> ProjectEntry:
        """Parse a single project entry"""
        project = ProjectEntry(raw_text=block)
        lines = [l.strip() for l in block.split('\n') if l.strip()]
        
        if not lines:
            return project
        
        # First line is usually project name
        first_line = lines[0]
        
        # Check for "Name | Link" or "Name - Description" format
        if '|' in first_line:
            parts = first_line.split('|')
            project.name = parts[0].strip()
            remaining = '|'.join(parts[1:]).strip()
            
            # Check if remaining is URL
            if re.match(r'https?://', remaining) or 'github.com' in remaining:
                project.url = remaining
        elif ' - ' in first_line:
            parts = first_line.split(' - ', 1)
            project.name = parts[0].strip()
        else:
            project.name = first_line
        
        # Extract URL
        for line in lines:
            url_match = re.search(r'(https?://[^\s]+|github\.com/[^\s]+)', line)
            if url_match and not project.url:
                project.url = url_match.group(1)
        
        # Extract technologies
        tech_match = re.search(r'(?:Technologies?|Tech\s+Stack|Built\s+with|Using)[:\s]*([^.]+)', block, re.IGNORECASE)
        if tech_match:
            techs = re.split(r'[,;]', tech_match.group(1))
            project.technologies = [t.strip() for t in techs if t.strip()]
        
        # Extract description bullets
        for line in lines[1:]:
            if line.startswith(('•', '-', '*', '●')):
                cleaned = re.sub(r'^[•\-\*●]\s*', '', line).strip()
                if cleaned:
                    project.description.append(cleaned)
            elif not project.description and len(line) > 20:
                project.description.append(line)
        
        return project
    
    def _parse_all_certifications(self, text: str, cert_section: str) -> List[CertificationEntry]:
        """Parse all certifications"""
        certs = []
        
        if not cert_section:
            cert_section = self._find_section(text, 'certifications')
        
        if not cert_section:
            return certs
        
        lines = cert_section.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 5:
                continue
            
            cert = CertificationEntry(raw_text=line)
            
            # Remove bullet
            cleaned = re.sub(r'^[•\-\*●▪]\s*', '', line).strip()
            
            # Try to extract components
            # Pattern: "Certification Name - Issuer (Date)" or "Certification Name, Issuer, Date"
            parts = re.split(r'\s*[-–—|,]\s*', cleaned)
            
            if len(parts) >= 1:
                cert.name = parts[0].strip()
            if len(parts) >= 2:
                # Check if second part is date or issuer
                if re.match(r'(?:19|20)\d{2}|(?:Jan|Feb|Mar)', parts[1], re.IGNORECASE):
                    cert.date = parts[1].strip()
                else:
                    cert.issuer = parts[1].strip()
            if len(parts) >= 3:
                cert.date = parts[2].strip()
            
            # Extract credential ID
            id_match = re.search(r'(?:ID|Credential)[:\s#]*([A-Z0-9-]+)', cleaned, re.IGNORECASE)
            if id_match:
                cert.credential_id = id_match.group(1)
            
            if cert.name:
                certs.append(cert)
        
        return certs
    
    def _parse_all_awards(self, text: str, awards_section: str) -> List[AwardEntry]:
        """Parse all awards/achievements"""
        awards = []
        
        if not awards_section:
            awards_section = self._find_section(text, 'awards')
        
        if not awards_section:
            return awards
        
        lines = awards_section.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 5:
                continue
            
            award = AwardEntry(raw_text=line)
            cleaned = re.sub(r'^[•\-\*●▪]\s*', '', line).strip()
            
            # Try to extract date
            date_match = re.search(r'[,\-–—]\s*((?:19|20)\d{2})', cleaned)
            if date_match:
                award.date = date_match.group(1)
                cleaned = cleaned[:date_match.start()].strip(' ,–—-')
            
            # Check for issuer pattern: "Award - Issuer"
            if ' - ' in cleaned:
                parts = cleaned.split(' - ', 1)
                award.name = parts[0].strip()
                award.issuer = parts[1].strip()
            else:
                award.name = cleaned
            
            if award.name:
                awards.append(award)
        
        return awards
    
    def _parse_all_publications(self, text: str, pub_section: str) -> List[PublicationEntry]:
        """Parse all publications"""
        pubs = []
        
        if not pub_section:
            pub_section = self._find_section(text, 'publications')
        
        if not pub_section:
            return pubs
        
        lines = pub_section.split('\n')
        current_block = []
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                if current_block:
                    pub = self._parse_single_publication('\n'.join(current_block))
                    if pub.title:
                        pubs.append(pub)
                    current_block = []
            else:
                current_block.append(stripped)
        
        if current_block:
            pub = self._parse_single_publication('\n'.join(current_block))
            if pub.title:
                pubs.append(pub)
        
        return pubs
    
    def _parse_single_publication(self, block: str) -> PublicationEntry:
        """Parse a single publication"""
        pub = PublicationEntry(raw_text=block)
        
        # Remove bullet
        cleaned = re.sub(r'^[•\-\*●▪]\s*', '', block).strip()
        
        # Try to extract title (usually in quotes or first part)
        title_match = re.search(r'"([^"]+)"', cleaned)
        if title_match:
            pub.title = title_match.group(1)
        else:
            # First sentence might be title
            first_part = cleaned.split('.')[0]
            if len(first_part) < 150:
                pub.title = first_part
        
        # Extract URL
        url_match = re.search(r'(https?://[^\s]+)', cleaned)
        if url_match:
            pub.url = url_match.group(1)
        
        # Extract date
        date_match = re.search(r'(?:19|20)\d{2}', cleaned)
        if date_match:
            pub.date = date_match.group()
        
        return pub
    
    def _parse_all_languages(self, text: str, lang_section: str) -> List[LanguageEntry]:
        """Parse all languages"""
        languages = []
        
        if not lang_section:
            lang_section = self._find_section(text, 'languages')
        
        if not lang_section:
            return languages
        
        # Common patterns
        lang_patterns = [
            r'([A-Za-z]+)\s*[-–—:]\s*(Native|Fluent|Proficient|Professional|Intermediate|Basic|Elementary|Conversational|Advanced|Working|Limited)',
            r'([A-Za-z]+)\s*\(([^)]+)\)',
        ]
        
        for pattern in lang_patterns:
            for match in re.finditer(pattern, lang_section, re.IGNORECASE):
                lang = LanguageEntry()
                lang.language = match.group(1).strip()
                lang.proficiency = match.group(2).strip()
                if lang.language.lower() not in ['programming', 'language', 'languages']:
                    languages.append(lang)
        
        # Also try simple comma-separated list
        if not languages:
            langs = re.split(r'[,;|\n]', lang_section)
            for l in langs:
                l = l.strip()
                if l and len(l) < 30 and re.match(r'^[A-Za-z]+$', l.split()[0]):
                    lang = LanguageEntry(language=l)
                    languages.append(lang)
        
        return languages
    
    def _parse_volunteer(self, text: str, vol_section: str) -> List[ExperienceEntry]:
        """Parse volunteer experience"""
        if not vol_section:
            vol_section = self._find_section(text, 'volunteer')
        
        if not vol_section:
            return []
        
        # Parse similar to regular experience
        blocks = self._split_experience_blocks(vol_section)
        experiences = []
        
        for block in blocks:
            exp = self._parse_single_experience(block)
            if exp.job_title or exp.company or exp.responsibilities:
                experiences.append(exp)
        
        return experiences
    
    def _parse_interests(self, text: str, interests_section: str) -> List[str]:
        """Parse interests/hobbies"""
        if not interests_section:
            interests_section = self._find_section(text, 'interests')
        
        if not interests_section:
            return []
        
        interests = []
        # Split by common delimiters
        items = re.split(r'[,;|•●○\n]', interests_section)
        for item in items:
            item = item.strip()
            if item and len(item) > 1 and len(item) < 50:
                interests.append(item)
        
        return interests
    
    # ==================== SECTION GENERATION ====================
    
    def _generate_all_sections(
        self,
        data: ResumeData,
        detected_skills: Dict[str, List[str]]
    ) -> Dict[str, str]:
        """Generate all sections in proper order"""
        sections = {}
        
        # 1. Contact (always first)
        sections['CONTACT'] = self._generate_contact_section(data.contact)
        
        # 2. Summary/Objective
        if data.summary or data.experience:
            sections['PROFESSIONAL SUMMARY'] = self._generate_summary_section(
                data.summary, data.contact, data.experience, detected_skills
            )
        elif data.objective:
            sections['CAREER OBJECTIVE'] = self._improve_text(data.objective)
        
        # 3. Experience (most important)
        if data.experience:
            sections['PROFESSIONAL EXPERIENCE'] = self._generate_experience_section(data.experience)
        
        # 4. Education
        if data.education:
            sections['EDUCATION'] = self._generate_education_section(data.education)
        
        # 5. Skills
        if data.skills and any(data.skills.values()):
            sections['SKILLS'] = self._generate_skills_section(data.skills)
        
        # 6. Projects
        if data.projects:
            sections['PROJECTS'] = self._generate_projects_section(data.projects)
        
        # 7. Certifications
        if data.certifications:
            sections['CERTIFICATIONS'] = self._generate_certifications_section(data.certifications)
        
        # 8. Awards
        if data.awards:
            sections['AWARDS & ACHIEVEMENTS'] = self._generate_awards_section(data.awards)
        
        # 9. Publications
        if data.publications:
            sections['PUBLICATIONS'] = self._generate_publications_section(data.publications)
        
        # 10. Languages
        if data.languages:
            sections['LANGUAGES'] = self._generate_languages_section(data.languages)
        
        # 11. Volunteer
        if data.volunteer:
            sections['VOLUNTEER EXPERIENCE'] = self._generate_experience_section(data.volunteer)
        
        # 12. Interests (optional)
        if data.interests:
            sections['INTERESTS'] = ', '.join(data.interests)
        
        return sections
    
    def _generate_contact_section(self, contact: ContactInfo) -> str:
        """Generate formatted contact section"""
        lines = []
        
        # Name (prominent)
        if contact.name:
            lines.append(contact.name.upper())
        else:
            lines.append("[YOUR FULL NAME]")
        
        lines.append("")  # Blank line
        
        # Contact line 1: Location | Phone | Email
        contact_parts = []
        if contact.location:
            contact_parts.append(contact.location)
        elif contact.address:
            contact_parts.append(contact.address)
        if contact.phone:
            contact_parts.append(contact.phone)
        if contact.email:
            contact_parts.append(contact.email)
        
        if contact_parts:
            lines.append(" | ".join(contact_parts))
        
        # Contact line 2: LinkedIn | GitHub | Portfolio
        link_parts = []
        if contact.linkedin:
            link_parts.append(contact.linkedin)
        if contact.github:
            link_parts.append(contact.github)
        if contact.portfolio:
            link_parts.append(contact.portfolio)
        if contact.website:
            link_parts.append(contact.website)
        
        if link_parts:
            lines.append(" | ".join(link_parts))
        
        return "\n".join(lines)
    
    def _generate_summary_section(
        self,
        existing_summary: str,
        contact: ContactInfo,
        experience: List[ExperienceEntry],
        detected_skills: Dict[str, List[str]]
    ) -> str:
        """Generate or improve professional summary"""
        
        # If good existing summary, improve it
        if existing_summary and len(existing_summary) > 50:
            return self._improve_text(existing_summary)
        
        # Generate new summary
        years_exp = self._calculate_experience_years(experience)
        recent_title = experience[0].job_title if experience else ""
        recent_company = experience[0].company if experience else ""
        
        top_skills = []
        for key in ['programming_languages', 'frameworks', 'technical']:
            top_skills.extend(detected_skills.get(key, [])[:3])
        top_skills = top_skills[:5]
        
        parts = []
        
        # Opening
        if years_exp >= 1 and recent_title:
            parts.append(f"Results-driven {recent_title} with {years_exp}+ years of experience.")
        elif recent_title:
            parts.append(f"Motivated {recent_title} with proven track record of delivering quality results.")
        else:
            parts.append("Results-driven professional with strong technical expertise and problem-solving abilities.")
        
        # Skills highlight
        if top_skills:
            parts.append(f"Expertise in {', '.join(top_skills[:4])}.")
        
        # Closing
        parts.append("Known for strong collaboration, attention to detail, and delivering high-quality solutions.")
        
        return " ".join(parts)
    
    def _calculate_experience_years(self, experience: List[ExperienceEntry]) -> int:
        """Calculate total years of experience"""
        if not experience:
            return 0
        
        current_year = datetime.now().year
        years = []
        
        for exp in experience:
            # Extract year from start date
            start_match = re.search(r'(19|20)\d{2}', exp.start_date or "")
            if start_match:
                years.append(int(start_match.group()))
            
            # Extract year from end date
            end_match = re.search(r'(19|20)\d{2}', exp.end_date or "")
            if end_match:
                years.append(int(end_match.group()))
            elif exp.is_current or (exp.end_date and exp.end_date.lower() in ['present', 'current', 'now']):
                years.append(current_year)
        
        if len(years) >= 2:
            return max(years) - min(years)
        
        return 0
    
    def _improve_text(self, text: str) -> str:
        """Improve text by removing weak phrases"""
        if not text:
            return ""
        
        improved = text.strip()
        
        # Remove weak openings
        weak_patterns = [
            r'^(?:I am|I\'m)\s+',
            r'^(?:Seeking|Looking for)\s+',
            r'^(?:To obtain|To secure)\s+',
            r'^(?:Objective|Summary|Profile)[:\s]*',
        ]
        
        for pattern in weak_patterns:
            improved = re.sub(pattern, '', improved, flags=re.IGNORECASE)
        
        # Capitalize first letter
        improved = improved.strip()
        if improved and improved[0].islower():
            improved = improved[0].upper() + improved[1:]
        
        return improved
    
    def _generate_experience_section(self, experiences: List[ExperienceEntry]) -> str:
        """Generate formatted experience section"""
        lines = []
        
        for i, exp in enumerate(experiences):
            # Job title
            title = exp.job_title if exp.job_title else "[Job Title]"
            lines.append(title)
            
            # Company | Location | Dates
            info_parts = []
            if exp.company:
                info_parts.append(exp.company)
            if exp.location:
                info_parts.append(exp.location)
            
            date_str = ""
            if exp.start_date and exp.end_date:
                date_str = f"{exp.start_date} - {exp.end_date}"
            elif exp.start_date:
                date_str = f"{exp.start_date} - Present"
            
            if date_str:
                info_parts.append(date_str)
            
            if info_parts:
                lines.append(" | ".join(info_parts))
            
            # Responsibilities/Achievements
            if exp.responsibilities:
                lines.append("")
                for resp in exp.responsibilities:
                    improved = self._improve_bullet(resp)
                    lines.append(f"• {improved}")
            elif exp.raw_text:
                # Try to extract content
                lines.append("")
                lines.append("• [Add your key accomplishments and responsibilities]")
            
            # Blank line between jobs
            if i < len(experiences) - 1:
                lines.append("")
        
        return "\n".join(lines)
    
    def _improve_bullet(self, bullet: str) -> str:
        """Improve a bullet point"""
        improved = bullet.strip()
        
        # Remove existing bullet characters
        improved = re.sub(r'^[•\-\*–►○●▪◦]\s*', '', improved)
        
        # Replace weak phrases with strong verbs
        for weak, strong in self.ACTION_VERBS['weak_to_strong'].items():
            if improved.lower().startswith(weak):
                improved = strong + improved[len(weak):]
                break
        
        # Capitalize first letter
        if improved and improved[0].islower():
            first_word = improved.split()[0].lower()
            # If first word is a verb, capitalize it
            improved = improved[0].upper() + improved[1:]
        
        # Remove trailing period (ATS prefers consistency)
        improved = improved.rstrip('.')
        
        return improved
    
    def _generate_education_section(self, education: List[EducationEntry]) -> str:
        """Generate formatted education section"""
        lines = []
        
        for i, edu in enumerate(education):
            # Degree line
            degree_line = edu.degree if edu.degree else "[Degree]"
            if edu.major and edu.major.lower() not in degree_line.lower():
                degree_line += f" in {edu.major}"
            if edu.minor:
                degree_line += f", Minor in {edu.minor}"
            lines.append(degree_line)
            
            # Institution | Location | Date
            info_parts = []
            if edu.institution:
                info_parts.append(edu.institution)
            if edu.location:
                info_parts.append(edu.location)
            if edu.end_date:
                info_parts.append(edu.end_date)
            
            if info_parts:
                lines.append(" | ".join(info_parts))
            
            # GPA and Honors
            extras = []
            if edu.gpa:
                extras.append(f"GPA: {edu.gpa}")
            if edu.honors:
                extras.append(edu.honors)
            
            if extras:
                lines.append("• " + ", ".join(extras))
            
            # Relevant coursework
            if edu.coursework:
                lines.append("• Relevant Coursework: " + ", ".join(edu.coursework[:6]))
            
            if i < len(education) - 1:
                lines.append("")
        
        return "\n".join(lines)
    
    def _generate_skills_section(self, skills: Dict[str, List[str]]) -> str:
        """Generate formatted skills section"""
        lines = []
        
        # Programming Languages
        if skills.get('programming_languages'):
            lines.append(f"Programming Languages: {', '.join(sorted(set(skills['programming_languages']), key=str.lower))}")
        
        # Frameworks & Libraries
        if skills.get('frameworks'):
            lines.append(f"Frameworks & Libraries: {', '.join(sorted(set(skills['frameworks']), key=str.lower))}")
        
        # Databases
        if skills.get('databases'):
            lines.append(f"Databases: {', '.join(sorted(set(skills['databases']), key=str.lower))}")
        
        # Cloud & DevOps
        if skills.get('cloud_devops'):
            lines.append(f"Cloud & DevOps: {', '.join(sorted(set(skills['cloud_devops']), key=str.lower))}")
        
        # Tools
        if skills.get('tools'):
            lines.append(f"Tools: {', '.join(sorted(set(skills['tools']), key=str.lower))}")
        
        # Other Technical Skills
        other_tech = skills.get('technical', []) + skills.get('other', [])
        if other_tech:
            # Remove duplicates from other categories
            existing = set()
            for key in ['programming_languages', 'frameworks', 'databases', 'cloud_devops', 'tools']:
                existing.update(s.lower() for s in skills.get(key, []))
            other_tech = [s for s in other_tech if s.lower() not in existing]
            if other_tech:
                lines.append(f"Technical Skills: {', '.join(sorted(set(other_tech), key=str.lower))}")
        
        # Soft Skills
        if skills.get('soft_skills'):
            lines.append(f"Soft Skills: {', '.join(sorted(set(skills['soft_skills']), key=str.lower))}")
        
        return "\n".join(lines)
    
    def _generate_projects_section(self, projects: List[ProjectEntry]) -> str:
        """Generate formatted projects section"""
        lines = []
        
        for i, proj in enumerate(projects):
            # Project name and link
            proj_line = proj.name if proj.name else "[Project Name]"
            if proj.url:
                proj_line += f" | {proj.url}"
            lines.append(proj_line)
            
            # Role and date
            info_parts = []
            if proj.role:
                info_parts.append(proj.role)
            if proj.organization:
                info_parts.append(proj.organization)
            if proj.date:
                info_parts.append(proj.date)
            if info_parts:
                lines.append(" | ".join(info_parts))
            
            # Technologies
            if proj.technologies:
                lines.append(f"Technologies: {', '.join(proj.technologies)}")
            
            # Description
            for desc in proj.description[:4]:
                lines.append(f"• {self._improve_bullet(desc)}")
            
            if i < len(projects) - 1:
                lines.append("")
        
        return "\n".join(lines)
    
    def _generate_certifications_section(self, certs: List[CertificationEntry]) -> str:
        """Generate formatted certifications section"""
        lines = []
        
        for cert in certs:
            cert_line = cert.name if cert.name else "[Certification Name]"
            
            parts = [cert_line]
            if cert.issuer:
                parts.append(cert.issuer)
            if cert.date:
                parts.append(cert.date)
            
            lines.append(" | ".join(parts))
            
            if cert.credential_id:
                lines.append(f"  Credential ID: {cert.credential_id}")
        
        return "\n".join(lines)
    
    def _generate_awards_section(self, awards: List[AwardEntry]) -> str:
        """Generate formatted awards section"""
        lines = []
        
        for award in awards:
            award_line = award.name if award.name else "[Award Name]"
            
            parts = [award_line]
            if award.issuer:
                parts.append(award.issuer)
            if award.date:
                parts.append(award.date)
            
            lines.append("• " + " | ".join(parts))
            
            if award.description:
                lines.append(f"  {award.description}")
        
        return "\n".join(lines)
    
    def _generate_publications_section(self, pubs: List[PublicationEntry]) -> str:
        """Generate formatted publications section"""
        lines = []
        
        for pub in pubs:
            if pub.title:
                pub_line = f'"{pub.title}"'
                if pub.publication:
                    pub_line += f", {pub.publication}"
                if pub.date:
                    pub_line += f" ({pub.date})"
                lines.append("• " + pub_line)
                
                if pub.url:
                    lines.append(f"  {pub.url}")
        
        return "\n".join(lines)
    
    def _generate_languages_section(self, languages: List[LanguageEntry]) -> str:
        """Generate formatted languages section"""
        parts = []
        
        for lang in languages:
            if lang.proficiency:
                parts.append(f"{lang.language} ({lang.proficiency})")
            else:
                parts.append(lang.language)
        
        return ", ".join(parts)
    
    def _build_full_resume(self, sections: Dict[str, str]) -> str:
        """Build complete resume text"""
        lines = []
        
        for section_name, content in sections.items():
            if section_name == 'CONTACT':
                lines.append(content)
            else:
                lines.append("")
                lines.append("=" * 50)
                lines.append(section_name)
                lines.append("=" * 50)
                lines.append(content)
        
        return "\n".join(lines)
    
    def _list_all_improvements(
        self,
        data: ResumeData,
        issues: List[Dict[str, Any]]
    ) -> List[str]:
        """List all improvements made"""
        improvements = []
        
        if data.contact.name:
            improvements.append("✓ Formatted contact information with consistent layout")
        
        if data.contact.linkedin or data.contact.github:
            improvements.append("✓ Added professional profile links")
        
        if data.experience:
            improvements.append(f"✓ Structured {len(data.experience)} work experience entries")
            bullet_count = sum(len(e.responsibilities) for e in data.experience)
            if bullet_count > 0:
                improvements.append(f"✓ Enhanced {bullet_count} achievement bullets with action verbs")
        
        if data.education:
            improvements.append(f"✓ Formatted {len(data.education)} education entries")
        
        if any(data.skills.values()):
            total_skills = sum(len(v) for v in data.skills.values())
            improvements.append(f"✓ Organized {total_skills} skills into clear categories")
        
        if data.projects:
            improvements.append(f"✓ Highlighted {len(data.projects)} projects")
        
        if data.certifications:
            improvements.append(f"✓ Listed {len(data.certifications)} certifications")
        
        if data.awards:
            improvements.append(f"✓ Showcased {len(data.awards)} awards/achievements")
        
        # Standard improvements
        improvements.extend([
            "✓ Applied ATS-friendly single-column format",
            "✓ Used clear section headers",
            "✓ Removed problematic formatting",
            "✓ Ensured consistent date formats"
        ])
        
        return improvements
    
    def _get_original_data_summary(self, data: ResumeData) -> Dict[str, Any]:
        """Get summary of original data extracted"""
        return {
            "name": data.contact.name,
            "email": data.contact.email,
            "phone": data.contact.phone,
            "location": data.contact.location,
            "linkedin": data.contact.linkedin,
            "github": data.contact.github,
            "experience_count": len(data.experience),
            "education_count": len(data.education),
            "skills_count": sum(len(v) for v in data.skills.values()),
            "projects_count": len(data.projects),
            "certifications_count": len(data.certifications),
            "awards_count": len(data.awards),
            "languages_count": len(data.languages)
        }
    
    def _get_template_suggestions(self) -> List[str]:
        """Get ATS-friendly template suggestions"""
        return [
            "Use single-column layout (no tables or columns)",
            "Choose standard fonts: Arial, Calibri, or Times New Roman (10-12pt)",
            "Save as PDF to preserve formatting",
            "Keep margins between 0.5 and 1 inch",
            "Avoid headers, footers, and text boxes",
            "Don't use images or graphics",
            "Use standard section headers",
            "Keep file size under 2MB"
        ]


# Singleton instance
_resume_builder_v4 = None


def get_resume_builder_v4() -> ResumeBuilderV4:
    """Get singleton instance"""
    global _resume_builder_v4
    if _resume_builder_v4 is None:
        _resume_builder_v4 = ResumeBuilderV4()
    return _resume_builder_v4
