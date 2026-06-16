# Vendor Selection API & Scoring Engine Guide

This document explains the Vendor Selection backend: API endpoints, scoring/prediction engine, XGBoost integration, database mapping, and how it aligns with the Functional Requirements Document (FRD).

---

## Table of Contents

1. [Overview](#overview)
2. [Project Structure](#project-structure)
3. [Setup & Running](#setup--running)
4. [API Base URL](#api-base-url)
5. [All API Endpoints](#all-api-endpoints)
6. [Chat / LLM Assistant](#chat--llm-assistant)
7. [Scoring & Prediction Engine](#scoring--prediction-engine)
8. [XGBoost ML Module](#xgboost-ml-module)
9. [Ranking Flow](#ranking-flow)
10. [Database Tables Used](#database-tables-used)
11. [FRD Mapping](#frd-mapping)
12. [Example Requests](#example-requests)
13. [Future Enhancements](#future-enhancements)

---

## Overview

The Vendor Selection system is a **FastAPI** backend that helps manufacturing procurement teams:

- Discover vendors for a product
- Score and rank vendors using multiple dimensions
- Predict vendor suitability with **XGBoost** (per FRD Section 13)
- Retrieve quality, risk, historical performance, and demand forecast data
- Support AI-driven procurement recommendations
- **Chat with an LLM assistant** that can answer questions and return scores, rankings, and predictions

**Tech stack**

| Layer | Technology |
|---|---|
| API | FastAPI |
| Database | PostgreSQL 16 (`vendor` schema) |
| ORM / Queries | SQLAlchemy (raw SQL) |
| ML Ranking | XGBoost |
| Fallback Scoring | Weighted feature score |
| LLM Chat | LangChain + LangGraph (Azure OpenAI) |

---

## Project Structure

```
Backend/
├── app/
│   ├── api/
│   │   ├── router.py              # Main API router
│   │   ├── pagination.py
│   │   └── routes/
│   │       ├── ranking_routes.py  # POST /rank
│   │       ├── scoring_routes.py  # Scoring & prediction endpoints
│   │       ├── chat_routes.py     # POST /chat (LLM assistant)
│   │       ├── vendor_routes.py
│   │       ├── utils_routes.py
│   │       └── user_routes.py
│   ├── db/
│   │   ├── connection.py          # DB engine & execute_query
│   │   └── pagination.py
│   ├── ml/
│   │   ├── xgboost_scorer.py      # Train & predict with XGBoost
│   │   └── models/                # Trained model (gitignored)
│   ├── models/                    # Pydantic request models
│   │   └── chat_model.py          # Chat request/response models
│   ├── repositories/              # SQL queries
│   │   ├── scoring.py
│   │   ├── vendor_filter.py
│   │   ├── vendors.py
│   │   └── utils.py
│   ├── scoring/
│   │   └── normalizer.py          # Score normalization utilities
│   ├── services/                  # Business logic
│   │   ├── chat_service.py        # LangGraph chat orchestration
│   │   ├── chat_tools.py          # LangChain @tool functions → scoring_service
│   │   ├── chat_context.py        # Per-request product/vendor context for tools
│   │   ├── llm_service.py         # AzureChatOpenAI + LangGraph agent
│   │   ├── scoring_service.py
│   │   ├── ranking_service.py
│   │   └── weighted_score.py
│   └── main.py
├── requirements.txt
└── .env.example
```

**Architecture pattern:** `Route → Service → Repository → Database`

---

## Setup & Running

### 1. Install dependencies

**Windows (if `pip` is not recognized):**

Python 3.12 is installed but may not be on your PATH. Use the venv in the `Backend` folder:

```powershell
cd Backend

# Create virtual environment (one time)
C:\Users\mudit.mishra1298\AppData\Local\Programs\Python\Python312\python.exe -m venv venv

# Activate venv
.\venv\Scripts\Activate.ps1

# Install packages
python -m pip install -r requirements.txt
```

**After activation**, use `python` and `pip` normally:

```powershell
python -m pip install -r requirements.txt
```

**Linux / macOS:**

```bash
cd Backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Key packages: `fastapi`, `uvicorn`, `sqlalchemy`, `psycopg`, `xgboost`, `numpy`

### 2. Configure environment

Copy `.env.example` to `.env` (or `.env.local`) and set:

**Database**

```env
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=vendor_db
DB_DRIVER=psycopg2
```

**Azure OpenAI (required for chat)**

```env
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_API_VERSION=2024-12-01-preview
```

The app loads `.env.{APP_ENV}` first (default `local` → `.env.local`), then falls back to `.env`.

### 3. Run the API

```powershell
cd Backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

Or without activating the venv:

```powershell
cd Backend
.\venv\Scripts\uvicorn.exe app.main:app --reload
```

### 4. Open API docs

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## API Base URL

All endpoints are prefixed with:

```
/api/v1
```

Example: `GET /api/v1/vendors`

---

## All API Endpoints

### Ranking

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/rank` | Rank vendors for a procurement request (XGBoost or weighted fallback) |

### Chat (LLM Assistant)

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/chat` | Chat with AI assistant — answers questions and returns scores, rankings, predictions |

### Scoring & Prediction

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/scoring/weight-configs` | List all active scoring weight configurations |
| `GET` | `/scoring/weight-configs/default` | Get the default weight configuration |
| `GET` | `/scoring/weight-configs/{config_id}` | Get a specific weight configuration |
| `GET` | `/scoring/vendor-scores/latest` | Latest aggregated vendor scores (materialized view) |
| `GET` | `/scoring/features/{product_id}` | Raw feature scores for all vendors of a product |
| `GET` | `/scoring/seasonal-demand/{product_id}` | Demand forecast by month for a product |
| `GET` | `/scoring/quality/{vendor_id}` | Quality score history for a vendor |
| `GET` | `/scoring/risk/{vendor_id}` | Risk score history for a vendor |
| `GET` | `/scoring/historical-performance/{vendor_id}` | Monthly historical performance for a vendor |
| `GET` | `/scoring/recommendations/{request_id}` | AI recommendations for a procurement request |
| `POST` | `/scoring/train` | Train the XGBoost vendor ranking model |
| `POST` | `/scoring/predict` | Predict/rank vendors using XGBoost (always prefers ML) |

### Vendors

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/vendors` | List vendors (paginated) |
| `GET` | `/vendors/{vendor_id}` | Get vendor by ID |
| `POST` | `/vendors/ids` | Get multiple vendors by IDs |
| `GET` | `/vendors/limit/{limit}` | Get vendors with a row limit |
| `GET` | `/vendor-products` | List vendor-product mappings (paginated) |
| `GET` | `/vendor-recommendations` | List all recommendations (paginated) |
| `GET` | `/categories` | List distinct vendor categories |
| `POST` | `/vendor-by-category` | Get vendors by category names |
| `GET` | `/vendor-production-capacity/{vendor_id}` | Production capacity for a vendor |

### Utils / Reference Data

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/countries` | List all countries |
| `POST` | `/weather-logistics-impact` | Weather events affecting logistics |
| `GET` | `/products-catalog` | List products (paginated) |
| `GET` | `/products-catalog/{product_id}` | Product detail |
| `GET` | `/compliance-certifications` | All compliance certifications |
| `GET` | `/compliance-certifications/vendor/{vendor_id}` | Certifications for a vendor |

### Users

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/users` | List users (paginated) |
| `GET` | `/users/{user_id}` | Get user by ID |

### Pagination

Paginated endpoints accept query parameters:

```
?page=1&page_size=20
```

---

## Chat / LLM Assistant

The chat endpoint is the main integration point for your **UI chat screen**. Users type natural language; the backend uses **LangChain + LangGraph** with **Azure OpenAI** and calls the same scoring services as the REST API.

### How it works (LangGraph)

```
UI sends POST /chat
        │
        ▼
LangGraph ReAct Agent (session_id = thread_id)
        │
        ▼
Azure OpenAI (LangChain AzureChatOpenAI)
        │
        ├── General question → text reply only
        │
        └── Needs data → LangChain @tool (rank_vendors, get_risk_scores, etc.)
                │
                ▼
            scoring_service → DB / XGBoost ML
                │
                ▼
            LangGraph loops back to LLM with tool result
                │
                ▼
UI receives: reply (text) + data (JSON) + actions (what was called)
```

**Stack:** `langgraph` (agent graph) + `langchain-openai` (Azure LLM) + `langchain_core.tools` (tools)

### Request body

```json
{
  "message": "Rank the best vendors for this product",
  "session_id": "optional-uuid-from-previous-response",
  "product_id": "optional-product-uuid",
  "vendor_id": "optional-vendor-uuid",
  "request_id": "optional-procurement-request-uuid"
}
```

| Field | Required | Description |
|---|---|---|
| `message` | Yes | User's question or command |
| `session_id` | No | Send back from previous response to keep conversation context |
| `product_id` | No | Helps the assistant when the user doesn't mention the product |
| `vendor_id` | No | Helps for vendor-specific score questions |
| `request_id` | No | Helps for recommendation lookups |

### Response body

```json
{
  "reply": "Here are the top 3 vendors ranked by score...",
  "session_id": "abc-123-uuid",
  "data": [ { "vendor_name": "...", "rank": 1, "final_score": 85.2 } ],
  "actions": ["rank_vendors"]
}
```

| Field | Description |
|---|---|
| `reply` | Natural language answer for the chat bubble |
| `session_id` | Store in UI state; send on next message |
| `data` | Structured JSON for tables/charts (null if no tool was used) |
| `actions` | List of tools called, e.g. `["rank_vendors"]` |

### Tools the assistant can call

| Tool | What it does |
|---|---|
| `rank_vendors` | Rank vendors for a product |
| `predict_vendors` | ML prediction via XGBoost |
| `get_scoring_features` | Raw feature breakdown per vendor |
| `get_vendor_latest_scores` | Latest scores from materialized view |
| `get_quality_scores` | Quality history for a vendor |
| `get_risk_scores` | Risk history for a vendor |
| `get_seasonal_demand` | Demand forecast for a product |
| `get_recommendations` | Stored recommendations for a request |
| `get_historical_performance` | Monthly performance for a vendor |

### Example chat messages (for UI testing)

- "Rank vendors for product `{product_id}`"
- "What is the risk score for vendor `{vendor_id}`?"
- "Show me the demand forecast for this product"
- "Predict the best vendor using ML"
- "What are the quality scores for this vendor?"

### Session storage

LangGraph **MemorySaver** stores conversation per `session_id` (`thread_id`). Fine for development; use Redis or Postgres checkpointer for production.

### Key files

| File | Purpose |
|---|---|
| `app/services/llm_service.py` | `AzureChatOpenAI` + `create_react_agent` (LangGraph) |
| `app/services/chat_tools.py` | LangChain `@tool` functions wired to `scoring_service` |
| `app/services/chat_context.py` | Passes `product_id` / `vendor_id` from UI to tools |
| `app/services/chat_service.py` | Invokes the LangGraph agent |
| `app/api/routes/chat_routes.py` | `POST /chat` endpoint |
| `app/models/chat_model.py` | Request/response models for the UI |

---

## Scoring & Prediction Engine

The scoring engine evaluates vendors across multiple dimensions pulled from the database.

### Feature dimensions (from `vendor_filter.py`)

When ranking or fetching features, the system loads:

| Feature | Source |
|---|---|
| `overall_quality_score` | `quality_scores` |
| `overall_risk_score` | `risk_scores` |
| `overall_esg_score` | `esg_scores` |
| `reliability_score` | `supplier_reliability_index` |
| `historical_score` | `vendor_historical_performance` |
| `historical_otd_rate` | `vendor_historical_performance` |
| `historical_quality_rate` | `vendor_historical_performance` |
| `historical_csat_score` | `vendor_historical_performance` |
| `on_time_rate` | `delivery_performance` (aggregated) |
| `avg_fill_rate_pct` | `delivery_performance` (aggregated) |
| `available_capacity` | `production_capacity` |
| `current_utilization_pct` | `production_capacity` |
| `compliance_cert_count` | `compliance_certifications` |
| `tier`, `is_preferred`, `is_strategic` | `vendors` |

### Two scoring methods

#### 1. Weighted score (fallback)

Used when no XGBoost model exists or `use_ml=false`.

Defined in `app/services/weighted_score.py`:

**Positive features**

| Feature | Weight |
|---|---|
| `overall_quality_score` | 0.25 |
| `reliability_score` | 0.20 |
| `historical_score` | 0.15 |
| `overall_esg_score` | 0.15 |
| `historical_quality_rate` | 0.10 |
| `historical_otd_rate` | 0.10 |
| `historical_csat_score` | 0.05 |

**Negative features**

| Feature | Weight |
|---|---|
| `overall_risk_score` | 0.10 (subtracted) |

#### 2. XGBoost score (primary, per FRD)

Used when a trained model exists at `app/ml/models/vendor_ranker.pkl`.

- Predicts a vendor suitability score from 16 input features
- Output stored as `ml_score` and `final_score`
- `scoring_method` = `"xgboost"`

### Weight configurations

The database table `scoring_weight_config` stores 20-dimension weight presets:

- Default Balanced
- Cost-Focused
- ESG-Prioritized
- Risk-Averse

These are exposed via the `/scoring/weight-configs` endpoints. The `weight_config_id` field is available on the procurement request model for future integration into composite scoring.

---

## XGBoost ML Module

**File:** `app/ml/xgboost_scorer.py`

### Training

```
POST /api/v1/scoring/train
```

**Training data source:** `vendor_historical_performance` joined with latest quality, risk, ESG, and reliability scores.

**Target variable:** `overall_score` from historical performance (labeled as `target_score`).

**Minimum rows required:** 5

**Model output:** `Backend/app/ml/models/vendor_ranker.pkl`

**Training response example:**

```json
{
  "status": "success",
  "message": "Model trained and saved",
  "rows_used": 120,
  "model_path": ".../app/ml/models/vendor_ranker.pkl"
}
```

### Prediction

```
POST /api/v1/scoring/predict
POST /api/v1/rank
```

Both use the same vendor feature pipeline. `/scoring/predict` always tries ML first; `/rank` respects the `use_ml` flag.

### Feature columns used by XGBoost

```
overall_quality_score, overall_risk_score, overall_esg_score,
reliability_score, historical_score, historical_otd_rate,
historical_quality_rate, historical_csat_score, on_time_rate,
avg_fill_rate_pct, available_capacity, current_utilization_pct,
compliance_cert_count, tier, is_preferred, is_strategic
```

### Model parameters

| Parameter | Value |
|---|---|
| Objective | `reg:squarederror` |
| Max depth | 4 |
| Learning rate (eta) | 0.1 |
| Boost rounds | 50 |

---

## Ranking Flow

```
Procurement Request (product_id, filters)
        │
        ▼
Find active vendors for product (vendor_products)
        │
        ▼
Apply country filters (preferred / excluded)
        │
        ▼
Load feature scores per vendor (vendor_filter)
        │
        ├── XGBoost model exists & use_ml=true?
        │       │
        │       YES → predict_vendor_scores() → ml_score
        │       │
        │       NO  → calculate_weighted_score() → final_score
        │
        ▼
Sort by final_score (descending)
        │
        ▼
Assign rank (1 = best)
        │
        ▼
Return ranked vendor list
```

### Procurement request body

```json
{
  "product_id": "uuid",
  "requried_quanity": "100",
  "required_by_date": "2026-07-01",
  "budget_usd": 50000,
  "quality_grade": "A",
  "preferred_countries": ["USA", "DEU"],
  "excluded_countries": ["CHN"],
  "weight_config_id": null,
  "use_ml": true
}
```

### Rank response fields (per vendor)

| Field | Description |
|---|---|
| `vendor_id` | Vendor UUID |
| `vendor_name` | Vendor name |
| `country_code` | ISO country code |
| `final_score` | Computed score used for ranking |
| `ml_score` | Present when XGBoost is used |
| `scoring_method` | `"xgboost"` or `"weighted"` |
| `rank` | Position (1 = highest score) |
| Plus all raw feature fields | quality, risk, ESG, etc. |

---

## Database Tables Used

| Table / View | Purpose |
|---|---|
| `vendors` | Vendor master data |
| `vendor_products` | Vendor-product pricing & lead time |
| `quality_scores` | Quality assessments |
| `risk_scores` | Composite risk scores |
| `esg_scores` | ESG assessments |
| `supplier_reliability_index` | Reliability dimensions |
| `vendor_historical_performance` | Monthly performance + ML training labels |
| `delivery_performance` | On-time delivery & fill rate |
| `production_capacity` | Capacity & utilization |
| `compliance_certifications` | Valid certifications count |
| `scoring_weight_config` | Configurable 20-dimension weights |
| `seasonal_demand` | Demand forecasts |
| `vendor_recommendations` | Stored AI recommendations |
| `v_vendor_latest_scores` | Materialized view of latest scores |
| `procurement_requests` | Procurement requests |
| `products_catalog` | Product master |
| `countries` | Country reference |
| `weather_logistics_impact` | Weather disruption data |

---

## FRD Mapping

| FRD Requirement | Implementation |
|---|---|
| **FR-010** Search approved vendors | `GET /vendors`, `GET /scoring/features/{product_id}` |
| **FR-013** Filter inactive vendors | Queries filter `is_active = true` and `blacklist_flag = false` |
| **FR-014** Calculate vendor score | `POST /rank`, `POST /scoring/predict` |
| **FR-015** Configurable weightage | `GET /scoring/weight-configs` (DB-driven configs) |
| **FR-016** Rank vendors | `POST /rank` returns sorted list with `rank` |
| **FR-017** Score explanation | `GET /scoring/features/{product_id}` exposes raw dimensions |
| **FR-022–025** Quality analytics | `GET /scoring/quality/{vendor_id}` |
| **FR-026–029** Supply chain / delivery | `delivery_performance` features + `POST /weather-logistics-impact` |
| **FR-037** Generate recommendation | `GET /scoring/recommendations/{request_id}` + chat tool `get_recommendations` |
| **FR-038** Explain recommendation | Chat assistant explains via `reply` field |
| **FR-039** Confidence score | Available on `vendor_recommendations.confidence_pct` |
| **Section 13 – XGBoost** | `app/ml/xgboost_scorer.py` + `/scoring/train` + `/scoring/predict` |
| **Section 13 – LLM** | `POST /chat` — LangGraph agent + LangChain tools + Azure OpenAI |
| **Demand forecasting** | `GET /scoring/seasonal-demand/{product_id}` + chat tool |

---

## Example Requests

### Train XGBoost model

```bash
curl -X POST http://localhost:8000/api/v1/scoring/train
```

### Rank vendors for a product

```bash
curl -X POST http://localhost:8000/api/v1/rank \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "your-product-uuid",
    "requried_quanity": "100",
    "use_ml": true
  }'
```

### Get feature breakdown for scoring UI

```bash
curl http://localhost:8000/api/v1/scoring/features/your-product-uuid
```

### Get demand forecast

```bash
curl http://localhost:8000/api/v1/scoring/seasonal-demand/your-product-uuid
```

### Get recommendations for a procurement request

```bash
curl http://localhost:8000/api/v1/scoring/recommendations/your-request-uuid
```

### Get default scoring weights

```bash
curl http://localhost:8000/api/v1/scoring/weight-configs/default
```

### Chat with the assistant

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Rank the best vendors for this product",
    "product_id": "your-product-uuid"
  }'
```

### Continue a conversation (send session_id from previous response)

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Which one has the lowest risk?",
    "session_id": "session-uuid-from-previous-response",
    "product_id": "your-product-uuid"
  }'
```

### Ask about vendor risk via chat

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me the risk scores for this vendor",
    "vendor_id": "your-vendor-uuid"
  }'
```

---

## Future Enhancements

These are planned or partially stubbed but not yet fully wired:

| Item | Status |
|---|---|
| Use `weight_config_id` in composite score calculation | Field exists on request model; logic not yet applied |
| Persist recommendations from `/rank` into `vendor_recommendations` | Not implemented |
| Persist chat sessions to database | LangGraph MemorySaver only (in-memory) |
| Score normalization in ranking pipeline | `normalizer.py` exists but not used in rank flow yet |
| Retrain model on schedule | Manual via `POST /scoring/train` only |
| Authentication / RBAC | Not implemented |

---

## Quick Reference: Which Endpoint to Use?

| Goal | Endpoint |
|---|---|
| **UI chat (questions + scores + predictions)** | `POST /chat` |
| Rank vendors for procurement | `POST /rank` |
| Force ML prediction | `POST /scoring/predict` |
| Train/retrain XGBoost | `POST /scoring/train` |
| Show score breakdown in UI | `GET /scoring/features/{product_id}` |
| Show quality history | `GET /scoring/quality/{vendor_id}` |
| Show risk history | `GET /scoring/risk/{vendor_id}` |
| Show demand forecast | `GET /scoring/seasonal-demand/{product_id}` |
| Show stored AI recommendations | `GET /scoring/recommendations/{request_id}` |
| Configure scoring weights | `GET /scoring/weight-configs` |

---

*Last updated: June 2026*
