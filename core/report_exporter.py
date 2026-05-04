"""Report export helpers."""

from __future__ import annotations

import re
from typing import Any


def filename_safe(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip())
    cleaned = cleaned.strip(".-")
    return cleaned or "jobfit-report"


def _list_markdown(items: list[str]) -> str:
    if not items:
        return "- None listed"
    return "\n".join(f"- {item}" for item in items)


def _list_text(items: list[str]) -> str:
    if not items:
        return "None listed"
    return "\n".join(f"* {item}" for item in items)


def export_markdown(result: dict[str, Any], preferences: dict[str, str]) -> str:
    rewrites = result.get("cv_bullet_rewrites", [])
    rewrite_lines = []
    for item in rewrites:
        rewrite_lines.append(
            "### Rewrite\n"
            f"Before: {item.get('before', '')}\n\n"
            f"After: {item.get('after', '')}\n\n"
            f"Reason: {item.get('reason', '')}"
        )

    return f"""# JobFit CV Studio Report

Target role: {preferences.get("target_role") or "Not specified"}
Language: {preferences.get("output_language", "English")}
Tone: {preferences.get("tone", "professional")}
Detail level: {preferences.get("detail_level", "balanced")}

## Match Score

{result.get("match_score", 0)}/100

## Summary

{result.get("summary", "")}

## Strong Matches

{_list_markdown(result.get("strong_matches", []))}

## Missing Keywords

{_list_markdown(result.get("missing_keywords", []))}

## Weak Areas

{_list_markdown(result.get("weak_areas", []))}

## CV Bullet Rewrites

{chr(10).join(rewrite_lines) if rewrite_lines else "No rewrites listed."}

## Cover Letter

{result.get("cover_letter", "")}

## LinkedIn Outreach Message

{result.get("linkedin_message", "")}

## Interview Preparation Questions

{_list_markdown(result.get("interview_questions", []))}

## Application Checklist

{_list_markdown(result.get("application_checklist", []))}

## Warnings

{_list_markdown(result.get("warnings", []))}
"""


def export_text(result: dict[str, Any], preferences: dict[str, str]) -> str:
    rewrite_lines = []
    for item in result.get("cv_bullet_rewrites", []):
        rewrite_lines.append(
            "Rewrite\n"
            f"Before: {item.get('before', '')}\n"
            f"After: {item.get('after', '')}\n"
            f"Reason: {item.get('reason', '')}"
        )

    return f"""JobFit CV Studio Report

Target role: {preferences.get("target_role") or "Not specified"}
Language: {preferences.get("output_language", "English")}
Tone: {preferences.get("tone", "professional")}
Detail level: {preferences.get("detail_level", "balanced")}

Match Score
{result.get("match_score", 0)}/100

Summary
{result.get("summary", "")}

Strong Matches
{_list_text(result.get("strong_matches", []))}

Missing Keywords
{_list_text(result.get("missing_keywords", []))}

Weak Areas
{_list_text(result.get("weak_areas", []))}

CV Bullet Rewrites
{chr(10).join(rewrite_lines) if rewrite_lines else "No rewrites listed."}

Cover Letter
{result.get("cover_letter", "")}

LinkedIn Outreach Message
{result.get("linkedin_message", "")}

Interview Preparation Questions
{_list_text(result.get("interview_questions", []))}

Application Checklist
{_list_text(result.get("application_checklist", []))}

Warnings
{_list_text(result.get("warnings", []))}
"""

