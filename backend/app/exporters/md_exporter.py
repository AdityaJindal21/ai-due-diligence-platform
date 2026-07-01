from __future__ import annotations

from pathlib import Path
from typing import List


def export_markdown(title: str, chunks: List[dict], dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", encoding="utf-8") as fh:
        fh.write(f"# {title}\n\n")
        for c in chunks:
            fh.write(f"## Section: {c.get('section')} (pages {c.get('start_page')}-{c.get('end_page')})\n\n")
            fh.write(c.get("text", "") + "\n\n")
    return dest
*** End Patch