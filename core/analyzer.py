"""Deterministic local analysis and result normalization."""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
import re
from typing import Any

from core.schemas import BULLET_REWRITE_FIELDS, EMPTY_RESULT, RESULT_FIELDS
from core.validators import clean_text, detect_too_short_input


STOPWORDS = {
    "about",
    "after",
    "again",
    "also",
    "and",
    "are",
    "based",
    "been",
    "being",
    "but",
    "can",
    "candidate",
    "company",
    "customer",
    "description",
    "for",
    "from",
    "has",
    "have",
    "into",
    "job",
    "more",
    "our",
    "role",
    "that",
    "the",
    "their",
    "this",
    "through",
    "with",
    "will",
    "work",
    "you",
    "your",
}


def _tokenize(text: str) -> list[str]:
    return [
        match.group(0).lower()
        for match in re.finditer(r"\b[a-zA-Z][a-zA-Z0-9+#.-]{2,}\b", text)
    ]


def extract_keywords(text: str, limit: int = 24) -> list[str]:
    tokens = [token for token in _tokenize(text) if token not in STOPWORDS]
    counts = Counter(tokens)
    first_seen: dict[str, int] = {}
    for index, token in enumerate(tokens):
        first_seen.setdefault(token, index)

    ranked = sorted(counts, key=lambda token: (-counts[token], first_seen[token], token))
    return ranked[:limit]


def calculate_basic_match_score(cv_text: str, job_post_text: str) -> int:
    job_keywords = extract_keywords(job_post_text)
    if not job_keywords:
        return 0

    cv_tokens = set(_tokenize(cv_text))
    matched = [keyword for keyword in job_keywords if keyword in cv_tokens]
    base_score = round((len(matched) / len(job_keywords)) * 100)

    if detect_too_short_input(cv_text):
        base_score -= 10
    if detect_too_short_input(job_post_text):
        base_score -= 5

    return max(0, min(100, base_score))


def analyze_locally(
    cv_text: str, job_post_text: str, preferences: dict[str, str]
) -> dict[str, Any]:
    job_keywords = extract_keywords(job_post_text)
    cv_tokens = set(_tokenize(cv_text))
    strong_matches = [keyword for keyword in job_keywords if keyword in cv_tokens][:10]
    missing_keywords = [keyword for keyword in job_keywords if keyword not in cv_tokens][:10]

    return {
        "match_score": calculate_basic_match_score(cv_text, job_post_text),
        "strong_matches": strong_matches,
        "missing_keywords": missing_keywords,
        "target_role": preferences.get("target_role") or "the target role",
    }


def _language_pack(language: str) -> dict[str, str]:
    packs = {
        "Turkish": {
            "summary": "CV metniniz iş ilanındaki bazı gereksinimlerle örtüşüyor. En iyi sonuç için ölçülebilir başarıları ve eksik anahtar kelimeleri daha görünür hale getirin.",
            "cover_intro": "Merhaba,",
            "cover_close": "Saygılarımla,",
            "linkedin": "Merhaba, bu pozisyonla ilgileniyorum ve deneyimimin özellikle {matches} alanlarında değer katabileceğini düşünüyorum.",
            "warning": "Demo Mode kullanıldı; sonuçlar deterministik yerel analizden üretildi.",
        },
        "Dutch": {
            "summary": "Je cv sluit deels aan op de functie-eisen. Maak relevante trefwoorden, meetbare resultaten en ontbrekende aandachtspunten duidelijker zichtbaar.",
            "cover_intro": "Beste hiring team,",
            "cover_close": "Met vriendelijke groet,",
            "linkedin": "Hallo, ik ben geinteresseerd in deze functie en denk dat mijn ervaring met {matches} goed aansluit.",
            "warning": "Demo Mode is gebruikt; de output komt uit deterministische lokale analyse.",
        },
        "English": {
            "summary": "Your CV matches several requirements in the job post. Improve the application by making measurable results, role-specific keywords, and gap areas easier to see.",
            "cover_intro": "Hello,",
            "cover_close": "Sincerely,",
            "linkedin": "Hello, I am interested in this role and believe my experience with {matches} would be relevant to your team.",
            "warning": "Demo Mode was used; output was created with deterministic local analysis.",
        },
    }
    return packs.get(language, packs["English"])


def _detail_count(detail_level: str, short: int, balanced: int, detailed: int) -> int:
    return {"short": short, "balanced": balanced, "detailed": detailed}.get(
        detail_level, balanced
    )


def _extract_cv_bullets(cv_text: str, count: int) -> list[str]:
    lines = [line.strip(" -*\u2022\t") for line in clean_text(cv_text).splitlines()]
    bullets = [line for line in lines if len(line.split()) >= 5]
    if not bullets:
        bullets = ["Add a role-relevant achievement from your CV."]
    return bullets[:count]


