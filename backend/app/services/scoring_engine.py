"""
ATS Scoring Engine
Main scoring service using local NLP models (no external APIs)
"""
import re
import logging
from typing import Dict, List, Set, Tuple, Any
from dataclasses import dataclass
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class ScoreBreakdown:
    """Score breakdown by category"""
    technical: float = 0
    experience: float = 0
    education: float = 0
    certifications: float = 0
    soft_skills: float = 0
    semantic: float = 0
    format: float = 0
    
    def to_dict(self) -> Dict[str, float]:
        return {
            "technical": round(self.technical, 2),
            "experience": round(self.experience, 2),
            "education": round(self.education, 2),
            "certifications": round(self.certifications, 2),
            "soft_skills": round(self.soft_skills, 2),
            "semantic": round(self.semantic, 2),
            "format": round(self.format, 2)
        }
    
    @property
    def total(self) -> float:
        return round(
            self.technical + self.experience + self.education +
            self.certifications + self.soft_skills + self.semantic + self.format,
            2
        )


class ATSScoringEngine:
    """
    Production-grade ATS Scoring Engine
    Uses local NLP models (spaCy, sentence-transformers)
    No external API keys required
    """
    
    # Scoring weights
    WEIGHTS = {
        "technical": 35,      # Technical skills match
        "experience": 20,     # Work experience match
        "education": 15,      # Education requirements
        "certifications": 10, # Certifications
        "soft_skills": 5,     # Soft skills
        "semantic": 10,       # Section-wise semantic similarity
        "format": 10          # ATS format compatibility
    }
    
    # Common technical skills
    TECH_SKILLS = {
        "python", "javascript", "java", "c++", "c#", "go", "rust", "ruby", "php",
        "react", "angular", "vue", "nodejs", "express", "django", "flask", "fastapi",
        "spring", "docker", "kubernetes", "aws", "gcp", "azure", "sql", "mysql",
        "postgresql", "mongodb", "redis", "elasticsearch", "git", "linux", "html",
        "css", "typescript", "graphql", "rest", "api", "microservices", "terraform"
    }
    
    # Soft skills
    SOFT_SKILLS = {
        "leadership", "communication", "teamwork", "problem solving", "analytical",
        "creative", "adaptable", "flexible", "organized", "detail oriented",
        "time management", "collaboration", "mentoring", "presentation"
    }
    
    # Education keywords
    EDUCATION_KEYWORDS = {
        "bachelor", "master", "phd", "doctorate", "degree", "b.s.", "m.s.", "b.a.",
        "m.a.", "mba", "computer science", "engineering", "university", "college"
    }
    
    # Certification keywords
    CERT_KEYWORDS = {
        "certified", "certification", "aws certified", "azure certified", "gcp certified",
        "pmp", "scrum master", "cissp", "comptia", "oracle certified"
    }
    
    def __init__(self):
        self.nlp = None
        self.sentence_model = None
        self._load_models()
    
    def _load_models(self):
        """Load NLP models"""
        try:
            import spacy
            self.nlp = spacy.load("en_core_web_md")
            logger.info("spaCy model loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load spaCy model: {e}. Using basic matching.")
            self.nlp = None
        
        try:
            from sentence_transformers import SentenceTransformer
            self.sentence_model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("Sentence Transformer model loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load Sentence Transformer: {e}. Semantic matching disabled.")
            self.sentence_model = None
    
    def calculate_score(
        self,
        resume_text: str,
        resume_sections: Dict[str, str],
        job_description: str,
        format_score: float = 10.0
    ) -> Tuple[ScoreBreakdown, List[str], List[str], List[str]]:
        """
        Calculate ATS score for resume against job description
        
        Returns:
            - ScoreBreakdown: Detailed score breakdown
            - matched_keywords: List of matched keywords
            - missing_keywords: List of missing keywords
            - suggestions: List of improvement suggestions
        """
        
        # Extract keywords from job description
        jd_keywords = self._extract_keywords(job_description)
        resume_keywords = self._extract_keywords(resume_text)
        
        # Initialize score breakdown
        scores = ScoreBreakdown()
        matched_keywords = []
        missing_keywords = []
        suggestions = []
        
        # 1. Technical Skills Score (35%)
        tech_score, tech_matched, tech_missing = self._score_technical_skills(
            resume_keywords, jd_keywords
        )
        scores.technical = tech_score * (self.WEIGHTS["technical"] / 100)
        matched_keywords.extend(tech_matched)
        missing_keywords.extend(tech_missing)
        
        # 2. Experience Score (20%)
        resume_exp = resume_sections.get("experience", "")
        exp_score, exp_suggestions = self._score_experience(resume_exp, job_description)
        scores.experience = exp_score * (self.WEIGHTS["experience"] / 100)
        suggestions.extend(exp_suggestions)
        
        # 3. Education Score (15%)
        resume_edu = resume_sections.get("education", "")
        edu_score = self._score_education(resume_edu, job_description)
        scores.education = edu_score * (self.WEIGHTS["education"] / 100)
        
        # 4. Certifications Score (10%)
        cert_score, cert_matched, cert_missing = self._score_certifications(
            resume_text, job_description
        )
        scores.certifications = cert_score * (self.WEIGHTS["certifications"] / 100)
        matched_keywords.extend(cert_matched)
        missing_keywords.extend(cert_missing)
        
        # 5. Soft Skills Score (5%)
        soft_score, soft_matched = self._score_soft_skills(resume_text, job_description)
        scores.soft_skills = soft_score * (self.WEIGHTS["soft_skills"] / 100)
        matched_keywords.extend(soft_matched)
        
        # 6. Semantic Match Score (10%)
        if self.sentence_model:
            semantic_score = self._score_semantic(resume_sections, job_description)
        else:
            semantic_score = self._basic_similarity(resume_text, job_description)
        scores.semantic = semantic_score * (self.WEIGHTS["semantic"] / 100)
        
        # 7. Format Score (10%)
        scores.format = (format_score / 10) * self.WEIGHTS["format"]
        
        # Generate suggestions
        if missing_keywords:
            suggestions.append(f"Add missing skills: {', '.join(missing_keywords[:5])}")
        
        if scores.experience < 10:
            suggestions.append("Quantify your experience with years and achievements")
        
        if scores.education < 8:
            suggestions.append("Ensure education section clearly lists degrees")
        
        return scores, matched_keywords, missing_keywords, suggestions
    
    def _extract_keywords(self, text: str) -> Set[str]:
        """Extract keywords from text"""
        text_lower = text.lower()
        keywords = set()
        
        # Use spaCy if available
        if self.nlp:
            doc = self.nlp(text_lower)
            for token in doc:
                if token.pos_ in ["NOUN", "PROPN", "ADJ"] and len(token.text) > 2:
                    keywords.add(token.lemma_)
        else:
            # Basic extraction
            words = re.findall(r'\b[a-z]{3,}\b', text_lower)
            keywords = set(words)
        
        # Add known skills
        for skill in self.TECH_SKILLS:
            if skill in text_lower:
                keywords.add(skill)
        
        return keywords
    
    def _score_technical_skills(
        self,
        resume_keywords: Set[str],
        jd_keywords: Set[str]
    ) -> Tuple[float, List[str], List[str]]:
        """Score technical skills match"""
        
        # Find tech skills in JD
        jd_tech = jd_keywords.intersection(self.TECH_SKILLS)
        resume_tech = resume_keywords.intersection(self.TECH_SKILLS)
        
        # Also check for skills mentioned in JD
        for kw in jd_keywords:
            if any(ts in kw for ts in self.TECH_SKILLS):
                jd_tech.add(kw)
        
        if not jd_tech:
            return 100, list(resume_tech), []
        
        matched = resume_tech.intersection(jd_tech)
        missing = jd_tech - resume_tech
        
        score = (len(matched) / len(jd_tech)) * 100 if jd_tech else 100
        
        return min(score, 100), list(matched), list(missing)
    
    def _score_experience(
        self,
        resume_experience: str,
        job_description: str
    ) -> Tuple[float, List[str]]:
        """Score experience section with intelligent weighting"""
        suggestions = []
        
        if not resume_experience:
            return 0, ["Add a detailed work experience section"]
        
        # Extract required years from JD
        required_years = self._extract_years_required(job_description)
        candidate_years = self._extract_candidate_years(resume_experience)
        
        # Score based on years match
        if required_years > 0:
            if candidate_years >= required_years:
                year_score = 100
            else:
                year_score = (candidate_years / required_years) * 100
                suggestions.append(f"JD requires {required_years}+ years, you have ~{candidate_years}")
        else:
            year_score = 80  # Default if no years specified
        
        # Check for keywords overlap
        jd_keywords = self._extract_keywords(job_description)
        exp_keywords = self._extract_keywords(resume_experience)
        
        keyword_overlap = len(jd_keywords.intersection(exp_keywords)) / max(len(jd_keywords), 1)
        keyword_score = keyword_overlap * 100
        
        # Combined score
        final_score = (year_score * 0.6) + (keyword_score * 0.4)
        
        return min(final_score, 100), suggestions
    
    def _extract_years_required(self, text: str) -> int:
        """Extract required years of experience from JD"""
        patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?)(?:\s+of)?\s+(?:experience|exp)',
            r'(\d+)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:work|professional)',
            r'minimum\s+(?:of\s+)?(\d+)\s*(?:years?|yrs?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return int(match.group(1))
        
        return 0
    
    def _extract_candidate_years(self, experience_text: str) -> int:
        """Estimate candidate's years of experience"""
        # Look for date ranges
        year_pattern = r'(?:19|20)\d{2}'
        years = re.findall(year_pattern, experience_text)
        
        if len(years) >= 2:
            years = sorted([int(y) for y in years])
            return years[-1] - years[0]
        
        # Look for explicit mentions
        exp_pattern = r'(\d+)\+?\s*(?:years?|yrs?)'
        match = re.search(exp_pattern, experience_text.lower())
        if match:
            return int(match.group(1))
        
        return 2  # Default estimate
    
    def _score_education(self, resume_education: str, job_description: str) -> float:
        """Score education section"""
        if not resume_education:
            return 50  # Some credit if education not explicitly required
        
        jd_lower = job_description.lower()
        edu_lower = resume_education.lower()
        
        score = 60  # Base score
        
        # Check for degree mentions
        for kw in self.EDUCATION_KEYWORDS:
            if kw in jd_lower and kw in edu_lower:
                score += 10
        
        # Check for specific requirements
        if "master" in jd_lower:
            if "master" in edu_lower or "m.s" in edu_lower or "mba" in edu_lower:
                score += 15
            else:
                score -= 10
        
        if "bachelor" in jd_lower:
            if "bachelor" in edu_lower or "b.s" in edu_lower or "b.a" in edu_lower:
                score += 10
        
        return min(score, 100)
    
    def _score_certifications(
        self,
        resume_text: str,
        job_description: str
    ) -> Tuple[float, List[str], List[str]]:
        """Score certifications"""
        jd_lower = job_description.lower()
        resume_lower = resume_text.lower()
        
        matched = []
        missing = []
        
        for cert in self.CERT_KEYWORDS:
            if cert in jd_lower:
                if cert in resume_lower:
                    matched.append(cert)
                else:
                    missing.append(cert)
        
        if not matched and not missing:
            return 80, [], []  # No certs required
        
        total_required = len(matched) + len(missing)
        score = (len(matched) / total_required) * 100 if total_required > 0 else 80
        
        return score, matched, missing
    
    def _score_soft_skills(
        self,
        resume_text: str,
        job_description: str
    ) -> Tuple[float, List[str]]:
        """Score soft skills"""
        jd_lower = job_description.lower()
        resume_lower = resume_text.lower()
        
        matched = []
        jd_soft = []
        
        for skill in self.SOFT_SKILLS:
            if skill in jd_lower:
                jd_soft.append(skill)
                if skill in resume_lower:
                    matched.append(skill)
        
        if not jd_soft:
            return 80, []  # No soft skills explicitly required
        
        score = (len(matched) / len(jd_soft)) * 100
        return score, matched
    
    def _score_semantic(
        self,
        resume_sections: Dict[str, str],
        job_description: str
    ) -> float:
        """Section-wise semantic matching using sentence transformers"""
        if not self.sentence_model:
            return 70  # Default score if model not available
        
        try:
            # Split JD into sections
            jd_skills = self._extract_jd_section(job_description, "skills")
            jd_responsibilities = self._extract_jd_section(job_description, "responsibilities")
            jd_requirements = self._extract_jd_section(job_description, "requirements")
            
            scores = []
            
            # Skills match
            if resume_sections.get("skills") and jd_skills:
                score = self._compute_similarity(resume_sections["skills"], jd_skills)
                scores.append(score)
            
            # Experience match
            if resume_sections.get("experience") and jd_responsibilities:
                score = self._compute_similarity(resume_sections["experience"], jd_responsibilities)
                scores.append(score)
            
            # Overall match
            full_resume = " ".join(resume_sections.values())
            if full_resume:
                score = self._compute_similarity(full_resume, job_description)
                scores.append(score)
            
            return (sum(scores) / len(scores) * 100) if scores else 70
            
        except Exception as e:
            logger.error(f"Semantic scoring error: {e}")
            return 70
    
    def _compute_similarity(self, text1: str, text2: str) -> float:
        """Compute cosine similarity between two texts"""
        try:
            embeddings = self.sentence_model.encode([text1, text2])
            similarity = np.dot(embeddings[0], embeddings[1]) / (
                np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
            )
            return max(0, min(1, similarity))
        except Exception:
            return 0.7
    
    def _extract_jd_section(self, jd: str, section_type: str) -> str:
        """Extract section from job description"""
        keywords = {
            "skills": ["skills", "technologies", "requirements", "qualifications"],
            "responsibilities": ["responsibilities", "duties", "what you'll do"],
            "requirements": ["requirements", "qualifications", "must have"]
        }
        
        jd_lines = jd.split("\n")
        capturing = False
        content = []
        
        for line in jd_lines:
            line_lower = line.lower().strip()
            
            if any(kw in line_lower for kw in keywords.get(section_type, [])):
                capturing = True
                continue
            
            if capturing:
                if line.strip() and not any(kw in line_lower for kw in sum(keywords.values(), [])):
                    content.append(line)
                elif any(kw in line_lower for kw in sum(keywords.values(), [])):
                    break
        
        return " ".join(content)
    
    def _basic_similarity(self, text1: str, text2: str) -> float:
        """Basic keyword similarity when ML models unavailable"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return (intersection / union) * 100 if union > 0 else 50
