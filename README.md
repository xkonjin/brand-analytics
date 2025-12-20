# 🚀 Brand Analytics Tool

**A comprehensive, automated 360° brand audit platform for startups.**

![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Node](https://img.shields.io/badge/node-20+-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-teal.svg)
![Next.js](https://img.shields.io/badge/Next.js-14-black)

## 📖 Overview

The **Brand Analytics Tool** is designed to be an automated "virtual brand analyst." In a world where agency audits take weeks and cost thousands, this tool delivers a consulting-grade report in minutes.

It analyzes a brand's online presence across **8 critical dimensions**:

| Module | What It Analyzes |
|--------|-----------------|
| 🔍 **SEO Performance** | Core Web Vitals, meta tags, indexing status |
| 🤖 **AI Discoverability** | Wikipedia presence, Knowledge Graph, LLM visibility |
| 📱 **Social Media** | Followers, engagement rates, posting consistency |
| 🎭 **Brand Messaging** | Archetype, tone, value proposition clarity |
| 🎨 **Website UX** | CTAs, navigation, trust signals, conversion readiness |
| 📝 **Content Analysis** | Content mix, sentiment, themes |
| 👥 **Team Presence** | Team visibility, founder credibility |
| 📊 **Channel Fit** | Marketing channel recommendations |

---

## 🚀 Quick Start

### Prerequisites

- **Docker** & **Docker Compose** (Recommended)
- **API Keys** (at minimum, an OpenAI API key)

### Option 1: Docker (Fastest) ⭐

```bash
# 1. Clone the repository
git clone <repo-url>
cd brand-analytics

# 2. Copy environment template and add your API keys
cp .env.example .env
# Edit .env and add at minimum: OPENAI_API_KEY

# 3. Start all services
./start-dev.sh docker
# Or manually: docker-compose up -d

# 4. Open the app
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

### Option 2: Local Development

```bash
# 1. Start database services with Docker
./start-dev.sh services

# 2. In terminal 1 - Start backend
cd backend
cp env.example .env
# Edit .env and add your API keys
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 3. In terminal 2 - Start frontend
cd frontend
npm install
npm run dev
```

---

## ⚙️ Configuration

### Required API Keys

| Key | Purpose | Get It At |
|-----|---------|-----------|
| `OPENAI_API_KEY` | Brand archetype & tone analysis | [OpenAI Platform](https://platform.openai.com/api-keys) |

### Recommended API Keys (Enhanced Analysis)

| Key | Purpose | Get It At |
|-----|---------|-----------|
| `GOOGLE_API_KEY` | PageSpeed & Search analysis | [Google Cloud Console](https://console.cloud.google.com/apis/credentials) |
| `GOOGLE_SEARCH_ENGINE_ID` | SERP & indexing checks | [Programmable Search](https://programmablesearchengine.google.com/) |
| `TWITTER_BEARER_TOKEN` | Social media metrics | [Twitter Developer](https://developer.twitter.com/) |

### Optional API Keys (Enhanced Analysis)

| Key | Purpose | Get It At |
|-----|---------|-----------|
| `APIFY_API_TOKEN` | Instagram, YouTube, Reddit scraping | [Apify Console](https://console.apify.com/) |
| `MOZ_API_KEY` | Domain Authority, backlinks | [Moz API](https://moz.com/products/api) |
| `CLEARBIT_API_KEY` | Company logo fetching | [Clearbit](https://clearbit.com/) |

### Planned API Keys (Coming Soon)

| Key | Purpose | Status |
|-----|---------|--------|
| `FIRECRAWL_API_KEY` | JavaScript-capable scraping | Planned |
| `SERPER_API_KEY` | Google Search, News, Knowledge Graph | Planned |

> **Note:** All API-dependent features have fallback behavior. Without API keys, the tool will use mock data or heuristic analysis.

---

## 🏗 Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Next.js 14    │────▶│   FastAPI       │────▶│   PostgreSQL    │
│   Frontend      │     │   Backend       │     │   Database      │
│   :3000         │     │   :8000         │     │   :5432         │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                        ┌────────▼────────┐     ┌─────────────────┐
                        │  Celery Worker  │────▶│     Redis       │
                        │  (Background)   │     │   :6379         │
                        └────────┬────────┘     └─────────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
       ┌──────▼──────┐    ┌──────▼──────┐    ┌──────▼──────┐
       │   OpenAI    │    │   Google    │    │  Twitter    │
       │   GPT-4     │    │  PageSpeed  │    │   API v2    │
       └─────────────┘    └─────────────┘    └─────────────┘
```

### Directory Structure

```
brand-analytics/
├── backend/                 # Python FastAPI Application
│   ├── app/
│   │   ├── analyzers/       # 8 analysis modules
│   │   ├── api/             # REST endpoints
│   │   ├── models/          # Database & Pydantic models
│   │   ├── scrapers/        # Website scraping
│   │   ├── services/        # External API integrations
│   │   └── tasks/           # Celery background tasks
│   ├── env.example          # Environment template
│   └── Dockerfile
├── frontend/                # Next.js 14 Application
│   ├── src/
│   │   ├── app/             # Pages (home, analyze, report)
│   │   ├── components/      # UI components
│   │   └── lib/             # Utilities & API client
│   └── Dockerfile
├── docker-compose.yml       # Full stack orchestration
├── start-dev.sh             # Development helper script
└── .env.example             # Root env for Docker Compose
```

---

## 🛠 API Endpoints

Once running, visit **http://localhost:8000/docs** for interactive documentation.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/analyze` | Start a new brand analysis |
| `GET` | `/api/v1/analysis/{id}` | Get analysis status |
| `GET` | `/api/v1/analysis/{id}/progress` | Get detailed progress |
| `GET` | `/api/v1/analysis/{id}/report` | Get complete report JSON |
| `GET` | `/api/v1/analysis/{id}/pdf` | Download PDF report |
| `GET` | `/api/v1/health` | Health check |

### Example: Start an Analysis

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

---

## 🔧 Development Commands

```bash
# Start everything with Docker
./start-dev.sh docker

# Start only database services
./start-dev.sh services

# View logs
docker-compose logs -f backend

# Stop all services
docker-compose down

# Reset database (caution: deletes data)
docker-compose down -v

# Run backend tests
cd backend && pytest

# Run frontend type check
cd frontend && npm run build
```

---

## 🐛 Troubleshooting

### "Connection refused" errors

1. Make sure Docker is running
2. Check if services are healthy: `docker-compose ps`
3. Wait for health checks to pass (30-60 seconds)

### "API key not configured" warnings

This is normal if you haven't set all API keys. The tool will use fallback/mock data.

### Frontend can't connect to backend

1. Check backend is running: `curl http://localhost:8000/api/v1/health`
2. Ensure `NEXT_PUBLIC_API_URL=http://localhost:8000` is set

### PDF download not working

PDF generation requires WeasyPrint system dependencies. In Docker, these are pre-installed. For local development, you may need to install them separately.

---

## 📊 Scoring Methodology

The tool generates a **0-100 Brand Health Score** using weighted analysis:

| Module | Weight |
|--------|--------|
| Social Media | 20% |
| SEO Performance | 15% |
| Brand Messaging | 15% |
| Website UX | 15% |
| AI Discoverability | 10% |
| Content | 10% |
| Team Presence | 10% |
| Channel Fit | 5% |

### Grade Scale

| Score | Grade | Interpretation |
|-------|-------|----------------|
| 90-100 | A+ | Industry leader |
| 80-89 | A | Excellent foundation |
| 70-79 | B | Good, above average |
| 60-69 | C | Average, room to improve |
| 50-59 | D | Below average |
| 0-49 | F | Needs immediate attention |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 🔌 Current Integrations

| Service | Purpose | Status |
|---------|---------|--------|
| **OpenAI GPT-4o** | Brand archetype, tone analysis | ✅ Active |
| **Google PageSpeed** | Core Web Vitals, performance | ✅ Active |
| **Moz Links API** | Domain Authority, backlinks, spam score | ✅ Active |
| **Twitter API v2** | Social metrics, engagement | ✅ Active |
| **Apify** | Instagram, YouTube, Reddit scraping | ✅ Active |
| **Wikipedia REST API** | AI discoverability, notability | ✅ Active |

---

## 🗺️ Roadmap

See [ENHANCEMENT_PLAN.md](./ENHANCEMENT_PLAN.md) for the full technical roadmap.

### Coming Soon

- **Phase 1:** JavaScript-capable scraping (Firecrawl)
- **Phase 2:** Comprehensive Google Search via Serper
- **Phase 3:** Review aggregation (G2, Trustpilot)
- **Phase 4:** Professional scoring with confidence intervals

### Recently Completed

- ✅ Apify integration for social media scraping
- ✅ Moz Links API for SEO authority metrics
- ✅ Reddit brand mention monitoring

---

## 📄 License

This project is licensed under the MIT License.
