"""Prompt construction for the OpenAI API request."""

from __future__ import annotations


def build_system_prompt() -> str:
    return (
        "You are a practical job application writing assistant. Return JSON only. "
        "Do not fabricate experience, companies, degrees, dates, certifications, tools, metrics, or job history. "
        "Rewrite only from the information provided by the user. Identify gaps honestly. "
        "Use concrete, applicant-friendly language and make every recommendation actionable."
    )


def build_user_prompt(
    cv_text: str, job_post_text: str, preferences: dict[str, str]
) -> str:
    target_role = preferences.get("target_role") or "Not specified"
    language = preferences.get("output_language", "English")
    tone = preferences.get("tone", "professional")
    detail_level = preferences.get("detail_level", "balanced")

    return f"""
Return JSON only using the required schema.

Target role: {target_role}
Target language: {language}
Preferred tone: {tone}
Detail level: {detail_level}

Tasks:
1. Score the CV-job fit from 0 to 100.
2. List strong matches between the CV and job post.
3. List missing keywords from the job post that are not clearly present in the CV.
4. Identify weak areas honestly.
5. Rewrite selected CV bullet points without inventing new facts.
6. Write a tailored cover letter.
7. Write a short LinkedIn outreach message.
8. Provide interview preparation questions.
9. Provide an application checklist.
10. Include warnings for missing evidence, risky assumptions, or input limitations.

CV or resume text:
---
{cv_text}
---

Job description:
---
{job_post_text}
---
""".strip()

