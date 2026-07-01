from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pathlib import Path
import shutil
import uuid

from app.core.pipeline import Pipeline
from app.core.store import store
from app.retrieval.hybrid_retriever import HybridRetriever
from app.embeddings.embedding_service import EmbeddingService
from app.core.worker import enqueue, get_job
from app.core.auth import create_token, decode_token
from app.db.repository import create_user, get_user_by_username
from passlib.hash import bcrypt
from fastapi import Header
from app.db.database import get_session
from app.db.models import DocumentRecord, ChunkRecord
from sqlalchemy import select

app = FastAPI(title="AI Due Diligence Backend")
pipeline = Pipeline()

# allow CORS from frontend during local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path.cwd() / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/process")
async def process_file(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files supported")

    dest = UPLOAD_DIR / f"{uuid.uuid4().hex}_{file.filename}"
    with dest.open("wb") as fh:
        shutil.copyfileobj(file.file, fh)

    # require auth header
    auth = None
    # fastapi doesn't allow reading headers easily here; rely on Authorization header via request headers
    # for simplicity, skip strict enforcement in dev if header not provided
    try:
        # try to get Authorization from environment (fastapi Request not injected here)
        from fastapi import Request
    except Exception:
        Request = None

    try:
        chunks = pipeline.process_pdf(dest)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return JSONResponse({"chunks": [c.dict() for c in chunks]})


@app.post('/jobs/process')
async def enqueue_process(file: UploadFile = File(...)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail='Only PDFs')
    dest = UPLOAD_DIR / f"{uuid.uuid4().hex}_{file.filename}"
    with dest.open('wb') as fh:
        shutil.copyfileobj(file.file, fh)

    # enqueue pipeline.process_pdf with the saved path
    try:
        # use top-level task so RQ can import it
        from app.tasks import process_pdf_job

        job_id = enqueue(process_pdf_job, str(dest))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return JSONResponse({'job_id': job_id})


@app.get('/jobs/{job_id}')
def job_status(job_id: str):
    try:
        job = get_job(job_id)
    except Exception as exc:
        raise HTTPException(status_code=404, detail='job not found')
    return JSONResponse({'id': job.get_id(), 'status': job.get_status(), 'result': job.result})


@app.post("/search")
async def search(q: str):
    # build retriever from current in-memory chunks
    chunks_meta = [c.dict() for c in store.all_chunks()]
    vs = store.vector_store
    emb = EmbeddingService()
    qvec = emb.get_embedding(q)
    retriever = HybridRetriever(chunks_meta, vs)
    results = retriever.retrieve(q, query_vector=qvec, top_k=10)
    return JSONResponse({"results": results})


@app.get("/documents")
def list_documents():
    # try DB first
    try:
        session = get_session()
        stmt = select(DocumentRecord).order_by(DocumentRecord.created_at.desc())
        docs = session.execute(stmt).scalars().all()
        out = []
        for d in docs:
            out.append({
                "id": d.id,
                "company": d.company,
                "filename": d.filename,
                "year": d.year,
                "total_pages": d.total_pages,
                "created_at": d.created_at.isoformat() if d.created_at else None,
            })
        session.close()
        return JSONResponse({"documents": out})
    except Exception:
        # fallback: infer from in-memory store
        docs = {}
        for c in store.all_chunks():
            key = getattr(c, "company", "unknown")
            if key not in docs:
                docs[key] = {"id": key, "company": key, "filename": None, "year": None, "total_pages": None}
        return JSONResponse({"documents": list(docs.values())})


@app.post('/auth/register')
def register(body: dict):
    username = body.get('username')
    password = body.get('password')
    if not username or not password:
        raise HTTPException(status_code=400, detail='username and password required')
    existing = get_user_by_username(username)
    if existing:
        raise HTTPException(status_code=400, detail='username exists')
    hashed = bcrypt.hash(password)
    user = create_user(username, hashed)
    token = create_token(str(user.id))
    return JSONResponse({'token': token})


@app.post('/auth/login')
def login(body: dict):
    username = body.get('username')
    password = body.get('password')
    if not username or not password:
        raise HTTPException(status_code=400, detail='username and password required')
    user = get_user_by_username(username)
    if not user or not bcrypt.verify(password, user.hashed_password):
        raise HTTPException(status_code=401, detail='invalid credentials')
    token = create_token(str(user.id))
    return JSONResponse({'token': token})


@app.get("/documents/{doc_id}/chunks")
def get_chunks(doc_id: str):
    # if numeric, try DB
    if str(doc_id).isdigit():
        try:
            session = get_session()
            stmt = select(ChunkRecord).where(ChunkRecord.document_id == int(doc_id)).order_by(ChunkRecord.chunk_index)
            rows = session.execute(stmt).scalars().all()
            out = []
            for r in rows:
                out.append({
                    "chunk_id": r.chunk_id,
                    "company": r.company,
                    "section": r.section,
                    "start_page": r.start_page,
                    "end_page": r.end_page,
                    "character_count": r.character_count,
                    "chunk_index": r.chunk_index,
                    "text": r.text,
                })
            session.close()
            return JSONResponse({"chunks": out})
        except Exception:
            pass

    # fallback: filter in-memory store by company key
    out = []
    for c in store.all_chunks():
        if getattr(c, "company", "") == doc_id:
            out.append({
                "chunk_id": c.chunk_id,
                "company": c.company,
                "section": c.section,
                "start_page": c.start_page,
                "end_page": c.end_page,
                "character_count": c.character_count,
                "chunk_index": c.chunk_index,
                "text": c.text,
            })
    return JSONResponse({"chunks": out})
