"""OpenAI API integration with deterministic fallback behavior."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from typing import Any

from core.analyzer import create_demo_result, normalize_result
from core.prompt_builder import build_system_prompt, build_user_prompt
from core.schemas import JOBFIT_RESPONSE_FORMAT


DEFAULT_OPENAI_MODEL = "gpt-4o-mini"


@dataclass(frozen=True)
class GenerationResult:
    result: dict[str, Any]
    source: str
    message: str


def get_api_key() -> str | None:
    try:
        import streamlit as st

        secret_value = st.secrets.get("OPENAI_API_KEY")
        if secret_value:
            return str(secret_value)
    except Exception:
        pass

    env_value = os.getenv("OPENAI_API_KEY")
    return env_value if env_value else None


def has_api_key() -> bool:
    return bool(get_api_key())


def _extract_response_text(response: Any) -> str:
    output_text = getattr(response, "output_text", None)
    if output_text:
        return str(output_text)

    output = getattr(response, "output", None)
    if not output:
        return ""

    text_parts: list[str] = []
    for item in output:
        for content in getattr(item, "content", []) or []:
            text = getattr(content, "text", None)
            if text:
                text_parts.append(str(text))
    return "\n".join(text_parts)


def request_openai_result(
    cv_text: str, job_post_text: str, preferences: dict[str, str]
) -> dict[str, Any]:
    api_key = get_api_key()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured.")

    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL),
        input=[
            {"role": "system", "content": build_system_prompt()},
            {"role": "user", "content": build_user_prompt(cv_text, job_post_text, preferences)},
        ],
        text={"format": JOBFIT_RESPONSE_FORMAT},
        temperature=0.2,
    )
    raw_text = _extract_response_text(response)
    parsed = json.loads(raw_text)
    return normalize_result(parsed)


def generate_application_kit(
    cv_text: str,
    job_post_text: str,
    preferences: dict[str, str],
    force_demo: bool = False,
) -> GenerationResult:
    if force_demo:
        return GenerationResult(
            result=create_demo_result(cv_text, job_post_text, preferences),
            source="demo",
            message="Demo Mode is on. The application kit was created with deterministic local analysis.",
        )

    if not has_api_key():
        return GenerationResult(
            result=create_demo_result(cv_text, job_post_text, preferences),
            source="demo",
            message="No OPENAI_API_KEY was found. The app used deterministic Demo Mode instead.",
        )

    try:
        return GenerationResult(
            result=request_openai_result(cv_text, job_post_text, preferences),
            source="api",
            message="Application kit created with the OpenAI API.",
        )
    except Exception as error:
        fallback = create_demo_result(cv_text, job_post_text, preferences)
        fallback["warnings"].append(f"API request failed; Demo Mode fallback was used. Detail: {error}")
        return GenerationResult(
            result=fallback,
            source="demo",
            message="The API request failed, so the app used deterministic Demo Mode instead.",
        )

