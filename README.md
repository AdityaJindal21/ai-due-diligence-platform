# AI Due Diligence Platform

Enterprise AI system for analyzing SEC filings using Retrieval-Augmented Generation (RAG).

## Planned Features

## Tech Stack

- Python
- FastAPI
- OpenAI
- ChromaDB
- PostgreSQL
- Docker
- Next.js

## Status

🚧 In Development

# Enterprise AI Due Diligence Platform

This repository implements an end-to-end pipeline for ingesting, processing, and
chunking SEC 10-K filings to enable high-quality retrieval and downstream LLM
workflows.

Important components:

- backend/app/ingestion/loader.py — PDF loader (PyMuPDF or PyPDF2 fallback)
- backend/app/preprocessing/cleaner.py — text cleaning utilities
- backend/app/preprocessing/section_parser.py — detect major ITEM sections
- backend/app/preprocessing/chunker.py — section-aware chunk generator
- backend/app/core/pipeline.py — simple pipeline wiring
- backend/app/api.py — minimal FastAPI endpoints for processing uploads
- scripts/test_sections.py — test script for section parsing
- scripts/test_chunker.py — test script for chunking

Quick start

1. Create a Python environment (recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

2. Run the chunker test on the sample Apple 10-K provided at `data/raw/apple_10k.pdf`:

```bash
python3 scripts/test_chunker.py data/raw/apple_10k.pdf
```

3. Run the section parser test:

```bash
python3 scripts/test_sections.py data/raw/apple_10k.pdf
```

4. Start the backend API (after installing dependencies):

```bash
uvicorn app.api:app --reload --host 0.0.0.0 --port 8000
```

Docker Compose

Start the full stack (Postgres, Chroma stub, backend, frontend):

```bash
docker compose up --build
```

The backend will be available at `http://localhost:8000` and the frontend at `http://localhost:3000`.

Database migrations

When you have the Python dependencies installed, run the alembic migrations from the `backend` folder:

```bash
cd backend
alembic upgrade head
```

If you need to create a new migration after changing models:

```bash
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

Notes

- PDF extraction requires either `PyMuPDF` (package name `PyMuPDF`) or `PyPDF2`.
	Install via `pip install PyMuPDF` for best results.
- If you prefer system utilities, `pdftotext` (from poppler) is another option.
- The project includes lightweight fallbacks so unit tests can run in minimal
	environments, but installing the recommended Python packages yields the best
	parsing accuracy.

Next steps

- Add embedding generation and a vector store adapter (ChromaDB)
- Implement BM25 and hybrid retrieval pipeline
- Add FastAPI endpoints for searching and report generation
- Add frontend UI (Next.js) for user upload and analysis

License: MIT