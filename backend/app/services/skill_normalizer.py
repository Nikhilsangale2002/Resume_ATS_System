"""
Skill Normalization Service
Normalizes skill variations to standard names
"""
import re
from typing import Dict, List, Set
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


# Default skill aliases mapping
DEFAULT_SKILL_ALIASES: Dict[str, str] = {
    # JavaScript variants
    "js": "JavaScript",
    "javascript": "JavaScript",
    "java script": "JavaScript",
    "ecmascript": "JavaScript",
    "es6": "JavaScript ES6+",
    "es2015": "JavaScript ES6+",
    
    # TypeScript
    "ts": "TypeScript",
    "typescript": "TypeScript",
    "type script": "TypeScript",
    
    # Node.js variants
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "node js": "Node.js",
    "expressjs": "Express.js",
    "express.js": "Express.js",
    "express": "Express.js",
    
    # React variants
    "react": "React.js",
    "reactjs": "React.js",
    "react.js": "React.js",
    "react js": "React.js",
    "react native": "React Native",
    "reactnative": "React Native",
    
    # Vue variants
    "vue": "Vue.js",
    "vuejs": "Vue.js",
    "vue.js": "Vue.js",
    "vue js": "Vue.js",
    "vuex": "Vuex",
    "nuxt": "Nuxt.js",
    "nuxtjs": "Nuxt.js",
    
    # Angular variants
    "angular": "Angular",
    "angularjs": "AngularJS",
    "angular.js": "AngularJS",
    "ng": "Angular",
    
    # Python variants
    "py": "Python",
    "python": "Python",
    "python3": "Python",
    "python 3": "Python",
    
    # Django
    "django": "Django",
    "drf": "Django REST Framework",
    "django rest framework": "Django REST Framework",
    
    # Flask
    "flask": "Flask",
    "fastapi": "FastAPI",
    "fast api": "FastAPI",
    
    # Databases
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "psql": "PostgreSQL",
    "mysql": "MySQL",
    "mariadb": "MariaDB",
    "mongo": "MongoDB",
    "mongodb": "MongoDB",
    "redis": "Redis",
    "elasticsearch": "Elasticsearch",
    "elastic search": "Elasticsearch",
    "es": "Elasticsearch",
    
    # Cloud
    "aws": "AWS",
    "amazon web services": "AWS",
    "gcp": "Google Cloud Platform",
    "google cloud": "Google Cloud Platform",
    "azure": "Microsoft Azure",
    "ms azure": "Microsoft Azure",
    
    # DevOps
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "k8": "Kubernetes",
    "docker": "Docker",
    "docker-compose": "Docker Compose",
    "dockercompose": "Docker Compose",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "jenkins": "Jenkins",
    "github actions": "GitHub Actions",
    "gitlab ci": "GitLab CI",
    
    # Version Control
    "git": "Git",
    "github": "GitHub",
    "gitlab": "GitLab",
    "bitbucket": "Bitbucket",
    
    # Other
    "html5": "HTML5",
    "html": "HTML",
    "css3": "CSS3",
    "css": "CSS",
    "sass": "SASS/SCSS",
    "scss": "SASS/SCSS",
    "tailwind": "Tailwind CSS",
    "tailwindcss": "Tailwind CSS",
    "bootstrap": "Bootstrap",
    "graphql": "GraphQL",
    "rest": "REST API",
    "restful": "REST API",
    "rest api": "REST API",
    "api": "REST API",
    "sql": "SQL",
    "nosql": "NoSQL",
    "agile": "Agile",
    "scrum": "Scrum",
    "jira": "Jira",
    "linux": "Linux",
    "unix": "Unix",
    "bash": "Bash",
    "shell": "Shell Scripting",
    "ml": "Machine Learning",
    "machine learning": "Machine Learning",
    "ai": "Artificial Intelligence",
    "artificial intelligence": "Artificial Intelligence",
    "nlp": "Natural Language Processing",
    "natural language processing": "Natural Language Processing",
}


class SkillNormalizer:
    """Normalize skill names to standard forms"""
    
    def __init__(self, db: Session = None):
        self.aliases = DEFAULT_SKILL_ALIASES.copy()
        
        # Load additional aliases from database if available
        if db:
            self._load_from_db(db)
    
    def _load_from_db(self, db: Session):
        """Load skill aliases from database"""
        try:
            from app.models.models import SkillAlias
            aliases = db.query(SkillAlias).all()
            for alias in aliases:
                self.aliases[alias.alias_name.lower()] = alias.standard_name
        except Exception as e:
            logger.warning(f"Could not load skill aliases from DB: {e}")
    
    def normalize(self, skill: str) -> str:
        """Normalize a skill name to its standard form"""
        skill_lower = skill.lower().strip()
        return self.aliases.get(skill_lower, skill.strip())
    
    def normalize_list(self, skills: List[str]) -> List[str]:
        """Normalize a list of skills and remove duplicates"""
        normalized = set()
        for skill in skills:
            normalized.add(self.normalize(skill))
        return list(normalized)
    
    def extract_and_normalize(self, text: str) -> Set[str]:
        """Extract skills from text and normalize them"""
        found_skills = set()
        text_lower = text.lower()
        
        # Check for each known skill/alias in text
        for alias, standard in self.aliases.items():
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(alias) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.add(standard)
        
        return found_skills


def get_skill_categories() -> Dict[str, List[str]]:
    """Get skills organized by category"""
    return {
        "frontend": ["JavaScript", "TypeScript", "React.js", "Vue.js", "Angular", "HTML5", "CSS3", "SASS/SCSS", "Tailwind CSS", "Bootstrap"],
        "backend": ["Python", "Node.js", "Django", "Flask", "FastAPI", "Express.js", "Java", "Go", "PHP", "Ruby"],
        "database": ["MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch", "SQL", "NoSQL"],
        "devops": ["Docker", "Kubernetes", "CI/CD", "Jenkins", "GitHub Actions", "Linux", "AWS", "Google Cloud Platform", "Microsoft Azure"],
        "mobile": ["React Native", "Flutter", "Swift", "Kotlin", "iOS", "Android"],
        "other": ["Git", "Agile", "Scrum", "REST API", "GraphQL", "Machine Learning", "Artificial Intelligence"]
    }
