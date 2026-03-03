# ATS Resume Scoring System

A production-grade Applicant Tracking System (ATS) resume scorer built with FastAPI, Next.js, MySQL, and local AI models. **No external API keys required!**

![ATS System](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![Next.js](https://img.shields.io/badge/next.js-14-black)
![MySQL](https://img.shields.io/badge/mysql-8.0-blue)
![Docker](https://img.shields.io/badge/docker-ready-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                     Next.js 14 Frontend                              │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐             │    │
│  │  │  Login   │  │ Analyzer │  │Dashboard │  │ History  │             │    │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘             │    │
│  │                                                                      │    │
│  │  Components: ScoreCard │ KeywordAnalysis │ SuggestionsPanel         │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│                                    ▼ HTTP/REST                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              API LAYER (FastAPI)                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         API Routes v1                                │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐             │    │
│  │  │  /auth   │  │ /resume  │  │  /score  │  │  /jobs   │             │    │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘             │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         Services Layer                               │    │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐         │    │
│  │  │ Scoring Engine │  │ Parser Service │  │ Auth Service   │         │    │
│  │  │  - 7 Categories│  │  - PDF/DOCX    │  │  - JWT Tokens  │         │    │
│  │  │  - AI Matching │  │  - Text Extract│  │  - OAuth2      │         │    │
│  │  └────────────────┘  └────────────────┘  └────────────────┘         │    │
│  │  ┌────────────────┐  ┌────────────────┐                              │    │
│  │  │Skill Normalizer│  │ Resume Builder │                              │    │
│  │  │  - 500+ Skills │  │  - Smart Format│                              │    │
│  │  └────────────────┘  └────────────────┘                              │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
          ┌──────────────────────────┼──────────────────────────┐
          │                          │                          │
          ▼                          ▼                          ▼
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   AI/ML LAYER   │      │  DATABASE LAYER │      │   CACHE LAYER   │
│                 │      │                 │      │                 │
│  ┌───────────┐  │      │  ┌───────────┐  │      │  ┌───────────┐  │
│  │   spaCy   │  │      │  │   MySQL   │  │      │  │   Redis   │  │
│  │ en_core_  │  │      │  │   8.0     │  │      │  │           │  │
│  │ web_lg    │  │      │  ├───────────┤  │      │  │ - Sessions│  │
│  └───────────┘  │      │  │ • users   │  │      │  │ - Cache   │  │
│  ┌───────────┐  │      │  │ • resumes │  │      │  │ - Queue   │  │
│  │ Sentence  │  │      │  │ • scores  │  │      │  └───────────┘  │
│  │Transformers│ │      │  │ • jobs    │  │      │                 │
│  │ MiniLM-L6 │  │      │  └───────────┘  │      │                 │
│  └───────────┘  │      │                 │      │                 │
└─────────────────┘      └─────────────────┘      └─────────────────┘
                                     │
                                     ▼
                         ┌─────────────────┐
                         │  WORKER LAYER   │
                         │                 │
                         │  ┌───────────┐  │
                         │  │  Celery   │  │
                         │  │  Workers  │  │
                         │  │           │  │
                         │  │ Async PDF │  │
                         │  │ Processing│  │
                         │  └───────────┘  │
                         └─────────────────┘
```

## 🛠️ Tech Stack

```
┌────────────────────────────────────────────────────────────────────────────┐
│                              TECH STACK                                     │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   FRONTEND                         BACKEND                                  │
│   ════════                         ═══════                                  │
│   ┌──────────────────┐            ┌──────────────────┐                     │
│   │  Next.js 14      │            │  FastAPI         │                     │
│   │  ├─ React 18     │            │  ├─ Python 3.11  │                     │
│   │  ├─ TypeScript   │            │  ├─ Pydantic     │                     │
│   │  ├─ TailwindCSS  │            │  ├─ SQLAlchemy   │                     │
│   │  ├─ Axios        │            │  ├─ JWT Auth     │                     │
│   │  └─ Recharts     │            │  └─ OAuth2       │                     │
│   └──────────────────┘            └──────────────────┘                     │
│                                                                             │
│   AI/NLP                           DATABASE                                 │
│   ══════                           ════════                                 │
│   ┌──────────────────┐            ┌──────────────────┐                     │
│   │  spaCy           │            │  MySQL 8.0       │                     │
│   │  ├─ en_core_web_lg│           │  ├─ Users        │                     │
│   │  ├─ NER          │            │  ├─ Resumes      │                     │
│   │  └─ POS Tagging  │            │  ├─ ATSScores    │                     │
│   │                  │            │  ├─ Jobs         │                     │
│   │  Sentence        │            │  └─ Skills       │                     │
│   │  Transformers    │            └──────────────────┘                     │
│   │  └─ MiniLM-L6-v2 │                                                     │
│   └──────────────────┘            INFRASTRUCTURE                           │
│                                   ══════════════                           │
│   DOCUMENT PARSING                ┌──────────────────┐                     │
│   ════════════════                │  Docker          │                     │
│   ┌──────────────────┐            │  ├─ Compose      │                     │
│   │  pdfminer.six    │            │  ├─ 7 Services   │                     │
│   │  pypdf           │            │  └─ Networking   │                     │
│   │  pdfplumber      │            │                  │                     │
│   │  python-docx     │            │  Redis           │                     │
│   └──────────────────┘            │  └─ Celery Queue │                     │
│                                   └──────────────────┘                     │
└────────────────────────────────────────────────────────────────────────────┘
```

## 🔄 Data Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Upload  │────▶│  Parse   │────▶│  Score   │────▶│  Display │
│  Resume  │     │  Content │     │  Analysis│     │  Results │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
     │                │                │                │
     ▼                ▼                ▼                ▼
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ PDF/DOCX │     │  spaCy   │     │ 7-Factor │     │  Radar   │
│ File     │     │  NLP     │     │ Scoring  │     │  Chart   │
│          │     │  Extract │     │  Engine  │     │  Grade   │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
```

## 🚀 Features

- **100% Local AI**: Uses spaCy + Sentence Transformers (no API keys)
- **Intelligent Scoring**: 7-category weighted scoring system
- **Skill Normalization**: Maps skill variations to standard names
- **Section-wise Analysis**: Skills, Experience, Education scoring
- **Format Checker**: ATS compatibility validation
- **Experience Weighting**: Smart years-of-experience matching
- **Background Processing**: Celery workers for scalability
- **Beautiful Dashboard**: Radar charts, score breakdowns

## 📊 Scoring Categories

| Category | Weight | Description |
|----------|--------|-------------|
| Technical Skills | 35% | Keyword matching + NLP extraction |
| Experience | 20% | Years + role matching |
| Education | 15% | Degree requirements |
| Certifications | 10% | Professional certifications |
| Semantic Match | 10% | Section-wise embeddings |
| Format Score | 10% | ATS compatibility |
| Soft Skills | 5% | Communication, leadership |

## 🛠️ Technology Details

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Next.js 14 | React framework with App Router |
| | TailwindCSS | Utility-first CSS |
| | Recharts | Score visualization charts |
| | Axios | HTTP client with interceptors |
| | TypeScript | Type safety |
| **Backend** | FastAPI | Python async web framework |
| | Python 3.11 | Runtime environment |
| | SQLAlchemy | ORM for database |
| | Pydantic | Data validation |
| | JWT/OAuth2 | Authentication (30-day sessions) |
| **Database** | MySQL 8.0 | Primary data store |
| | Redis | Caching & task queue |
| **AI/NLP** | spaCy (en_core_web_lg) | NER, POS tagging, skill extraction |
| | Sentence Transformers | Semantic similarity matching |
| | scikit-learn | ML utilities |
| **Document Parsing** | pdfminer.six | PDF text extraction |
| | pypdf | PDF fallback parser |
| | pdfplumber | PDF table extraction |
| | python-docx | DOCX parsing |
| **Infrastructure** | Docker | Containerization |
| | Docker Compose | Multi-container orchestration |
| | Celery | Background task processing |

## 🐳 Docker Services

```
┌─────────────────────────────────────────────────────────────────┐
│                    docker-compose.yml                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│   │  frontend   │  │   backend   │  │    mysql    │             │
│   │  :3000      │  │   :8000     │  │   :3306     │             │
│   │  Next.js    │  │   FastAPI   │  │   MySQL 8   │             │
│   └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                  │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│   │    redis    │  │   celery    │  │   adminer   │             │
│   │   :6379     │  │   worker    │  │   :8080     │             │
│   │   Cache     │  │   Tasks     │  │   DB Admin  │             │
│   └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                  │
│   ┌─────────────┐                                                │
│   │ phpmyadmin  │                                                │
│   │   :8081     │                                                │
│   │   DB GUI    │                                                │
│   └─────────────┘                                                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
ats-system/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── api/v1/routes/     # API endpoints
│   │   ├── core/              # Logging config
│   │   ├── database/          # MySQL connection
│   │   ├── models/            # SQLAlchemy models
│   │   ├── services/          # Business logic
│   │   │   ├── scoring_engine.py
│   │   │   ├── parser_service.py
│   │   │   └── skill_normalizer.py
│   │   └── workers/           # Celery tasks
│   └── requirements.txt
├── frontend/                   # Next.js Frontend
│   ├── src/
│   │   ├── app/               # Pages
│   │   ├── components/        # React components
│   │   ├── lib/               # API client
│   │   └── types/             # TypeScript types
│   └── package.json
├── docker/                     # Docker configs
├── uploads/                    # Resume storage
└── docker-compose.yml
```

## 🚦 Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 20+ (for local frontend dev)
- Python 3.11+ (for local backend dev)

### Option 1: Docker Compose (Recommended)

```bash
# Clone and navigate
cd ats-system

# Copy environment file
cp backend/.env.example backend/.env

# Start all services
docker-compose up -d

# Access:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000/docs
# - Adminer (MySQL): http://localhost:8080
```

### Option 2: Local Development

**Backend:**
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_lg

# Copy env file
cp .env.example .env

# Start MySQL and Redis (via Docker)
docker-compose up -d mysql redis

# Run backend
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

**Celery Worker:**
```bash
cd backend
celery -A app.workers.celery_config worker --loglevel=info
```

## 🔧 Configuration

Edit `backend/.env`:

```env
# Database
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=ats_system

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# JWT
SECRET_KEY=your-secret-key

# NLP Models
SPACY_MODEL=en_core_web_lg
SENTENCE_TRANSFORMER_MODEL=all-MiniLM-L6-v2
```

## 📡 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register user
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Get current user

### Resume
- `POST /api/v1/resume/upload` - Upload resume
- `GET /api/v1/resume/` - List resumes
- `GET /api/v1/resume/{id}` - Get resume details
- `DELETE /api/v1/resume/{id}` - Delete resume
- `POST /api/v1/resume/analyze-direct` - Direct resume analysis
- `GET /api/v1/resume/history` - Analysis history
- `GET /api/v1/resume/dashboard-stats` - Dashboard statistics

### Job Descriptions
- `POST /api/v1/jobs/` - Create job description
- `GET /api/v1/jobs/` - List jobs
- `PUT /api/v1/jobs/{id}` - Update job
- `DELETE /api/v1/jobs/{id}` - Delete job

### Scoring
- `POST /api/v1/score/calculate` - Calculate ATS score
- `GET /api/v1/score/history` - Get score history
- `GET /api/v1/score/{id}` - Get score details

### Monitoring
- `GET /api/v1/monitoring/health` - Basic health check
- `GET /api/v1/monitoring/health/live` - Kubernetes liveness probe
- `GET /api/v1/monitoring/health/ready` - Kubernetes readiness probe
- `GET /api/v1/monitoring/health/detailed` - Detailed health with component status
- `GET /api/v1/monitoring/metrics` - Application metrics
- `GET /api/v1/monitoring/info` - System information
- `GET /api/v1/monitoring/stats/summary` - Admin statistics (auth required)

## 🔐 Rate Limiting

Rate limits are applied per IP address and endpoint:

| Endpoint | Limit | Window |
|----------|-------|--------|
| Login | 5 requests | 5 minutes |
| Auth endpoints | 5 requests | 1 minute |
| File upload | 10 requests | 1 minute |
| Analysis | 20 requests | 1 minute |
| History/Dashboard | 60 requests | 1 minute |
| Default | 100 requests | 1 minute |

Rate limit headers in response:
- `X-RateLimit-Limit` - Maximum requests allowed
- `X-RateLimit-Remaining` - Requests remaining
- `X-RateLimit-Reset` - Unix timestamp when limit resets

## 🛡️ Error Handling

All errors follow a consistent format:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [...],
    "error_id": "abc123",
    "timestamp": "2026-03-03T08:00:00Z"
  }
}
```

Error codes:
- `BAD_REQUEST` (400)
- `UNAUTHORIZED` (401)
- `FORBIDDEN` (403)
- `NOT_FOUND` (404)
- `VALIDATION_ERROR` (422)
- `RATE_LIMITED` (429)
- `INTERNAL_ERROR` (500)

## 📈 Monitoring

### Dashboard Access
- Adminer (MySQL): http://localhost:8080
- phpMyAdmin: http://localhost:8081

### Health Endpoints
```bash
# Basic health
curl http://localhost:8000/api/v1/monitoring/health

# Detailed health with component status
curl http://localhost:8000/api/v1/monitoring/health/detailed

# Application metrics
curl http://localhost:8000/api/v1/monitoring/metrics
```

## 🚀 CI/CD Pipeline

GitHub Actions workflow (`.github/workflows/ci-cd.yml`):

```
┌─────────────────────────────────────────────────────────────────┐
│                     CI/CD Pipeline                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────┐     ┌──────────┐     ┌──────────┐                │
│   │  Lint &  │────▶│  Tests   │────▶│ Security │                │
│   │  Quality │     │          │     │   Scan   │                │
│   └──────────┘     └──────────┘     └──────────┘                │
│        │                │                │                       │
│        └────────────────┼────────────────┘                       │
│                         ▼                                        │
│                   ┌──────────┐                                   │
│                   │  Build   │                                   │
│                   │  Docker  │                                   │
│                   └──────────┘                                   │
│                         │                                        │
│           ┌─────────────┼─────────────┐                          │
│           ▼             ▼             ▼                          │
│     ┌──────────┐  ┌──────────┐  ┌──────────┐                    │
│     │ Staging  │  │Production │  │  Health  │                    │
│     │ Deploy   │  │  Deploy  │  │  Check   │                    │
│     └──────────┘  └──────────┘  └──────────┘                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

Pipeline stages:
1. **Lint & Code Quality** - flake8, black, ESLint, TypeScript check
2. **Backend Tests** - pytest with coverage
3. **Frontend Tests** - Jest/Vitest with coverage
4. **Security Scan** - Trivy vulnerability scanner
5. **Build Docker** - Multi-arch images pushed to GHCR
6. **Deploy** - Zero-downtime deployment to staging/production

## 🌐 Nginx Configuration

Production-ready Nginx config (`nginx/nginx.conf`) includes:

- **Rate Limiting** - Per-IP request throttling
- **Load Balancing** - Least connections algorithm
- **Gzip Compression** - Text/JSON/CSS/JS compression
- **Security Headers** - XSS, Content-Type, Frame Options
- **SSL/TLS** - Modern cipher configuration (optional)
- **Caching** - Static file caching with immutable headers
- **Health Checks** - `/health` endpoint for monitoring

Enable Nginx by uncommenting in `docker-compose.yml`:
```yaml
nginx:
  image: nginx:1.25-alpine
  ports:
    - "80:80"
    - "443:443"
  volumes:
    - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
```

## 🔒 Security Notes

- Change `SECRET_KEY` in production
- Use HTTPS in production
- Set proper CORS origins
- Rate limiting is enabled by default
- JWT tokens expire after 30 days
- Refresh tokens expire after 60 days

## 📁 New Files Structure

```
ats-system/
├── .github/
│   └── workflows/
│       └── ci-cd.yml           # GitHub Actions CI/CD
├── nginx/
│   └── nginx.conf              # Nginx configuration
├── backend/
│   └── app/
│       └── core/
│           ├── rate_limiter.py     # Rate limiting middleware
│           ├── error_handlers.py   # Error handling middleware
│           └── logging_config.py   # Logging setup
│       └── api/v1/routes/
│           └── monitoring.py       # Health & metrics endpoints
└── docker/
    └── Dockerfile.nginx        # Nginx Docker image
```

## 📄 License

MIT License

---

Built with ❤️ using FastAPI + Next.js + Local AI
