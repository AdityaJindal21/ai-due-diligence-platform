from __future__ import annotations

import json
import os
from typing import List

try:
    import openai
except Exception:
    openai = None


PROMPT_TEMPLATE = """
You are an assistant that produces a structured investment memo in JSON.
Given the following context chunks and a query, produce a JSON object with keys:
- overview
- risks
- financial_highlights
- recommendations
Include citations as an array of {"page": <n>, "section": <name>} where relevant.

Context:
{context}

Query: {query}

Respond only with valid JSON matching the schema.
"""


class LLMOrchestrator:
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model

    def generate_memo(self, query: str, chunks: List[dict]) -> dict:
        context = "\n\n".join([f"[Pages {c['chunk']['start_page']}-{c['chunk']['end_page']}] {c['chunk']['text']}" for c in chunks])
        prompt = PROMPT_TEMPLATE.format(context=context, query=query)
        if openai is not None:
            try:
                resp = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.0,
                )
                content = resp["choices"][0]["message"]["content"]
                return json.loads(content)
            except Exception:
                pass
        # fallback: simple aggregation
        overview = chunks[0]["chunk"]["text"][:1000] if chunks else ""
        return {
            "overview": overview,
            "risks": [],
            "financial_highlights": [],
            "recommendations": [],
        }
