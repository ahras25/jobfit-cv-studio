"""Shared result schema definitions."""

from __future__ import annotations

from typing import Any


RESULT_FIELDS = [
    "match_score",
    "summary",
    "strong_matches",
    "missing_keywords",
    "weak_areas",
    "cv_bullet_rewrites",
    "cover_letter",
    "linkedin_message",
    "interview_questions",
    "application_checklist",
    "warnings",
]

BULLET_REWRITE_FIELDS = ["before", "after", "reason"]

EMPTY_RESULT: dict[str, Any] = {
    "match_score": 0,
    "summary": "",
    "strong_matches": [],
    "missing_keywords": [],
    "weak_areas": [],
    "cv_bullet_rewrites": [],
    "cover_letter": "",
    "linkedin_message": "",
    "interview_questions": [],
    "application_checklist": [],
    "warnings": [],
}

JOBFIT_RESPONSE_FORMAT: dict[str, Any] = {
    "type": "json_schema",
    "name": "jobfit_application_kit",
    "description": "A complete job application preparation kit.",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "match_score": {"type": "integer"},
            "summary": {"type": "string"},
            "strong_matches": {"type": "array", "items": {"type": "string"}},
            "missing_keywords": {"type": "array", "items": {"type": "string"}},
            "weak_areas": {"type": "array", "items": {"type": "string"}},
            "cv_bullet_rewrites": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "before": {"type": "string"},
                        "after": {"type": "string"},
                        "reason": {"type": "string"},
                    },
                    "required": BULLET_REWRITE_FIELDS,
                    "additionalProperties": False,
                },
            },
            "cover_letter": {"type": "string"},
            "linkedin_message": {"type": "string"},
            "interview_questions": {"type": "array", "items": {"type": "string"}},
            "application_checklist": {"type": "array", "items": {"type": "string"}},
            "warnings": {"type": "array", "items": {"type": "string"}},
        },
        "required": RESULT_FIELDS,
        "additionalProperties": False,
    },
}

