"""
Standalone ATS Scoring Engine
Analyzes resume without job description - checks general ATS compatibility
Provides suggestions and generates ATS-optimized resume
"""
import re
import logging
from typing import Dict, List, Set, Tuple, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json

logger = logging.getLogger(__name__)


@dataclass
class ATSIssue:
    """Represents an ATS compatibility issue"""
    category: str
    severity: str  # 'critical', 'major', 'minor'
    issue: str
    suggestion: str
    impact_score: int  # How much this affects the score (0-10)


@dataclass 
class StandaloneScoreBreakdown:
    """Score breakdown for standalone analysis"""
    formatting: float = 0
    contact_info: float = 0
    skills_section: float = 0
    experience_section: float = 0
    education_section: float = 0
    keywords_density: float = 0
    readability: float = 0
    length_optimization: float = 0
    
    def to_dict(self) -> Dict[str, float]:
        return {
            "formatting": round(self.formatting, 2),
            "contact_info": round(self.contact_info, 2),
            "skills_section": round(self.skills_section, 2),
            "experience_section": round(self.experience_section, 2),
            "education_section": round(self.education_section, 2),
            "keywords_density": round(self.keywords_density, 2),
            "readability": round(self.readability, 2),
            "length_optimization": round(self.length_optimization, 2)
        }
    
    @property
    def total(self) -> float:
        weights = {
            "formatting": 15,
            "contact_info": 10,
            "skills_section": 20,
            "experience_section": 25,
            "education_section": 10,
            "keywords_density": 10,
            "readability": 5,
            "length_optimization": 5
        }
        
        weighted_sum = (
            (self.formatting / 100) * weights["formatting"] +
            (self.contact_info / 100) * weights["contact_info"] +
            (self.skills_section / 100) * weights["skills_section"] +
            (self.experience_section / 100) * weights["experience_section"] +
            (self.education_section / 100) * weights["education_section"] +
            (self.keywords_density / 100) * weights["keywords_density"] +
            (self.readability / 100) * weights["readability"] +
            (self.length_optimization / 100) * weights["length_optimization"]
        )
        
        return round(weighted_sum, 2)


