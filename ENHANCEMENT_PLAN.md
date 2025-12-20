# Brand Analytics Enhancement Plan

**Document Version:** 1.0  
**Date:** December 20, 2025  
**Status:** Planning Complete, Ready for Implementation

---

## Executive Summary

This document outlines the comprehensive enhancement plan to bring Brand Analytics from MVP to market-ready state. Based on analysis of the current codebase, industry frameworks, and competitive research, we've identified four key areas for improvement:

1. **JavaScript-capable scraping** (Critical - current BeautifulSoup fails on 85% of modern sites)
2. **Professional scoring system** (High - replace hardcoded thresholds with continuous, confidence-aware scoring)
3. **Comprehensive search/research** (High - add Serper for brand intelligence)
4. **Enhanced brand signals** (Medium - reviews, competitors, news monitoring)

**Estimated Total Effort:** 66-117 hours  
**Estimated Monthly API Cost:** $91-200

---

## Current State Analysis

### Architecture Overview

```
Frontend (Next.js 14) → Backend (FastAPI) → PostgreSQL
                              ↓
                        Celery Worker → Redis
                              ↓
                    External APIs (OpenAI, Google, Twitter, Moz, Apify)
```

### 8 Analysis Modules

| Module | Weight | Current Implementation |
|--------|--------|----------------------|
| SEO Performance | 15% | PageSpeed API + Moz Domain Authority |
| Social Media | 20% | Twitter API + Apify (Instagram, YouTube, Reddit) |
| Brand Messaging | 15% | OpenAI GPT-4 archetype analysis |
| Website UX | 15% | Heuristic analysis of CTAs, navigation, trust signals |
| AI Discoverability | 10% | Wikipedia + Google Search + Schema.org |
| Content | 10% | OpenAI content analysis |
| Team Presence | 10% | Team page detection, LinkedIn signals |
| Channel Fit | 5% | Channel recommendation engine |

### Current Strengths

- Solid 8-module architecture with clear separation
- Apify integration working (Instagram, YouTube, Reddit)
- Moz Links API for Domain Authority
- Twitter API v2 integration
- Wikipedia REST API for AI discoverability
- Well-structured frontend with benchmarks and frameworks
- Docker-ready deployment

### Critical Gaps Identified

| Area | Problem | Business Impact |
|------|---------|----------------|
| **Scraping** | BeautifulSoup cannot render JavaScript | 85% of modern React/Vue/Angular sites return minimal content |
| **Scoring** | Hardcoded thresholds (e.g., 50k followers = 100 pts) | Cliff effects cause unfair/unstable scoring |
| **Confidence** | No score reliability indicators | Users can't distinguish high vs low-confidence scores |
| **Search** | Limited to Google Custom Search | Missing brand intelligence, news, knowledge graph |
| **Reviews** | No review aggregation | Missing critical trust/esteem signals |
| **Competitors** | No competitive analysis | Can't assess differentiation or share of voice |

---

## Recommended Technology Stack

### Scraping Solutions (Evaluated)

| Solution | JS Support | Cost/100 pages | Recommendation |
|----------|------------|----------------|----------------|
| **Firecrawl** | Full | $16 | **Primary** - Best for AI/LLM pipelines |
| **Apify** | Full | $4.90 | **Backup** - Already integrated |
| **Jina Reader** | Full | Free tier | **Fallback** - Good for content extraction |
| **ScrapingFish** | Full | $0.20 | Budget option |
| BeautifulSoup | None | $0 | Current - deprecate for main scraping |

### Search/Research APIs (Evaluated)

| API | Purpose | Cost/Month | Recommendation |
|-----|---------|------------|----------------|
| **Serper.dev** | Google Search, News, KG | $50 (50k queries) | **Primary** - Best price/performance |
| SerpAPI | Multi-engine search | $50-250 | Alternative |
| **Apollo.io** | Company enrichment | $49 | Optional - industry detection |
| **GDELT** | News monitoring | Free | **Add** - Global news mentions |

