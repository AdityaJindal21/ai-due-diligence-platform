from __future__ import annotations

import re
from typing import List, Tuple

from app.schemas.chunk import Chunk
from app.schemas.document import Document
from app.schemas.section import Section
from app.ingestion.section_parser import SectionParser
from app.preprocessing.token_chunker import split_tokens


class Chunker:
	def __init__(self, chunk_size: int = 1000, overlap: int = 200):
		self.chunk_size = chunk_size
		self.overlap = overlap

	def chunk_document(self, document: Document) -> List[Chunk]:
		"""Chunk an entire Document by sections.

		Returns a list of `Chunk` objects covering all detected sections.
		"""
		parser = SectionParser()
		sections = parser.parse(document)

		chunks: List[Chunk] = []
		idx = 1
		for sec in sections:
			sec_chunks, idx = self.chunk_section(sec, document, start_index=idx)
			chunks.extend(sec_chunks)

		return chunks

	def chunk_section(self, section: Section, document: Document, start_index: int = 1) -> Tuple[List[Chunk], int]:
		"""Chunk a single Section and return (chunks, next_index).

		Uses character-based recursive splitting with configured chunk_size and overlap.
		"""
		chunks: List[Chunk] = []
		splits = self.split_text(section.text, self.chunk_size, self.overlap)

		# build page char bounds for mapping offsets back to page numbers
		page_texts = []
		for p in document.pages:
			if section.start_page <= p.page_number <= section.end_page:
				page_texts.append((p.page_number, p.text or ""))

		page_bounds = []  # list of (page_number, start_char, end_char)
		cursor = 0
		for page_num, txt in page_texts:
			start = cursor
			end = start + len(txt)
			page_bounds.append((page_num, start, end))
			cursor = end

		idx = start_index
		for start_char, end_char, piece in splits:
			start_page = self._page_for_offset(page_bounds, start_char, default=section.start_page)
			end_page = self._page_for_offset(page_bounds, max(0, end_char - 1), default=section.end_page)
			chunk = self.create_chunk(
				company=document.metadata.company,
				year=document.metadata.year,
				section_title=section.title,
				start_page=start_page,
				end_page=end_page,
				text=piece,
				chunk_index=idx,
			)
			chunks.append(chunk)
			idx += 1

		return chunks, idx

	def split_text(self, text: str, chunk_size: int, overlap: int) -> List[Tuple[int, int, str]]:
		"""Split text into (start_char, end_char, substring) tuples.

		Simple sliding window: advance by chunk_size - overlap each iteration.
		"""
		# Attempt token-aware split first (best-effort); fallback to char windows
		try:
			splits = split_tokens(text, chunk_size, overlap)
			# if token splitter produced a single chunk that covers more than chunk_size,
			# fall back to character-based windows to ensure multiple chunks when expected.
			if len(splits) == 1:
				slen = splits[0][1] - splits[0][0]
				if slen > chunk_size:
					raise ValueError("token split produced single oversized chunk; fallback to char windows")
			return splits
		except Exception:
			if not text:
				return []
			results: List[Tuple[int, int, str]] = []
			start = 0
			length = len(text)
			step = max(1, chunk_size - overlap)
			while start < length:
				end = min(start + chunk_size, length)
				piece = text[start:end]
				results.append((start, end, piece))
				if end == length:
					break
				start = end - overlap
			return results

	def create_chunk(self, *, company: str, year: int, section_title: str, start_page: int, end_page: int, text: str, chunk_index: int) -> Chunk:
		company_key = re.sub(r"[^0-9a-zA-Z]+", "_", company.lower()).strip("_")
		year_part = str(year) if year else "unknown"
		chunk_id = f"{company_key}_{year_part}_chunk_{chunk_index:03d}"

		return Chunk(
			chunk_id=chunk_id,
			company=company,
			section=section_title,
			start_page=start_page,
			end_page=end_page,
			text=text,
			character_count=len(text),
			chunk_index=chunk_index,
		)

	def _page_for_offset(self, page_bounds: List[Tuple[int, int, int]], offset: int, default: int) -> int:
		"""Map a character offset within a section to a page number using page_bounds.

		page_bounds is a list of (page_number, start_char, end_char) with start_char/end_char
		being cumulative offsets within the section.
		"""
		for page_num, start, end in page_bounds:
			if start <= offset < end:
				return page_num
		return default


__all__ = ["Chunker"]
