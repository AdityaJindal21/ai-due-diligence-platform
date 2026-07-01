from __future__ import annotations

import re

from app.schemas.document import Document
from app.schemas.section import Section


class SectionParser:

    ITEM_PATTERN = re.compile(
        r"^\s*ITEM\s+\d+[A-Z]?\.?\s+.*$",
        re.IGNORECASE | re.MULTILINE,
    )

    def parse(self, document: Document) -> list[Section]:
        sections: list[Section] = []

        current_title: str | None = None
        current_start_page: int | None = None

        for page in document.pages:

            page_text = page.text or ""

            first_lines = "\n".join(page_text.splitlines()[:40])

            match = self.ITEM_PATTERN.search(first_lines)

            if match:

                if current_title is not None:

                    end_page = page.page_number - 1

                    sections.append(
                        Section(
                            title=current_title,
                            start_page=current_start_page,
                            end_page=end_page,
                            text=self._collect_text(
                                document,
                                current_start_page,
                                end_page,
                            ),
                        )
                    )

                current_title = match.group().strip()
                current_start_page = page.page_number

        if current_title is not None:

            end_page = document.metadata.total_pages

            sections.append(
                Section(
                    title=current_title,
                    start_page=current_start_page,
                    end_page=end_page,
                    text=self._collect_text(
                        document,
                        current_start_page,
                        end_page,
                    ),
                )
            )

        return sections

    @staticmethod
    def _collect_text(
        document: Document,
        start_page: int,
        end_page: int,
    ) -> str:
        """
        Collect text belonging to a page range.
        """

        return "\n\n".join(
            page.text
            for page in document.pages
            if start_page <= page.page_number <= end_page
        )