### Scoring Frameworks (Research)

| Framework | Components | Application |
|-----------|------------|-------------|
| **Brand Asset Valuator (BAV)** | Differentiation, Relevance, Esteem, Knowledge | Overall brand health overlay |
| **BrandZ (MDS)** | Meaningful, Different, Salient | Growth potential indicators |
| **Interbrand** | Financial, Role of Brand, Brand Strength | Enterprise valuation |
| **Keller CBBE** | Identity, Meaning, Response, Resonance | Customer-based equity |

---

## Implementation Phases

### Phase 0: Foundation & Safety (6-10 hours)
> Prevent regressions before changing scoring logic

| Task | Description | Effort | Priority |
|------|-------------|--------|----------|
| 0.1 | Add scoring regression tests for `utils/scoring.py` | 4h | Critical |
| 0.2 | Add "golden report shape" test (validate JSON structure) | 2h | Critical |
| 0.3 | Mock external APIs for test stability | 2h | Critical |

**Deliverable:** CI pipeline catches any scoring regressions

---

### Phase 1: JavaScript-Capable Scraping (12-22 hours)
> The single biggest quality improvement

| Task | Description | Effort | Priority |
|------|-------------|--------|----------|
| 1.1 | Add `FIRECRAWL_API_KEY` to config.py and env templates | 1h | Critical |
| 1.2 | Create `FirecrawlService` wrapper with retry logic | 4h | Critical |
| 1.3 | Update `WebsiteScraper` with fallback chain | 4h | Critical |
| 1.4 | Add circuit breaker pattern for external services | 4h | High |
| 1.5 | Add Jina Reader as secondary fallback | 3h | Medium |

**Scraping Priority Chain:**
```
Firecrawl (JS-rendered) → BeautifulSoup (static) → Partial data with low confidence
```

**API Cost:** ~$16/analysis (100 pages)

---

### Phase 2: Comprehensive Search via Serper (7-14 hours)
> Backbone for brand research and intelligence

| Task | Description | Effort | Priority |
|------|-------------|--------|----------|
| 2.1 | Add `SERPER_API_KEY` to config | 1h | High |
| 2.2 | Create `SerperService` with `/search` and `/news` endpoints | 4h | High |
| 2.3 | Integrate into `AIDiscoverabilityAnalyzer` | 3h | High |
| 2.4 | Add news monitoring for brand mentions | 3h | Medium |

**New Capabilities:**
- Knowledge Graph presence detection
- "People Also Ask" questions (market gaps)
- News sentiment monitoring
- SERP position tracking

**API Cost:** ~$50/month (50k queries)

---

### Phase 3: Enhanced Brand Research (19-31 hours)
> Move from audit to strategic market view

| Task | Description | Effort | Priority |
|------|-------------|--------|----------|
| 3.1 | Review discovery via Serper queries | 4h | High |
| 3.2 | Review extraction (Trustpilot, G2, Capterra ratings) | 10h | High |
| 3.3 | Competitor "share of voice" analysis | 10h | Medium |
| 3.4 | Clearbit industry enrichment (optional) | 4h | Low |

**New Data Sources:**
- Trustpilot ratings + review count
- G2 ratings + review themes  
- Competitor SERP positioning
- Industry auto-detection

---

### Phase 4: Professional Scoring System (22-40 hours)
> Framework-driven, confidence-aware scoring

#### 4.1 Schema Updates (4-8h)
Add to each module's report:
```python
{
    "score": 74,
    "score_breakdown": {
        "performance": 85,
        "meta_tags": 70,
        "mobile": 60,
        "technical": 80
    },
    "evidence": {
        "pagespeed_score": {"value": 70, "source": "Google PSI"},
        "domain_authority": {"value": 45, "source": "Moz"}
    },
    "confidence": 0.85,
    "confidence_interval": [68, 80]
}
```

