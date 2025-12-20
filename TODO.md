# Brand Analytics - Implementation TODO

**Last Updated:** December 20, 2025

This document tracks the prioritized implementation tasks for the Brand Analytics enhancement plan.

---

## Phase 0: Foundation & Safety

### Critical (Do First)

- [x] **0.1** Add scoring regression tests ✅ PR #16
  - File: `backend/tests/test_scoring.py`
  - Test `weighted_average`, `score_to_grade`, `normalize_score`
  - Test `clamp_score`, `score_to_rating` from BaseAnalyzer
  - 42 tests covering utilities, regression, and edge cases

- [x] **0.2** Add "golden report shape" test ✅ PR #16
  - File: `backend/tests/test_report_shape.py`
  - Assert report JSON contains all required fields
  - Assert all scores are 0-100
  - 30 tests covering structure, validation, serialization

- [ ] **0.3** Mock external APIs for test stability
  - Mock: PageSpeed, Moz, Twitter, Apify, OpenAI
  - Use fixed payloads for reproducible tests
  - Effort: 2 hours

---

## Phase 1: JavaScript-Capable Scraping

### Critical

- [ ] **1.1** Add Firecrawl configuration
  - Add `FIRECRAWL_API_KEY` to `backend/app/config.py`
  - Add to `backend/env.example`
  - Add to `docker-compose.yml`
  - Effort: 1 hour

- [ ] **1.2** Create FirecrawlService
  - File: `backend/app/services/firecrawl_service.py`
  - Methods: `scrape_url(url, formats=['html', 'markdown'])`
  - Include retry logic with exponential backoff
  - Effort: 4 hours

- [ ] **1.3** Update WebsiteScraper with fallback chain
  - File: `backend/app/scrapers/website.py`
  - Priority: Firecrawl → BeautifulSoup → partial data
  - Set confidence based on which method succeeded
  - Effort: 4 hours

### High

- [ ] **1.4** Add circuit breaker for external services
  - Use existing `backend/app/utils/circuit_breaker.py`
  - Apply to Firecrawl, Apify, Moz services
  - Effort: 4 hours

### Medium

- [ ] **1.5** Add Jina Reader as secondary fallback
  - File: `backend/app/services/jina_service.py`
  - Use for content extraction when Firecrawl fails
  - Effort: 3 hours

---

## Phase 2: Comprehensive Search via Serper

### High

- [ ] **2.1** Add Serper configuration
  - Add `SERPER_API_KEY` to `backend/app/config.py`
  - Add to env templates
  - Effort: 1 hour

- [ ] **2.2** Create SerperService
  - File: `backend/app/services/serper_service.py`
  - Methods:
    - `search_web(query, num=10)`
    - `search_news(query, num=10)`
  - Parse: organic results, knowledge graph, PAA
  - Effort: 4 hours

- [ ] **2.3** Integrate into AIDiscoverabilityAnalyzer
  - File: `backend/app/analyzers/ai_discoverability.py`
  - Add Knowledge Graph presence detection
  - Add SERP position tracking
  - Effort: 3 hours

### Medium

- [ ] **2.4** Add news monitoring
  - Query: `"{brand} funding"`, `"{brand} review"`, etc.
  - Add `news_mentions` to report
  - Effort: 3 hours

---

## Phase 3: Enhanced Brand Research

### High

- [ ] **3.1** Review discovery via Serper
  - Query: `"{brand} Trustpilot"`, `"{brand} G2"`, etc.
  - Capture canonical review URLs
  - Effort: 4 hours

- [ ] **3.2** Review extraction
  - Scrape discovered review URLs via Firecrawl
  - Extract: rating, review count, themes
  - Add to report with confidence score
  - Effort: 10 hours

### Medium

- [ ] **3.3** Competitor share of voice analysis
  - Query: `"{brand} competitors"`, `"{category} best"`
  - Track competitor mentions vs brand
  - File: `backend/app/analyzers/competitor.py` or extend `channel_fit.py`
  - Effort: 10 hours

### Low

- [ ] **3.4** Clearbit industry enrichment (optional)
  - File: `backend/app/services/clearbit_service.py`
  - Auto-detect industry for benchmarking
  - Effort: 4 hours

---

## Phase 4: Professional Scoring System

### High

- [ ] **4.1** Add score breakdown schema
  - File: `backend/app/models/report.py`
  - Add optional fields: `score_breakdown`, `evidence`, `confidence`, `confidence_interval`
  - Effort: 4 hours

- [ ] **4.2** Replace hardcoded thresholds
  - Files: All analyzers in `backend/app/analyzers/`
  - Replace tier-based scoring with continuous sigmoid/log functions
  - Add helpers to `backend/app/utils/scoring.py`:
    - `sigmoid_score(value, midpoint, steepness)`
    - `log_scaled_score(value, min_log, max_log)`
  - Effort: 6 hours

- [ ] **4.3** Add confidence scoring
  - File: `backend/app/utils/scoring.py`
  - Function: `compute_confidence(signals: dict) -> float`
  - Populate in each analyzer
  - Effort: 8 hours

### Medium

- [ ] **4.4** Add BAV framework overlay
  - Calculate: Differentiation, Relevance, Esteem, Knowledge
  - Add to report as optional `brand_equity_frameworks` section
  - Effort: 8 hours

- [ ] **4.5** Add BrandZ (MDS) overlay
  - Calculate: Meaningful, Different, Salient
  - Effort: 4 hours

- [ ] **4.6** Frontend updates for new scoring data
  - Display confidence intervals
  - Show score breakdown
  - Visualize framework overlays
  - Effort: 10 hours

---

## Completed Tasks

### December 2025

- [x] **Phase 0 Foundation Tests (PR #16)** - 72 tests total
  - `test_scoring.py`: 42 tests for scoring utilities
  - `test_report_shape.py`: 30 tests for report validation
- [x] **Documentation (PR #15)** - ENHANCEMENT_PLAN.md, TODO.md, README updates
- [x] **Apify Integration** - Instagram, YouTube, Reddit scraping
- [x] **Moz Integration** - Domain Authority, backlinks, spam score
- [x] **Reddit Analysis** - Brand mention monitoring in social analyzer
- [x] **Docker Fixes** - Frontend Dockerfile with `--legacy-peer-deps`
- [x] **PR #14 Merged** - Social media Apify/Moz integrations

---

## API Keys Status

| Service | Status | Config Key |
|---------|--------|------------|
| OpenAI | Configured | `OPENAI_API_KEY` |
| Apify | Configured | `APIFY_API_TOKEN` |
| Moz | Configured | `MOZ_API_KEY` |
| Twitter | Optional | `TWITTER_BEARER_TOKEN` |
| Google PageSpeed | Optional | `GOOGLE_API_KEY` |
| Firecrawl | Needed | `FIRECRAWL_API_KEY` |
| Serper | Needed | `SERPER_API_KEY` |

---

## Priority Legend

- **Critical** - Must do first, blocks other work
- **High** - Important for market readiness
- **Medium** - Nice to have, improves quality
- **Low** - Can defer, optional enhancement

---

## Notes

- All scoring changes should be covered by regression tests (Phase 0)
- Cache aggressively to control API costs
- Set confidence = low when using fallback data sources
- Frontend changes should follow existing component patterns

---

*See [ENHANCEMENT_PLAN.md](./ENHANCEMENT_PLAN.md) for full technical details.*
