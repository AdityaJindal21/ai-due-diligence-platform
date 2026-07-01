from __future__ import annotations

import re
import unicodedata

from app.schemas.document import Document, Page


class TextCleaner:
    def clean_document(self, document: Document) -> Document:
        cleaned_pages: list[Page] = []

        for page in document.pages:
            cleaned_text = self.clean_text(page.text)

            cleaned_pages.append(
                page.model_copy(
                    update={
                        "text": cleaned_text,
                        "character_count": len(cleaned_text),
                    }
                )
            )

        return document.model_copy(
            update={
                "pages": cleaned_pages,
            }
        )

    def clean_text(self, text: str) -> str:
        if not text:
            return ""

        text = self.normalize_unicode(text)
        text = self.normalize_whitespace(text)
        text = self.remove_extra_blank_lines(text)
        text = self.strip_trailing_spaces(text)

        return text.strip()

    def normalize_unicode(self, text: str) -> str:
        text = unicodedata.normalize("NFKC", text)

        replacements = {
            "\u2013": "-",      # en dash
            "\u2014": "-",      # em dash
            "\u2026": "...",    # ellipsis
            "\u2018": "'",      # left single quote
            "\u2019": "'",      # right single quote
            "\u201c": '"',      # left double quote
            "\u201d": '"',      # right double quote
            "\u201e": '"',
            "\u00A0": " ",      # non-breaking space
            "\u2022": "-",      # bullet
        }

        for old, new in replacements.items():
            text = text.replace(old, new)

        return text

    def normalize_whitespace(self, text: str) -> str:
        lines = []

        for line in text.splitlines():
            line = line.replace("\t", " ")
            line = re.sub(r" {2,}", " ", line)
            lines.append(line)

        return "\n".join(lines)

    def remove_extra_blank_lines(self, text: str) -> str:
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        return re.sub(r"\n\s*\n+", "\n\n", text)

    def strip_trailing_spaces(self, text: str) -> str:
        return re.sub(r"[ \t]+$", "", text, flags=re.MULTILINE)