#### 4.2 Replace Hardcoded Thresholds (4-6h)
```python
# Current (problematic)
if total_followers >= 50000:
    follower_score = 100
elif total_followers >= 10000:
    follower_score = 80

# New (continuous sigmoid)
def sigmoid_score(value, midpoint=10000, steepness=0.5):
    import math
    x = math.log10(max(value, 1))
    return 100 / (1 + math.exp(-steepness * (x - math.log10(midpoint))))
```

#### 4.3 Add Confidence Scoring (6-12h)
```python
def compute_confidence(signals: dict) -> float:
    weights = {
        "api_data_available": 0.3,
        "js_rendered": 0.2,
        "recent_data": 0.2,
        "multiple_sources": 0.2,
        "no_errors": 0.1
    }
    return sum(weights[k] for k, v in signals.items() if v)
```

#### 4.4 Framework Overlay (8-14h)
Add professional brand equity frameworks:

**Brand Asset Valuator (BAV):**
- Differentiation = Archetype confidence + competitor differentiation
- Relevance = Value proposition clarity + content relevance
- Esteem = Review ratings + trust signals + engagement
- Knowledge = KG presence + search volume + direct traffic

**BrandZ (MDS):**
- Meaningful = Value prop + emotional hooks
- Different = Archetype strength + uniqueness
- Salient = Share of voice + social reach

---

## Cost Summary

| Phase | Effort (hours) | API Cost/Month | Priority |
|-------|----------------|----------------|----------|
| Phase 0 | 6-10 | $0 | Critical |
| Phase 1 | 12-22 | $16-50 | Critical |
| Phase 2 | 7-14 | $50 | High |
| Phase 3 | 19-31 | $25-100 | High |
| Phase 4 | 22-40 | $0 | Medium |
| **Total** | **66-117** | **$91-200** | |

---

## API Keys Required

| Service | Purpose | Monthly Cost | Required |
|---------|---------|--------------|----------|
| OpenAI | Brand archetype analysis | ~$20 | Already have |
| Apify | Social media scraping | ~$49 | Already have |
| Moz | Domain Authority | ~$99 | Already have |
| **Firecrawl** | JS-capable scraping | $16+ | New |
| **Serper** | Google Search/News | $50 | New |
| Apollo (optional) | Company enrichment | $49 | Optional |

---

## Recommended Timeline

### Sprint 1 (Week 1-2): Foundation
- Phase 0: Tests
- Phase 1: Firecrawl integration

### Sprint 2 (Week 3-4): Research Backbone
- Phase 2: Serper integration
- Phase 3.1-3.2: Review discovery

### Sprint 3 (Week 5-6): Scoring Upgrade
- Phase 4.1-4.3: Schema + continuous scoring + confidence

### Sprint 4 (Week 7-8): Polish
- Phase 3.3: Competitor analysis
- Phase 4.4: Framework overlay
- Frontend updates for new data

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Review site anti-bot / ToS | Start with presence detection only, add confidence |
| API cost creep | Aggressive caching (Redis), cap queries per analysis |
| Score drift | Regression tests, `score_breakdown` for transparency |
| Firecrawl failures | Fallback chain: Firecrawl → Jina → BeautifulSoup |

---

## Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| JS-rendered site success rate | ~15% | >90% |
| Score confidence visibility | None | All modules |
| Review data availability | 0% | >60% of brands |
| Average analysis time | ~4s | <10s |
| API cost per analysis | ~$2 | <$5 |

---

## Next Steps

1. **Approve budget** for Firecrawl ($16+/mo) and Serper ($50/mo)
2. **Create feature branch** for Phase 1 implementation
3. **Set up API accounts** at firecrawl.dev and serper.dev
4. **Begin Phase 0** with scoring regression tests

---

*Document prepared by AI analysis of codebase, industry research, and competitive landscape.*
