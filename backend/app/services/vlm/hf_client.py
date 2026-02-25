from __future__ import annotations

import base64
import os
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import List

from openai import OpenAI
from PIL import Image


@dataclass(frozen=True)
class VLMResult:
    text: str
    confidence: float | None = None


def build_grid_image(
    image_paths: List[Path],
    cols: int = 4,
    tile_w: int = 384,
) -> Image.Image:
    imgs: List[Image.Image] = []
    for p in image_paths:
        im = Image.open(p).convert("RGB")
        w, h = im.size
        new_h = max(1, int(tile_w * (h / max(1, w))))
        im = im.resize((tile_w, new_h))
        imgs.append(im)

    if not imgs:
        raise ValueError("No keyframes found to build grid.")

    rows = (len(imgs) + cols - 1) // cols
    tile_h = max(im.size[1] for im in imgs)

    grid = Image.new("RGB", (cols * tile_w, rows * tile_h), (255, 255, 255))

    for i, im in enumerate(imgs):
        r = i // cols
        c = i % cols
        x = c * tile_w
        y = r * tile_h
        grid.paste(im, (x, y))

    return grid


def image_to_data_url_jpeg(im: Image.Image, quality: int = 90) -> str:
    buf = BytesIO()
    im.save(buf, format="JPEG", quality=quality)
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{b64}"


async def describe_scene_hf(keyframe_paths: List[Path]) -> VLMResult:
    token = os.environ.get("HF_TOKEN")
    model = os.environ.get("HF_VLM_MODEL")
    if not token:
        raise RuntimeError("HF_TOKEN env var is missing")
    if not model:
        raise RuntimeError("HF_VLM_MODEL env var is missing")

    # build 2x4 grid from up to 8 keyframes
    grid = build_grid_image(keyframe_paths[:8], cols=4, tile_w=384)
    img_url = image_to_data_url_jpeg(grid)

    client = OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=token,
    )

    prompt = (
    """Describe only what is visually observable across these ordered keyframes. "
    "Do not invent events or objects. "
    "Write 3-4 sentences describing actions and changes over time."""
    )

    resp = client.chat.completions.create(
        model=model,
        temperature=0.0,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": img_url}},
                ],
            }
        ],
    )

    text = (resp.choices[0].message.content or "").strip()
    if not text:
        text = "(no description)"

    return VLMResult(text=text, confidence=None)