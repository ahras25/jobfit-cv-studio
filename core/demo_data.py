"""Sample data helpers for Demo Mode."""

from __future__ import annotations

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
ASSETS_DIR = BASE_DIR / "assets"


def load_sample_cv() -> str:
    return (ASSETS_DIR / "sample_cv.txt").read_text(encoding="utf-8")


def load_sample_job_post() -> str:
    return (ASSETS_DIR / "sample_job_post.txt").read_text(encoding="utf-8")


def default_preferences() -> dict[str, str]:
    return {
        "target_role": "Customer Success Operations Specialist",
        "output_language": "English",
        "tone": "professional",
        "detail_level": "balanced",
    }