def _create_bullet_rewrites(
    cv_text: str, strong_matches: list[str], missing_keywords: list[str], count: int
) -> list[dict[str, str]]:
    bullets = _extract_cv_bullets(cv_text, count)
    focus_terms = strong_matches[:3] or missing_keywords[:3] or ["role requirements"]
    focus = ", ".join(focus_terms)
    rewrites: list[dict[str, str]] = []

    for bullet in bullets:
        if bullet.startswith("Add a role-relevant"):
            after = (
                "Add a concise achievement bullet that connects your experience to "
                f"{focus} and includes a measurable outcome if available."
            )
        else:
            after = f"{bullet} - framed for this role by emphasizing {focus}."
        rewrites.append(
            {
                "before": bullet,
                "after": after,
                "reason": "The rewrite makes the bullet easier to connect to the job post without inventing new facts.",
            }
        )
    return rewrites


def _weak_areas(missing_keywords: list[str], score: int) -> list[str]:
    areas: list[str] = []
    if missing_keywords:
        areas.append(
            "Several job-post keywords are not clearly visible in the CV: "
            + ", ".join(missing_keywords[:6])
            + "."
        )
    if score < 65:
        areas.append("The CV may need stronger evidence for the most important role requirements.")
    if not areas:
        areas.append("No major weak area was detected, but each claim should still be supported with evidence.")
    return areas


def create_demo_result(
    cv_text: str, job_post_text: str, preferences: dict[str, str]
) -> dict[str, Any]:
    cv_text = clean_text(cv_text)
    job_post_text = clean_text(job_post_text)
    analysis = analyze_locally(cv_text, job_post_text, preferences)

    language = preferences.get("output_language", "English")
    tone = preferences.get("tone", "professional")
    detail_level = preferences.get("detail_level", "balanced")
    role = preferences.get("target_role") or "the target role"
    pack = _language_pack(language)

    strong_matches = analysis["strong_matches"]
    missing_keywords = analysis["missing_keywords"]
    match_text = ", ".join(strong_matches[:4]) if strong_matches else "the role requirements"
    question_count = _detail_count(detail_level, 4, 6, 8)
    bullet_count = _detail_count(detail_level, 2, 3, 5)

    cover_letter = (
        f"{pack['cover_intro']}\n\n"
        f"I am applying for {role}. Based on the CV and job post provided, the strongest fit appears around "
        f"{match_text}. I would position the application with a {tone} tone, emphasizing concrete outcomes, "
        "relevant tools, and evidence already present in the CV.\n\n"
        "I would also address gaps honestly by showing learning ability, adjacent experience, and examples "
        "that transfer to the advertised responsibilities.\n\n"
        f"{pack['cover_close']}"
    )

    interview_questions = [
        f"Which example best shows your experience with {keyword}?"
        for keyword in (strong_matches[: question_count // 2] + missing_keywords[: question_count])
    ][:question_count]
    while len(interview_questions) < question_count:
        interview_questions.append(
            "What measurable result from your CV is most relevant to this role?"
        )

    checklist = [
        "Align the CV headline with the target role.",
        "Add the strongest matching keywords naturally where they are accurate.",
        "Turn responsibilities into measurable achievement bullets.",
        "Address missing keywords honestly in the cover letter or interview preparation.",
        "Check dates, company names, titles, and contact details before applying.",
    ]

    result = {
        "match_score": analysis["match_score"],
        "summary": pack["summary"],
        "strong_matches": strong_matches,
        "missing_keywords": missing_keywords,
        "weak_areas": _weak_areas(missing_keywords, analysis["match_score"]),
        "cv_bullet_rewrites": _create_bullet_rewrites(
            cv_text, strong_matches, missing_keywords, bullet_count
        ),
        "cover_letter": cover_letter,
        "linkedin_message": pack["linkedin"].format(matches=match_text),
        "interview_questions": interview_questions,
        "application_checklist": checklist,
        "warnings": [pack["warning"]],
    }
    return normalize_result(result)


def normalize_result(result: dict[str, Any]) -> dict[str, Any]:
    normalized = deepcopy(EMPTY_RESULT)
    if isinstance(result, dict):
        normalized.update({key: result.get(key, normalized[key]) for key in RESULT_FIELDS})

    try:
        normalized["match_score"] = int(normalized["match_score"])
    except (TypeError, ValueError):
        normalized["match_score"] = 0
    normalized["match_score"] = max(0, min(100, normalized["match_score"]))

    for key in [
        "strong_matches",
        "missing_keywords",
        "weak_areas",
        "interview_questions",
        "application_checklist",
        "warnings",
    ]:
        values = normalized.get(key)
        if not isinstance(values, list):
            values = []
        normalized[key] = [str(value) for value in values if str(value).strip()]

    rewrites = normalized.get("cv_bullet_rewrites")
    if not isinstance(rewrites, list):
        rewrites = []
    normalized["cv_bullet_rewrites"] = [
        {
            field: str(item.get(field, "")).strip()
            for field in BULLET_REWRITE_FIELDS
        }
        for item in rewrites
        if isinstance(item, dict)
    ]

    for key in ["summary", "cover_letter", "linkedin_message"]:
        normalized[key] = str(normalized.get(key, "")).strip()

    return normalized

