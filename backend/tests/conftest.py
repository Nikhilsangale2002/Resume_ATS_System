# pytest configuration for ATS backend tests
import pytest
import asyncio
from typing import Generator, AsyncGenerator
from unittest.mock import MagicMock, patch
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock spaCy before importing app modules
mock_nlp = MagicMock()
mock_nlp.return_value = MagicMock()
mock_nlp.return_value.ents = []
mock_nlp.return_value.__iter__ = lambda self: iter([])

with patch.dict('sys.modules', {'spacy': MagicMock()}):
    pass


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_db_session():
    """Mock database session."""
    session = MagicMock()
    session.commit = MagicMock()
    session.rollback = MagicMock()
    session.close = MagicMock()
    return session


@pytest.fixture
def sample_job_description():
    """Sample job description for testing."""
    return """
    Senior Python Developer
    
    Requirements:
    - 5+ years of Python experience
    - FastAPI or Django framework
    - PostgreSQL or MySQL
    - Docker and Kubernetes
    - AWS or GCP cloud experience
    
    Nice to have:
    - Machine Learning experience
    - React or Vue.js
    """


@pytest.fixture
def sample_resume_text():
    """Sample resume text for testing."""
    return """
    John Doe
    Senior Software Engineer
    
    Experience:
    - 6 years of Python development
    - Built APIs with FastAPI and Flask
    - MySQL and PostgreSQL database design
    - Docker containerization
    - AWS deployment (EC2, S3, Lambda)
    
    Education:
    - B.S. Computer Science, MIT, 2018
    
    Skills:
    Python, FastAPI, Django, MySQL, PostgreSQL, Docker, AWS, Git
    """


@pytest.fixture
def auth_headers():
    """Mock authentication headers."""
    return {"Authorization": "Bearer test-token-12345"}
