from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List

from openai import OpenAI


@dataclass(frozen=True)
class NarrativeResult:
    narrative: str
    summary: str
    structured: Dict[str, Any]


def generate_narrative_from_scenes(scene_lines: List[str]) -> NarrativeResult:
    """
    Build a coherent job-level narrative from scene descriptions (text-only).

    Env required:
      HF_TOKEN
      HF_LLM_MODEL  e.g. "meta-llama/Llama-3.1-8B-Instruct:groq"
    """
    token = os.environ.get("HF_TOKEN")
    model = os.environ.get("HF_LLM_MODEL")
    if not token:
        raise RuntimeError("HF_TOKEN env var is missing")
    if not model:
        raise RuntimeError("HF_LLM_MODEL env var is missing")

    client = OpenAI(base_url="https://router.huggingface.co/v1", api_key=token)

    scenes_text = "\n".join(f"- {line}" for line in scene_lines)

    prompt = f"""
You are given ordered scene notes from a video. Write a coherent narrative and a summary.

Rules:
- Use ONLY the provided scene notes. Do not invent new events.
- If something is unclear, keep it vague instead of guessing.
- Keep the narrative readable and connected.

Return STRICT JSON with exactly these keys:
{{
  "narrative": "1-3 paragraphs",
  "summary": "5 bullet points (use \\n- )",
  "structured": {{
    "main_characters": [],
    "setting": "",
    "key_events": [],
    "notable_objects": [],
    "timeline": [{{"t":"start-end sec","event":""}}],
    "open_questions": []
  }}
}}

Scene notes (ordered):
{scenes_text}
""".strip()

    resp = client.chat.completions.create(
        model=model,
        temperature=0.2,  # slightly >0 helps coherence, still controlled
        messages=[{"role": "user", "content": prompt}],
    )

    raw = (resp.choices[0].message.content or "").strip()

    #attempting strict JSON parse; if model adds extra text, salvage the JSON block.
    data = None
    try:
        data = json.loads(raw)
    except Exception:
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1 and end > start:
            data = json.loads(raw[start : end + 1])
        else:
            raise RuntimeError(f"LLM did not return JSON. Got: {raw[:400]}")

    narrative = (data.get("narrative") or "").strip()
    summary = data.get("summary")

    if isinstance(summary, list):
        parts = []
        for x in summary:
            if isinstance(x, str):
                parts.append(x)
            elif isinstance(x, dict):
                parts.append(x.get("text", ""))
            else:
                parts.append(str(x))
        summary = " ".join(parts)

    elif isinstance(summary, dict):
        summary = summary.get("text", "")

    summary = (summary or "").strip()
    structured = data.get("structured") or {}

    return NarrativeResult(narrative=narrative, summary=summary, structured=structured)