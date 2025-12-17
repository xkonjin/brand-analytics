# Brand Analytics Tool

A comprehensive brand analysis tool that provides professional marketing audits across multiple dimensions: SEO, social media, brand messaging, website UX, AI discoverability, and more.

## Features

- **SEO Performance Analysis**: PageSpeed, meta tags, Core Web Vitals, indexing status
- **Social Media Presence**: Follower counts, engagement rates, platform coverage
- **Brand Messaging & Archetype**: Jungian archetype identification, tone analysis, readability
- **Website UX & Conversion**: CTAs, navigation, trust signals, mobile responsiveness
- **AI Discoverability**: Wikipedia presence, structured data, content depth
- **Content Analysis**: Recent posts, sentiment, content mix evaluation
- **Team Presence**: LinkedIn, founder visibility, credibility signals
- **Channel Fit Scoring**: Platform suitability recommendations

## Architecture

```
brand-analytics/
├── backend/          # FastAPI Python backend
│   ├── app/
│   │   ├── analyzers/    # 9 analysis modules
│   │   ├── api/          # REST endpoints
│   │   ├── models/       # Pydantic schemas
│   │   ├── scrapers/     # Web scraping utilities
│   │   ├── services/     # External API integrations
│   │   └── tasks/        # Celery async tasks
│   └── requirements.txt
├── frontend/         # Next.js React frontend
│   └── src/
│       ├── app/          # Pages (home, analyze, report)
│       ├── components/   # React components
│       └── lib/          # API client
└── docker-compose.yml
```

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 20+
- Docker & Docker Compose (for local development)
- API Keys (optional but recommended):
  - OpenAI API key (for GPT-4 analysis)
  - Google API key (for PageSpeed)

### 1. Clone and Setup

```bash
cd brand-analytics

# Copy environment file
cp backend/.env.example backend/.env
# Edit .env with your API keys
```

### 2. Start with Docker Compose

```bash
# Start all services (PostgreSQL, Redis, Backend, Celery)
docker-compose up -d

# View logs
docker-compose logs -f backend
```

### 3. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

### 4. Access the Application

- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- Celery Monitor: http://localhost:5555

## Development Setup (Without Docker)

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Start PostgreSQL and Redis (local or cloud)
# Update DATABASE_URL and REDIS_URL in .env

# Run database migrations
# alembic upgrade head

# Start the API server
uvicorn app.main:app --reload --port 8000

# In another terminal, start Celery worker
celery -A app.tasks.celery_app worker --loglevel=info
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/analyze` | Start new analysis |
| GET | `/api/v1/analysis/{id}` | Get analysis status |
| GET | `/api/v1/analysis/{id}/progress` | Real-time progress |
| GET | `/api/v1/analysis/{id}/report` | Get full report |
| GET | `/api/v1/analysis/{id}/pdf` | Download PDF |
| GET | `/api/v1/health` | Health check |

## Configuration

Key environment variables:

```env
# Required
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/brand_analytics
REDIS_URL=redis://localhost:6379/0

# Recommended for full functionality
OPENAI_API_KEY=sk-...          # GPT-4 for brand analysis
GOOGLE_API_KEY=...             # PageSpeed Insights

# Optional
APIFY_API_TOKEN=...            # Social media scraping
S3_BUCKET_NAME=...             # PDF storage
```

## Scoring System

Each module generates a score from 0-100, weighted to calculate the overall brand score:

| Module | Weight |
|--------|--------|
| SEO Performance | 15% |
| Social Media | 20% |
| Brand Messaging | 15% |
| Website UX | 15% |
| AI Discoverability | 10% |
| Content Analysis | 10% |
| Team Presence | 10% |
| Channel Fit | 5% |

## Deployment

### Backend (Railway/Render)

1. Connect your GitHub repository
2. Set environment variables
3. Deploy with `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Frontend (Vercel)

1. Connect your GitHub repository
2. Set `NEXT_PUBLIC_API_URL` to your backend URL
3. Deploy automatically

### Database (Supabase/Railway)

Use managed PostgreSQL for production reliability.

## License

MIT License - see LICENSE file for details.

