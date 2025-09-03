# Nutrion: Smart Nutrition and Diet Assistant

## Meal Planner (Mistral)

`meal.py` generates daily macro plans using the Mistral API.

- Required: `MISTRAL_API_KEY`
- Optional: `MISTRAL_MODEL` (model ID). Defaults to the fine‑tuned model used by the maintainer if not overridden.

Ways to run it:
- Use a fine‑tuned model you have access to: set `MISTRAL_MODEL` to your FT model ID (e.g., `ft:ministral-3b-latest:xxxx`)
- Use a base/public model: set `MISTRAL_MODEL` to a base model (e.g., `mistral-small-latest`). Output quality may vary.
- Maintain your own fine‑tune: prepare a small instruction dataset, fine‑tune via the Mistral console/CLI, then set the resulting model ID in `MISTRAL_MODEL`.

Note: If `MISTRAL_API_KEY` is missing, `meal.py` will fail at runtime. Ensure the key is present in `.env` or deployment secrets.

## Overview

Nutrion is a Streamlit-based web application that serves as a comprehensive nutrition and diet assistant. The application provides users with AI-powered nutrition advice, meal analysis capabilities, nutrition tracking dashboards, and report generation features. The system is designed with a modular architecture that separates authentication, database operations, and utility functions for maintainability and scalability.


## Quickstart

- Clone the repo
- Create a virtual environment and install deps
  - Python 3.10+ recommended
  - `pip install -r requirements.txt`
- Copy `.env.example` to `.env` and fill values (see below)
- Run the app
  - `streamlit run app.py`


## Environment Variables

Create a `.env` in the project root. See `.env.example` for a template.

- SUPABASE_URL
- SUPABASE_ANON_KEY
- SUPABASE_SERVICE_ROLE_KEY (optional; for server-side maintenance or ingestion)
- DATABASE_URL (optional; SQLAlchemy URL if not using session-state fallback)
- GOOGLE_API_KEY (required for Gemini LLM + embeddings)
- MISTRAL_API_KEY (required for meal planning in `meal.py`)
- MISTRAL_MODEL (optional; fine-tuned model ID to use for meal planning)

Notes:
- Secrets must NOT be committed. `.gitignore` already excludes `.env`.
- RAG components and `auth.py`/`rag/src/vector_store.py` read credentials from environment variables first.


## Running

- Development: `streamlit run app.py`
- The app uses UTC to determine “today” for meal logs and dashboard. Times are not displayed per meal.


## RAG: Knowledge Base Ingestion

- Place source URLs or use `tools/crawl.py` to build local Markdown documents.
- Configure `rag/config.yaml` (no secrets). Vector store credentials are taken from env.
- Ingest:
  - `python rag/src/ingest.py`
  - Requires `GOOGLE_API_KEY`, `SUPABASE_URL`, and either `SUPABASE_ANON_KEY` or `SUPABASE_SERVICE_ROLE_KEY` in `.env`.


## Deployment

### Streamlit Cloud
- Add your environment variables in Streamlit Secrets or environment settings:
  - SUPABASE_URL, SUPABASE_ANON_KEY, GOOGLE_API_KEY, MISTRAL_API_KEY, and optionally DATABASE_URL
- Ensure `requirements.txt` is used by the service.

### Docker (optional)
- You can create a simple Dockerfile if needed. Not provided by default.


## Security & Privacy

- No secrets are hardcoded. Use environment variables (`.env`) locally.
- Authentication integrates with Supabase Auth; fallback session-state is for development only.
- All timestamps are stored in UTC; the UI computes “today” in UTC.
- Optional maintenance: a button allows users to clear prior days’ meals.


## Project Structure (high-level)

- `app.py` — Streamlit UI, RAG wiring, timezone-aware filtering.
- `auth.py` — Sign up / login via Supabase; loads creds from env.
- `database.py` — `DatabaseManager` for meals, analyses, preferences, and cleanup helpers.
- `rag/` — RAG ingestion and vector store setup (Supabase Vector Store via env).
- `tools/` — Utilities like `crawl.py` for building a nutrition KB.


## Troubleshooting

- RAG not initializing: Ensure `GOOGLE_API_KEY` is set and Supabase env vars are present.
- Supabase connection issues: Verify `SUPABASE_URL` and keys. For SQLAlchemy DB, verify `DATABASE_URL`.



