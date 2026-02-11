# Architectural & Strategy Decisions

## 2026-02-11: Influencer Data API Selection

### Problem
The brand audit tool uses Apify scraping to find influencers associated with a specific brand, but it can't answer "find the best 10 fitness influencers in Poland with 5%+ engagement under budget Z." Roadmap step 2 (Influencer Scoring & Matching Tool) requires a third-party discovery API with filterable search across demographics, engagement, location, and audience data.

**Approach chosen:** Hybrid — third-party API for discovery/filtering, our own scoring pipeline for quality/fraud analysis, our own orchestration for campaign execution.

### Viable Options

| Provider | Database | CEE Coverage | Entry Price | API Quality | Notes |
|---|---|---|---|---|---|
| **Modash** | 350M+ (IG/TT/YT) | **Confirmed** (PL/RO/CZ) | $16,200/yr (Discovery API) | Excellent — public docs, SDKs, AI Search | Largest DB, best docs, credit rollover. Annual commitment. |
| **HypeAuditor** | 219M+ (6 platforms) | **Confirmed** (PL/RO/CZ) | ~$500-1,000+/mo (custom) | Good — sandbox, 40+ filters | Richest fraud detection (AQS). Opaque pricing, sales-gated. |
| **Phyllo** | 250M+ (IG/TT/YT) | **Unverified** (global, skews US/UK/India) | $199/mo (Starter) | Good — Postman collections, SDKs | Starter plan too limited (200 profiles/mo). Reviews flag instability. |
| **Influencers.Club** | 340M+ (12 platforms) | **Unverified** (global) | $249/mo | Decent — public docs | Broadest platform coverage. Email enrichment. Month-to-month. |
| **InsightIQ** | 400M+ (6 platforms) | **Unverified** (global) | Custom (usage-based) | Good — sandbox available | Purchase intent filtering is unique. Opaque pricing. |
| **Wobb** | 400M+ (IG/YT/TT) | **Unverified** (geo targeting confirmed) | Custom (token-based) | Good — public docs | Developer-first. Token pricing could be cost-effective. |
| **Click Analytic** | 250-400M+ (IG/TT/YT) | **Unverified** (global) | ~$79-199/mo (platform) | Limited public docs | Lowest entry price. API pricing requires demo. |

### Key Data Points

**Modash Discovery API details:**
- Credits: 3,000/mo at $0.45/credit base. Search = 0.01/result, profile report = 1 credit, email lookup = 0.02/result. Unused credits roll over.
- Filters: 20+ params — follower range, country, engagement rate, gender, keywords, interests, bio, topics, hashtags, age, language, location, lookalikes.
- Data: 37+ data points per profile — audience demographics (age/gender/geo/language/interests/ethnicity), credibility scoring, audience overlap, brand collab history, content breakdown.
- CEE: Poland has dedicated discovery pages across niches. Romania: 12K+ IG, 17K+ TT indexed. Czech Republic: 2K+ TT indexed. City-level filtering available.
- Also has Raw API ($10,000/yr, 40K req/mo at $0.02/credit) for live unfiltered data.

**HypeAuditor specifics:**
- AQS (Audience Quality Score): composite of 15 metrics, 1-100 scale.
- Detects: fake followers, engagement pods, giveaway inflation, suspicious growth patterns.
- Audience data includes income brackets, marital status, education.
- EMV, estimated post/story prices, CPE, CPM.
- Credits: 1/report, 1/search page (20 results/page, max 10K results).

### Eliminated Options

| Provider | Reason |
|---|---|
| **InfluenceFlow** | **Fake.** `api.influenceflow.io` doesn't exist (NXDOMAIN). "API docs" are contradictory AI-generated SEO content. No external reviews anywhere. Actually a free SaaS web UI with no API. |
| **inBeat** | No API. SaaS-only micro-influencer tool ($200-1,000/mo). |
| **Heepsy** | No API. SaaS-only search tool ($89-369/mo). |
| **GRIN** | API exists but is CRM/campaign export only — no discovery/search endpoints. |
| **CreatorIQ** | Enterprise pricing (~$28K-36K/yr). Overkill for early-stage. |
| **NeoReach** | Enterprise-only. Fully opaque pricing and access. |
| **Upfluence** | $24K/yr minimum. Small database (12M vs 350M+). Shopify-focused. |

### Recommended Path

1. **Start now (low cost):** Influencers.Club at $249/mo — broadest platform coverage, month-to-month, email enrichment, free tier for testing.
2. **Primary backbone (when investing):** Modash Discovery API at ~$16,200/yr — largest DB, confirmed CEE coverage, best developer experience, AI Search.
3. **Worth demo calls:** InsightIQ (usage-based pricing, sandbox), Wobb (token-based, 400M+), Click Analytic (cheapest entry).

### Next Steps
- [ ] Contact Modash sales for Discovery API quote and CEE coverage demo
- [ ] Test Influencers.Club free tier for PL/RO/CZ coverage
- [ ] Request InsightIQ and Wobb demos to compare pricing
- [ ] Evaluate whether Phyllo Starter ($199/mo) has enough CEE data via free trial