class StandaloneATSScorer:
    """
    Standalone ATS Scorer - No job description needed
    Analyzes resume for general ATS compatibility and best practices
    """
    
    # Industry standard skills by category
    TECH_SKILLS = {
        "programming": ["python", "javascript", "java", "c++", "c#", "go", "rust", "ruby", "php", "swift", "kotlin", "typescript", "scala", "r"],
        "frontend": ["react", "angular", "vue", "html", "css", "sass", "tailwind", "bootstrap", "jquery", "webpack", "next.js", "nuxt.js"],
        "backend": ["node.js", "express", "django", "flask", "fastapi", "spring", "rails", "asp.net", "laravel", "graphql", "rest api"],
        "database": ["sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "oracle", "sqlite", "dynamodb", "cassandra"],
        "cloud": ["aws", "azure", "gcp", "docker", "kubernetes", "terraform", "jenkins", "ci/cd", "devops"],
        "data": ["machine learning", "data science", "pandas", "numpy", "tensorflow", "pytorch", "spark", "hadoop", "tableau", "power bi"],
        "tools": ["git", "jira", "confluence", "slack", "figma", "postman", "vs code", "linux", "agile", "scrum"]
    }
    
    # Soft skills
    SOFT_SKILLS = {
        "leadership", "communication", "teamwork", "problem-solving", "analytical",
        "creative", "adaptable", "organized", "detail-oriented", "time management",
        "collaboration", "mentoring", "presentation", "negotiation", "critical thinking",
        "decision making", "conflict resolution", "emotional intelligence", "initiative"
    }
    
    # Action verbs that ATS systems look for
    ACTION_VERBS = {
        "achieved", "accomplished", "administered", "analyzed", "built", "collaborated",
        "created", "delivered", "designed", "developed", "directed", "enhanced",
        "established", "executed", "generated", "implemented", "improved", "increased",
        "initiated", "launched", "led", "managed", "optimized", "organized",
        "planned", "produced", "reduced", "resolved", "spearheaded", "streamlined",
        "supervised", "trained", "transformed"
    }
    
    # Required sections
    REQUIRED_SECTIONS = ["contact", "experience", "education", "skills"]
    OPTIONAL_SECTIONS = ["summary", "certifications", "projects", "achievements"]
    
    def __init__(self):
        self.nlp = None
        self._load_models()
    
    def _load_models(self):
        """Load NLP models"""
        try:
            import spacy
            self.nlp = spacy.load("en_core_web_md")
            logger.info("spaCy model loaded for standalone scorer")
        except Exception as e:
            logger.warning(f"Could not load spaCy model: {e}")
            self.nlp = None
    
    def analyze_resume(
        self,
        resume_text: str,
        resume_sections: Dict[str, str],
        file_format: str = "pdf"
    ) -> Dict[str, Any]:
        """
        Analyze resume for ATS compatibility without job description
        
        Returns comprehensive analysis including:
        - Overall score
        - Category breakdowns
        - Issues found
        - Detailed suggestions
        - Optimized resume content
        """
        
        issues: List[ATSIssue] = []
        scores = StandaloneScoreBreakdown()
        
        # 1. Formatting Analysis (15%)
        scores.formatting, format_issues = self._analyze_formatting(
            resume_text, file_format
        )
        issues.extend(format_issues)
        
        # 2. Contact Information (10%)
        scores.contact_info, contact_issues = self._analyze_contact_info(
            resume_text, resume_sections.get("contact", "")
        )
        issues.extend(contact_issues)
        
        # 3. Skills Section (20%)
        scores.skills_section, skills_issues, detected_skills = self._analyze_skills(
            resume_text, resume_sections.get("skills", "")
        )
        issues.extend(skills_issues)
        
        # 4. Experience Section (25%)
        scores.experience_section, exp_issues = self._analyze_experience(
            resume_sections.get("experience", "")
        )
        issues.extend(exp_issues)
        
        # 5. Education Section (10%)
        scores.education_section, edu_issues = self._analyze_education(
            resume_sections.get("education", "")
        )
        issues.extend(edu_issues)
        
        # 6. Keywords Density (10%)
        scores.keywords_density, keyword_issues = self._analyze_keywords(
            resume_text, detected_skills
        )
        issues.extend(keyword_issues)
        
        # 7. Readability (5%)
        scores.readability, read_issues = self._analyze_readability(resume_text)
        issues.extend(read_issues)
        
        # 8. Length Optimization (5%)
        scores.length_optimization, length_issues = self._analyze_length(resume_text)
        issues.extend(length_issues)
        
        # Generate prioritized suggestions
        suggestions = self._generate_suggestions(issues)
        
        # Generate optimized resume using V4 builder (complete accurate version)
        from app.services.resume_builder_v4 import get_resume_builder_v4
        builder = get_resume_builder_v4()
        optimized_resume = builder.build_optimized_resume(
            resume_text, 
            resume_sections, 
            detected_skills,
            [self._issue_to_dict(i) for i in issues]
        )
        
        return {
            "total_score": scores.total,
            "score_details": scores.to_dict(),
            "issues": [self._issue_to_dict(i) for i in issues],
            "suggestions": suggestions,
            "detected_skills": detected_skills,
            "optimized_resume": optimized_resume,
            "grade": self._get_grade(scores.total),
            "summary": self._generate_summary(scores, issues)
        }
    
    def _analyze_formatting(
        self, 
        text: str, 
        file_format: str
    ) -> Tuple[float, List[ATSIssue]]:
        """Analyze resume formatting for ATS compatibility"""
        issues = []
        score = 100
        
        # Check file format
        if file_format.lower() not in ["pdf", "docx"]:
            issues.append(ATSIssue(
                category="formatting",
                severity="critical",
                issue=f"File format '{file_format}' may not be ATS-friendly",
                suggestion="Use PDF or DOCX format for best ATS compatibility",
                impact_score=10
            ))
            score -= 30
        
        # Check for tables (indicated by excessive spacing patterns)
        if re.search(r'\t{2,}|\s{5,}', text):
            issues.append(ATSIssue(
                category="formatting",
                severity="major",
                issue="Detected possible tables or complex formatting",
                suggestion="Use simple single-column layout without tables",
                impact_score=7
            ))
            score -= 15
        
        # Check for special characters that might confuse ATS
        special_chars = re.findall(r'[^\x00-\x7F]', text)
        if len(special_chars) > 10:
            issues.append(ATSIssue(
                category="formatting",
                severity="minor",
                issue=f"Found {len(special_chars)} special characters",
                suggestion="Replace special characters with standard ASCII equivalents",
                impact_score=3
            ))
            score -= 5
        
        # Check for consistent formatting
        lines = text.split('\n')
        empty_lines = sum(1 for l in lines if not l.strip())
        if empty_lines > len(lines) * 0.3:
            issues.append(ATSIssue(
                category="formatting",
                severity="minor",
                issue="Excessive white space detected",
                suggestion="Reduce unnecessary blank lines to improve readability",
                impact_score=2
            ))
            score -= 5
        
        # Check for headers/sections
        header_patterns = r'^(?:experience|education|skills|summary|objective|projects|certifications)'
        headers_found = len(re.findall(header_patterns, text.lower(), re.MULTILINE))
        if headers_found < 3:
            issues.append(ATSIssue(
                category="formatting",
                severity="major",
                issue="Missing clear section headers",
                suggestion="Add clear section headers: EXPERIENCE, EDUCATION, SKILLS, SUMMARY",
                impact_score=8
            ))
            score -= 20
        
        return max(0, score), issues
    
    def _analyze_contact_info(
        self,
        text: str,
        contact_section: str
    ) -> Tuple[float, List[ATSIssue]]:
        """Analyze contact information completeness"""
        issues = []
        score = 100
        text_lower = (contact_section or text).lower()
        
        # Check for email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if not re.search(email_pattern, text):
            issues.append(ATSIssue(
                category="contact",
                severity="critical",
                issue="No email address found",
                suggestion="Add a professional email address (e.g., firstname.lastname@email.com)",
                impact_score=10
            ))
            score -= 40
        
        # Check for phone
        phone_pattern = r'[\+]?[(]?[0-9]{1,3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}'
        if not re.search(phone_pattern, text):
            issues.append(ATSIssue(
                category="contact",
                severity="major",
                issue="No phone number found",
                suggestion="Add a contact phone number with country code",
                impact_score=7
            ))
            score -= 25
        
        # Check for LinkedIn
        if "linkedin" not in text_lower:
            issues.append(ATSIssue(
                category="contact",
                severity="minor",
                issue="No LinkedIn profile found",
                suggestion="Add your LinkedIn profile URL to improve credibility",
                impact_score=3
            ))
            score -= 10
        
        # Check for location
        location_keywords = ["city", "state", "country", "location", ","]
        has_location = any(kw in text_lower for kw in location_keywords)
        if not has_location and not re.search(r'\b[A-Z][a-z]+,\s*[A-Z]{2}\b', text):
            issues.append(ATSIssue(
                category="contact",
                severity="minor",
                issue="No location information found",
                suggestion="Add city and state/country (e.g., 'San Francisco, CA')",
                impact_score=2
            ))
            score -= 10
        
        return max(0, score), issues
    
    def _analyze_skills(
        self,
        text: str,
        skills_section: str
    ) -> Tuple[float, List[ATSIssue], Dict[str, List[str]]]:
        """Analyze skills section and detect skills"""
        issues = []
        score = 100
        text_lower = text.lower()
        detected_skills: Dict[str, List[str]] = {
            "technical": [],
            "soft": [],
            "tools": []
        }
        
        # Check if skills section exists
        if not skills_section and "skills" not in text_lower:
            issues.append(ATSIssue(
                category="skills",
                severity="critical",
                issue="No dedicated skills section found",
                suggestion="Add a clear 'SKILLS' section listing your technical and soft skills",
                impact_score=10
            ))
            score -= 40
        
        # Detect technical skills
        for category, skills in self.TECH_SKILLS.items():
            for skill in skills:
                if skill.lower() in text_lower:
                    detected_skills["technical"].append(skill)
        
        # Detect soft skills
        for skill in self.SOFT_SKILLS:
            if skill.lower() in text_lower:
                detected_skills["soft"].append(skill)
        
        # Check skill count
        total_skills = len(detected_skills["technical"]) + len(detected_skills["soft"])
        
        if total_skills < 5:
            issues.append(ATSIssue(
                category="skills",
                severity="major",
                issue=f"Only {total_skills} skills detected - too few for most positions",
                suggestion="Add more relevant skills. Most resumes should have 10-20 skills listed",
                impact_score=8
            ))
            score -= 30
        elif total_skills < 10:
            issues.append(ATSIssue(
                category="skills",
                severity="minor",
                issue=f"Found {total_skills} skills - consider adding more",
                suggestion="Aim for 10-20 relevant skills for better ATS matching",
                impact_score=3
            ))
            score -= 10
        
        # Check for skill organization
        if skills_section:
            if not any(cat in skills_section.lower() for cat in ["technical", "programming", "software", "tools", "languages"]):
                issues.append(ATSIssue(
                    category="skills",
                    severity="minor",
                    issue="Skills not categorized",
                    suggestion="Organize skills into categories (e.g., 'Programming Languages:', 'Tools:', 'Frameworks:')",
                    impact_score=2
                ))
                score -= 5
        
        return max(0, score), issues, detected_skills
    
    def _analyze_experience(
        self,
        experience_section: str
    ) -> Tuple[float, List[ATSIssue]]:
        """Analyze experience section quality"""
        issues = []
        score = 100
        
        if not experience_section:
            issues.append(ATSIssue(
                category="experience",
                severity="critical",
                issue="No experience section found",
                suggestion="Add a detailed work experience section with job titles, companies, dates, and achievements",
                impact_score=10
            ))
            return 0, issues
        
        exp_lower = experience_section.lower()
        
        # Check for action verbs
        action_verb_count = sum(1 for verb in self.ACTION_VERBS if verb in exp_lower)
        if action_verb_count < 3:
            issues.append(ATSIssue(
                category="experience",
                severity="major",
                issue="Few action verbs found in experience descriptions",
                suggestion="Start bullet points with strong action verbs: 'Developed', 'Implemented', 'Managed', 'Led', 'Achieved'",
                impact_score=7
            ))
            score -= 20
        
        # Check for quantifiable achievements
        number_pattern = r'\d+%|\$[\d,]+|\d+\s*(users|customers|clients|projects|team|people|years)'
        metrics = re.findall(number_pattern, experience_section, re.IGNORECASE)
        if len(metrics) < 2:
            issues.append(ATSIssue(
                category="experience",
                severity="major",
                issue="Lack of quantifiable achievements",
                suggestion="Add metrics and numbers: 'Increased sales by 25%', 'Managed team of 10', 'Reduced costs by $50K'",
                impact_score=8
            ))
            score -= 25
        
        # Check for dates
        date_pattern = r'(?:19|20)\d{2}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*'
        dates = re.findall(date_pattern, experience_section, re.IGNORECASE)
        if len(dates) < 2:
            issues.append(ATSIssue(
                category="experience",
                severity="major",
                issue="Missing or unclear employment dates",
                suggestion="Include clear date ranges for each position (e.g., 'Jan 2020 - Present')",
                impact_score=6
            ))
            score -= 15
        
        # Check for job titles
        title_keywords = ["engineer", "developer", "manager", "analyst", "designer", "specialist", "lead", "director", "coordinator"]
        has_titles = any(title in exp_lower for title in title_keywords)
        if not has_titles:
            issues.append(ATSIssue(
                category="experience",
                severity="minor",
                issue="Job titles not clearly stated",
                suggestion="Use standard industry job titles that ATS can recognize",
                impact_score=4
            ))
            score -= 10
        
        return max(0, score), issues
    
    def _analyze_education(
        self,
        education_section: str
    ) -> Tuple[float, List[ATSIssue]]:
        """Analyze education section"""
        issues = []
        score = 100
        
        if not education_section:
            issues.append(ATSIssue(
                category="education",
                severity="major",
                issue="No education section found",
                suggestion="Add an education section with degree, institution, and graduation date",
                impact_score=7
            ))
            return 30, issues  # Some score for experienced professionals
        
        edu_lower = education_section.lower()
        
        # Check for degree
        degree_keywords = ["bachelor", "master", "phd", "doctorate", "associate", "b.s.", "b.a.", "m.s.", "m.a.", "mba", "degree"]
        has_degree = any(deg in edu_lower for deg in degree_keywords)
        if not has_degree:
            issues.append(ATSIssue(
                category="education",
                severity="minor",
                issue="Degree type not clearly specified",
                suggestion="Clearly state your degree (e.g., 'Bachelor of Science in Computer Science')",
                impact_score=3
            ))
            score -= 15
        
        # Check for graduation date
        year_pattern = r'(?:19|20)\d{2}'
        years = re.findall(year_pattern, education_section)
        if not years:
            issues.append(ATSIssue(
                category="education",
                severity="minor",
                issue="Graduation date not specified",
                suggestion="Add graduation year or expected graduation date",
                impact_score=2
            ))
            score -= 10
        
        return max(0, score), issues
    
    def _analyze_keywords(
        self,
        text: str,
        detected_skills: Dict[str, List[str]]
    ) -> Tuple[float, List[ATSIssue]]:
        """Analyze keyword density and distribution"""
        issues = []
        score = 100
        
        words = text.lower().split()
        total_words = len(words)
        
        if total_words == 0:
            return 0, issues
        
        # Calculate keyword density
        skill_mentions = sum(
            len([w for w in words if skill.lower() in w.lower()])
            for skills in detected_skills.values()
            for skill in skills
        )
        
        density = skill_mentions / total_words
        
        if density < 0.02:
            issues.append(ATSIssue(
                category="keywords",
                severity="major",
                issue="Low keyword density - skills not mentioned enough",
                suggestion="Naturally incorporate your key skills throughout the resume, not just in the skills section",
                impact_score=6
            ))
            score -= 30
        elif density > 0.15:
            issues.append(ATSIssue(
                category="keywords",
                severity="minor",
                issue="Possible keyword stuffing detected",
                suggestion="Reduce repetition of keywords - use natural language",
                impact_score=3
            ))
            score -= 15
        
        return max(0, score), issues
    
    def _analyze_readability(self, text: str) -> Tuple[float, List[ATSIssue]]:
        """Analyze text readability"""
        issues = []
        score = 100
        
        sentences = re.split(r'[.!?]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return 50, issues
        
        # Check average sentence length
        avg_words = sum(len(s.split()) for s in sentences) / len(sentences)
        
        if avg_words > 25:
            issues.append(ATSIssue(
                category="readability",
                severity="minor",
                issue="Sentences are too long on average",
                suggestion="Use shorter, punchier sentences. Aim for 15-20 words per sentence",
                impact_score=2
            ))
            score -= 15
        
        # Check for bullet points
        bullet_pattern = r'^[\•\-\*\→\►]|\n[\•\-\*\→\►]'
        bullets = len(re.findall(bullet_pattern, text))
        if bullets < 5:
            issues.append(ATSIssue(
                category="readability",
                severity="minor",
                issue="Few bullet points used",
                suggestion="Use bullet points to make achievements scannable by ATS and recruiters",
                impact_score=3
            ))
            score -= 10
        
        return max(0, score), issues
    
    def _analyze_length(self, text: str) -> Tuple[float, List[ATSIssue]]:
        """Analyze resume length"""
        issues = []
        score = 100
        
        words = len(text.split())
        
        if words < 200:
            issues.append(ATSIssue(
                category="length",
                severity="major",
                issue=f"Resume too short ({words} words)",
                suggestion="Add more detail. A good resume should be 400-800 words for 1 page, or 800-1200 for 2 pages",
                impact_score=7
            ))
            score -= 40
        elif words > 1500:
            issues.append(ATSIssue(
                category="length",
                severity="minor",
                issue=f"Resume may be too long ({words} words)",
                suggestion="Consider trimming to most relevant experience. Most resumes should be 1-2 pages",
                impact_score=3
            ))
            score -= 15
        
        return max(0, score), issues
    
    def _generate_suggestions(self, issues: List[ATSIssue]) -> List[Dict[str, Any]]:
        """Generate prioritized suggestions from issues"""
        # Sort by severity and impact
        severity_order = {"critical": 0, "major": 1, "minor": 2}
        sorted_issues = sorted(
            issues,
            key=lambda x: (severity_order.get(x.severity, 3), -x.impact_score)
        )
        
        suggestions = []
        for issue in sorted_issues:
            suggestions.append({
                "priority": issue.severity,
                "category": issue.category,
                "issue": issue.issue,
                "suggestion": issue.suggestion,
                "impact": "high" if issue.impact_score >= 7 else "medium" if issue.impact_score >= 4 else "low"
            })
        
        return suggestions
    
    def _generate_optimized_resume(
        self,
        original_text: str,
        sections: Dict[str, str],
        issues: List[ATSIssue],
        detected_skills: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """Generate an ATS-optimized version of the resume using actual user data"""
        
        optimized = {
            "sections": {},
            "improvements": [],
            "template_suggestions": []
        }
        
        # Extract contact info from original text
        contact_info = self._extract_contact_from_text(original_text)
        
        # Generate optimized contact section with actual data
        optimized["sections"]["contact"] = self._optimize_contact_with_data(
            sections.get("contact", ""),
            contact_info,
            original_text
        )
        
        # Generate optimized summary using actual resume content
        all_skills = detected_skills.get("technical", []) + detected_skills.get("soft", [])
        optimized["sections"]["summary"] = self._generate_summary_from_content(
            sections.get("summary", ""),
            sections.get("experience", ""),
            all_skills[:10],
            original_text
        )
        
        # Generate optimized skills section with actual detected skills
        optimized["sections"]["skills"] = self._optimize_skills_with_data(
            sections.get("skills", ""),
            detected_skills
        )
        
        # Generate optimized experience with actual data
        optimized["sections"]["experience"] = self._optimize_experience_with_data(
            sections.get("experience", "")
        )
        
        # Generate optimized education with actual data
        optimized["sections"]["education"] = self._optimize_education_with_data(
            sections.get("education", "")
        )
        
        # Track improvements made
        optimized["improvements"] = self._track_improvements(sections, detected_skills, issues)
        
        # Add template suggestions
        optimized["template_suggestions"] = [
            "Use a single-column layout for best ATS parsing",
            "Use standard section headers: SUMMARY, SKILLS, EXPERIENCE, EDUCATION",
            "Use common fonts: Arial, Calibri, Times New Roman (10-12pt)",
            "Save as PDF for best compatibility",
            "Avoid headers, footers, and text boxes"
        ]
        
        return optimized
    
    def _extract_contact_from_text(self, text: str) -> Dict[str, str]:
        """Extract actual contact info from resume text"""
        contact = {}
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            contact["email"] = email_match.group()
        
        # Extract phone
        phone_patterns = [
            r'[\+]?[1]?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}',
            r'[\+]?[0-9]{1,3}[-.\s]?[0-9]{4,5}[-.\s]?[0-9]{4,6}'
        ]
        for pattern in phone_patterns:
            phone_match = re.search(pattern, text)
            if phone_match:
                contact["phone"] = phone_match.group().strip()
                break
        
        # Extract LinkedIn
        linkedin_pattern = r'linkedin\.com/in/([a-zA-Z0-9-]+)'
        linkedin_match = re.search(linkedin_pattern, text, re.IGNORECASE)
        if linkedin_match:
            contact["linkedin"] = f"linkedin.com/in/{linkedin_match.group(1)}"
        
        # Extract GitHub
        github_pattern = r'github\.com/([a-zA-Z0-9-]+)'
        github_match = re.search(github_pattern, text, re.IGNORECASE)
        if github_match:
            contact["github"] = f"github.com/{github_match.group(1)}"
        
        # Extract name (usually at the beginning, in title case)
        lines = text.strip().split('\n')
        for line in lines[:5]:
            line = line.strip()
            # Skip empty lines and lines that look like headers
            if not line or len(line) < 3:
                continue
            # Check if line looks like a name (2-4 words, title case)
            words = line.split()
            if 2 <= len(words) <= 4:
                # Check if words are capitalized (name pattern)
                if all(w[0].isupper() for w in words if w.isalpha()):
                    # Avoid common headers
                    if line.lower() not in ["professional experience", "work experience", "education", "skills", "summary"]:
                        contact["name"] = line
                        break
        
        # Extract location (city, state pattern)
        location_pattern = r'([A-Z][a-z]+(?:\s[A-Z][a-z]+)?),?\s*([A-Z]{2})\b'
        location_match = re.search(location_pattern, text)
        if location_match:
            contact["location"] = f"{location_match.group(1)}, {location_match.group(2)}"
        
        return contact
    
    def _optimize_contact_with_data(
        self,
        contact_section: str,
        contact_info: Dict[str, str],
        original_text: str
    ) -> str:
        """Generate optimized contact section using actual user data"""
        name = contact_info.get("name", "")
        email = contact_info.get("email", "")
        phone = contact_info.get("phone", "")
        location = contact_info.get("location", "")
        linkedin = contact_info.get("linkedin", "")
        github = contact_info.get("github", "")
        
        # Build contact section
        lines = []
        
        if name:
            lines.append(name.upper())
        
        contact_line_parts = []
        if location:
            contact_line_parts.append(location)
        if phone:
            contact_line_parts.append(phone)
        if email:
            contact_line_parts.append(email)
        
        if contact_line_parts:
            lines.append(" | ".join(contact_line_parts))
        
        links_parts = []
        if linkedin:
            links_parts.append(f"LinkedIn: {linkedin}")
        if github:
            links_parts.append(f"GitHub: {github}")
        
        if links_parts:
            lines.append(" | ".join(links_parts))
        
        return "\n".join(lines) if lines else self._fallback_contact()
    
    def _fallback_contact(self) -> str:
        """Fallback if no contact info found"""
        return """[Your Full Name]
[City, State] | [Phone Number] | [Email]
LinkedIn: linkedin.com/in/yourprofile"""
    
    def _generate_summary_from_content(
        self,
        existing_summary: str,
        experience: str,
        top_skills: List[str],
        original_text: str
    ) -> str:
        """Generate ATS-friendly summary from actual resume content"""
        
        # Try to extract years of experience
        years_exp = self._extract_years_experience(experience, original_text)
        
        # Try to extract job titles from experience
        job_titles = self._extract_job_titles(experience)
        main_title = job_titles[0] if job_titles else ""
        
        # Build optimized summary
        skills_text = ", ".join(top_skills[:5]) if top_skills else ""
        
        # If existing summary exists, optimize it
        if existing_summary and len(existing_summary) > 50:
            # Clean and improve existing summary
            summary = self._improve_summary_text(existing_summary, top_skills, years_exp, main_title)
        else:
            # Generate new summary from extracted info
            summary = self._generate_new_summary(years_exp, main_title, skills_text, experience)
        
        return summary
    
    def _extract_years_experience(self, experience: str, full_text: str) -> str:
        """Extract years of experience from resume"""
        # Look for explicit mentions
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'(\d+)\+?\s*years?\s*(?:of\s*)?professional',
            r'over\s*(\d+)\s*years?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                return f"{match.group(1)}+"
        
        # Try to calculate from date ranges
        year_pattern = r'\b(20\d{2}|19\d{2})\b'
        years = re.findall(year_pattern, experience or full_text)
        
        if years:
            years = [int(y) for y in years]
            years_diff = max(years) - min(years)
            if years_diff > 0:
                return str(years_diff)
        
        return ""
    
    def _extract_job_titles(self, experience: str) -> List[str]:
        """Extract job titles from experience section"""
        common_titles = [
            "software engineer", "developer", "programmer", "architect",
            "manager", "director", "lead", "senior", "junior", "analyst",
            "consultant", "designer", "administrator", "specialist",
            "coordinator", "associate", "intern", "technician", "engineer"
        ]
        
        titles_found = []
        lines = experience.split('\n') if experience else []
        
        for line in lines:
            line_lower = line.lower().strip()
            # Check if line contains job title keywords
            for title in common_titles:
                if title in line_lower and len(line.strip()) < 100:
                    # This line might be a job title
                    titles_found.append(line.strip())
                    break
        
        return titles_found[:3]  # Return top 3 titles
    
    def _improve_summary_text(
        self,
        existing: str,
        skills: List[str],
        years: str,
        title: str
    ) -> str:
        """Improve existing summary text"""
        summary = existing.strip()
        
        # Remove weak phrases
        weak_phrases = [
            "seeking", "looking for", "I am", "I'm", 
            "objective:", "summary:", "profile:"
        ]
        for phrase in weak_phrases:
            summary = re.sub(phrase, "", summary, flags=re.IGNORECASE)
        
        # Clean up
        summary = re.sub(r'\s+', ' ', summary).strip()
        
        # If too short, enhance it
        if len(summary) < 100 and skills:
            skills_mention = f" Skilled in {', '.join(skills[:3])}." if skills else ""
            summary = summary.rstrip('.') + "." + skills_mention
        
        return summary
    
    def _generate_new_summary(
        self,
        years: str,
        title: str,
        skills_text: str,
        experience: str
    ) -> str:
        """Generate new summary when existing is missing or poor"""
        parts = []
        
        if years and title:
            parts.append(f"Results-driven professional with {years} years of experience as a {title}.")
        elif years:
            parts.append(f"Results-driven professional with {years} years of experience.")
        elif title:
            parts.append(f"Experienced {title} with a proven track record of delivering results.")
        else:
            parts.append("Results-driven professional with proven expertise in delivering high-quality solutions.")
        
        if skills_text:
            parts.append(f"Skilled in {skills_text}.")
        
        parts.append("Strong problem-solving abilities with excellent collaboration and communication skills.")
        
        return " ".join(parts)
    
    def _optimize_skills_with_data(
        self,
        skills_section: str,
        detected_skills: Dict[str, List[str]]
    ) -> str:
        """Generate optimized skills section with actual detected skills"""
        tech_skills = detected_skills.get("technical", [])
        soft_skills = detected_skills.get("soft", [])
        tools = detected_skills.get("tools", [])
        
        output_lines = []
        
        # Combine technical skills and tools for a strong technical section
        all_tech = list(set(tech_skills + tools))
        
        if all_tech:
            # Group skills logically
            output_lines.append(f"Technical Skills: {', '.join(sorted(all_tech, key=str.lower))}")
        
        if soft_skills:
            output_lines.append(f"Soft Skills: {', '.join(sorted(soft_skills, key=str.lower))}")
        
        # If we extracted some skills from section but didn't detect them, include raw content
        if not all_tech and not soft_skills and skills_section:
            # Clean and format existing skills
            cleaned = self._clean_skills_text(skills_section)
            if cleaned:
                output_lines.append(cleaned)
        
        return "\n".join(output_lines) if output_lines else "Technical Skills: [Your skills to be added]\nSoft Skills: Leadership, Communication, Problem-solving"
    
    def _clean_skills_text(self, text: str) -> str:
        """Clean up skills text"""
        # Remove common headers
        text = re.sub(r'^(?:skills|technical skills|core competencies)[:\s]*', '', text, flags=re.IGNORECASE)
        # Normalize separators
        text = re.sub(r'[•●○◦▪■□►]', ',', text)
        text = re.sub(r'\s*[,;|]\s*', ', ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _optimize_experience_with_data(self, experience_text: str) -> str:
        """Generate optimized experience section using actual user data"""
        if not experience_text or len(experience_text.strip()) < 50:
            return self._experience_template()
        
        lines = experience_text.split('\n')
        optimized_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                optimized_lines.append("")
                continue
            
            # Improve bullet points
            improved_line = self._improve_bullet_point(line)
            optimized_lines.append(improved_line)
        
        result = '\n'.join(optimized_lines)
        
        # Add tips at the end
        result += "\n\n[TIP: Start each bullet with strong action verbs and include metrics where possible]"
        
        return result
    
    def _improve_bullet_point(self, line: str) -> str:
        """Improve a single bullet point for ATS optimization"""
        # Remove existing bullets
        line = re.sub(r'^[•●○◦▪■□►\-\*]\s*', '', line)
        
        # If line starts with lowercase, check if it should be an action verb
        words = line.split()
        if not words:
            return line
        
        first_word = words[0].lower()
        
        # Convert weak starts to action verbs
        weak_to_strong = {
            "responsible for": "Managed",
            "duties included": "Executed",
            "helped": "Assisted",
            "worked on": "Developed",
            "was part of": "Collaborated with team to",
            "did": "Executed"
        }
        
        for weak, strong in weak_to_strong.items():
            if line.lower().startswith(weak):
                line = strong + line[len(weak):]
                break
        
        # Add bullet if this looks like an accomplishment
        if len(line) > 20 and not line[0].isdigit():
            line = "• " + line
        
        return line
    
    def _experience_template(self) -> str:
        """Fallback template when no experience data found"""
        return """[Job Title]
[Company Name] | [Location] | [Start Date] - [End Date]
• [Action verb] + [specific task] + [measurable result]
• Developed and implemented solutions that improved [metric] by [X%]
• Collaborated with cross-functional teams to deliver [project/result]"""
    
    def _optimize_education_with_data(self, education_text: str) -> str:
        """Generate optimized education section using actual user data"""
        if not education_text or len(education_text.strip()) < 20:
            return self._education_template()
        
        # Clean and format education
        lines = education_text.split('\n')
        optimized_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Clean up line
            line = re.sub(r'^[•●○◦▪■□►\-\*]\s*', '', line)
            
            # Detect degree patterns and format consistently
            optimized_lines.append(line)
        
        return '\n'.join(optimized_lines) if optimized_lines else self._education_template()
    
    def _education_template(self) -> str:
        """Fallback template for education"""
        return """[Degree] in [Field of Study]
[University Name] | [Graduation Year]
• Relevant coursework, honors, or achievements"""
    
    def _track_improvements(
        self,
        sections: Dict[str, str],
        detected_skills: Dict[str, List[str]],
        issues: List[ATSIssue]
    ) -> List[str]:
        """Track improvements made to the resume"""
        improvements = []
        
        # Check what was improved
        if detected_skills.get("technical"):
            improvements.append("Organized technical skills")
        
        if detected_skills.get("soft"):
            improvements.append("Highlighted soft skills")
        
        # Check critical issues being addressed
        critical_issues = [i for i in issues if i.severity == "critical"]
        for issue in critical_issues[:3]:
            if "contact" in issue.category.lower():
                improvements.append("Formatted contact information")
            elif "formatting" in issue.category.lower():
                improvements.append("Improved formatting")
            elif "action" in issue.suggestion.lower():
                improvements.append("Added action verbs")
        
        # Add generic improvements
        improvements.append("ATS-friendly formatting applied")
        improvements.append("Clear section headers added")
        
        return list(set(improvements))
    
    def _issue_to_dict(self, issue: ATSIssue) -> Dict[str, Any]:
        """Convert ATSIssue to dictionary"""
        return {
            "category": issue.category,
            "severity": issue.severity,
            "issue": issue.issue,
            "suggestion": issue.suggestion,
            "impact_score": issue.impact_score
        }
    
    def _get_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 90:
            return "A+"
        elif score >= 85:
            return "A"
        elif score >= 80:
            return "A-"
        elif score >= 75:
            return "B+"
        elif score >= 70:
            return "B"
        elif score >= 65:
            return "B-"
        elif score >= 60:
            return "C+"
        elif score >= 55:
            return "C"
        elif score >= 50:
            return "C-"
        elif score >= 45:
            return "D"
        else:
            return "F"
    
    def _generate_summary(
        self,
        scores: StandaloneScoreBreakdown,
        issues: List[ATSIssue]
    ) -> str:
        """Generate human-readable summary"""
        critical_count = sum(1 for i in issues if i.severity == "critical")
        major_count = sum(1 for i in issues if i.severity == "major")
        
        if scores.total >= 80:
            status = "Your resume is well-optimized for ATS systems."
        elif scores.total >= 60:
            status = "Your resume has good ATS compatibility but needs some improvements."
        elif scores.total >= 40:
            status = "Your resume needs significant improvements for better ATS performance."
        else:
            status = "Your resume has major ATS compatibility issues that need immediate attention."
        
        if critical_count > 0:
            status += f" Found {critical_count} critical issue(s) to fix."
        if major_count > 0:
            status += f" Found {major_count} major issue(s) to address."
        
        return status
