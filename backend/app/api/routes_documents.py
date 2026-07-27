import os
import shutil
import uuid

from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Document
from app.db.schemas import DocumentOut
from app.rag.ingestion import load_pdf, ingest_chunks

router = APIRouter(prefix="/documents", tags=["documents"])

UPLOAD_DIR = "/tmp/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload", response_model=DocumentOut)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    doc = Document(filename=file.filename, source_type="pdf", status="processing")
    db.add(doc)
    db.commit()
    db.refresh(doc)

    dest_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{file.filename}")
    with open(dest_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        chunks = load_pdf(dest_path, source_name=file.filename)
        count = ingest_chunks(chunks, doc_id=str(doc.id))
        doc.status = "indexed"
        doc.chunk_count = count
    except Exception:
        doc.status = "failed"
    finally:
        db.commit()
        db.refresh(doc)
        os.remove(dest_path)

    return doc


@router.get("", response_model=list[DocumentOut])
def list_documents(db: Session = Depends(get_db)):
    return db.query(Document).order_by(Document.uploaded_at.desc()).all()
