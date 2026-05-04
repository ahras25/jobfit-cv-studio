"""Input validation and text cleanup utilities."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TextQuality:
    char_count: int
    word_count: int
    line_count: int
    too_short: bool
    signal: str


def clean_text(text: str) -> str:
    """Trim each line and collapse repeated spaces while preserving readable blocks."""
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [" ".join(line.strip().split()) for line in normalized.split("\n")]

    cleaned_lines: list[str] = []
    previous_blank = False
    for line in lines:
        if not line:
            if not previous_blank and cleaned_lines:
                cleaned_lines.append("")
            previous_blank = True
            continue
        cleaned_lines.append(line)
        previous_blank = False

    return "\n".join(cleaned_lines).strip()


def detect_too_short_input(text: str) -> bool:
    cleaned = clean_text(text)
    word_count = len(cleaned.split())
    return len(cleaned) < 120 or word_count < 25


def estimate_text_quality(text: str) -> TextQuality:
    cleaned = clean_text(text)
    words = cleaned.split()
    lines = [line for line in cleaned.splitlines() if line.strip()]
    too_short = detect_too_short_input(cleaned)

    if not cleaned:
        signal = "empty"
    elif too_short:
        signal = "too short"
    elif len(words) < 120:
        signal = "usable but brief"
    else:
        signal = "usable"

    return TextQuality(
        char_count=len(cleaned),
        word_count=len(words),
        line_count=len(lines),
        too_short=too_short,
        signal=signal,
    )


def validate_inputs(
    cv_text: str, job_post_text: str, use_sample_data: bool
) -> list[str]:
    if use_sample_data:
        return []

    errors: list[str] = []
    if not clean_text(cv_text):
        errors.append("CV or resume text is required.")
    if not clean_text(job_post_text):
        errors.append("Job description text is required.")
    return errors

