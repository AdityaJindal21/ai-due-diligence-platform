from __future__ import annotations

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class DocumentRecord(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    company = Column(String(255), index=True)
    filename = Column(String(512))
    filing_type = Column(String(100))
    year = Column(Integer)
    source = Column(String(255))
    total_pages = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    sections = relationship("SectionRecord", back_populates="document")
    chunks = relationship("ChunkRecord", back_populates="document")


class UserRecord(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(150), unique=True, index=True)
    hashed_password = Column(String(512))
    full_name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class SectionRecord(Base):
    __tablename__ = "sections"
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), index=True)
    title = Column(String(512))
    start_page = Column(Integer)
    end_page = Column(Integer)
    text = Column(Text)

    document = relationship("DocumentRecord", back_populates="sections")


class ChunkRecord(Base):
    __tablename__ = "chunks"
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), index=True)
    chunk_id = Column(String(255), index=True)
    company = Column(String(255))
    section = Column(String(255))
    start_page = Column(Integer)
    end_page = Column(Integer)
    text = Column(Text)
    character_count = Column(Integer)
    chunk_index = Column(Integer)

    document = relationship("DocumentRecord", back_populates="chunks")
