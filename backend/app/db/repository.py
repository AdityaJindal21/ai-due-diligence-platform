from __future__ import annotations

from typing import List

from app.db.database import get_session
from app.db.models import DocumentRecord, SectionRecord, ChunkRecord, Base, UserRecord
from sqlalchemy.exc import SQLAlchemyError


def init_db():
    # create tables if not exist
    Base.metadata.create_all(bind=get_session().get_bind())


def create_document_record(metadata) -> DocumentRecord:
    session = get_session()
    try:
        doc = DocumentRecord(
            company=metadata.company,
            filename=metadata.filename,
            filing_type=metadata.filing_type,
            year=getattr(metadata, "year", None),
            source=getattr(metadata, "source", None),
            total_pages=getattr(metadata, "total_pages", None),
        )
        session.add(doc)
        session.commit()
        session.refresh(doc)
        return doc
    except SQLAlchemyError:
        session.rollback()
        raise
    finally:
        session.close()


def add_section(document_id: int, section) -> SectionRecord:
    session = get_session()
    try:
        sec = SectionRecord(
            document_id=document_id,
            title=section.title,
            start_page=section.start_page,
            end_page=section.end_page,
            text=section.text,
        )
        session.add(sec)
        session.commit()
        session.refresh(sec)
        return sec
    finally:
        session.close()


def add_chunk(document_id: int, chunk) -> ChunkRecord:
    session = get_session()
    try:
        c = ChunkRecord(
            document_id=document_id,
            chunk_id=chunk.chunk_id,
            company=chunk.company,
            section=chunk.section,
            start_page=chunk.start_page,
            end_page=chunk.end_page,
            text=chunk.text,
            character_count=chunk.character_count,
            chunk_index=chunk.chunk_index,
        )
        session.add(c)
        session.commit()
        session.refresh(c)
        return c
    finally:
        session.close()


def create_user(username: str, hashed_password: str, full_name: str | None = None, email: str | None = None):
    session = get_session()
    try:
        user = UserRecord(username=username, hashed_password=hashed_password, full_name=full_name, email=email)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    finally:
        session.close()


def get_user_by_username(username: str):
    session = get_session()
    try:
        return session.query(UserRecord).filter(UserRecord.username == username).first()
    finally:
        session.close()
*** End Patch