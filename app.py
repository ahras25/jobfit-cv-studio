"""Streamlit user interface for JobFit CV Studio."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys

import streamlit as st

from core.demo_data import load_sample_cv, load_sample_job_post
from core.openai_client import generate_application_kit, has_api_key
from core.report_exporter import export_markdown, export_text, filename_safe
from core.validators import clean_text, estimate_text_quality, validate_inputs


LANGUAGES = ["English", "Turkish", "Dutch"]
TONES = ["professional", "concise", "confident", "friendly"]
DETAIL_LEVELS = ["short", "balanced", "detailed"]


def apply_page_style() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(65, 179, 163, 0.18), transparent 32rem),
                linear-gradient(135deg, #0f1117 0%, #141821 50%, #10151b 100%);
            color: #f5f7fb;
        }
        .block-container {
            max-width: 1180px;
            padding-top: 2.4rem;
            padding-bottom: 4rem;
        }
        .hero {
            border: 1px solid rgba(255, 255, 255, 0.10);
            background: rgba(20, 24, 33, 0.88);
            border-radius: 18px;
            padding: 2rem;
            margin-bottom: 1.2rem;
            box-shadow: 0 20px 70px rgba(0, 0, 0, 0.28);
        }
        .hero h1 {
            font-size: clamp(2.2rem, 5vw, 4.3rem);
            line-height: 0.98;
            margin: 0.2rem 0 0.8rem;
            letter-spacing: 0;
        }
        .hero p {
            color: #b8c1d1;
            max-width: 760px;
            font-size: 1.05rem;
            line-height: 1.65;
        }
        .eyebrow {
            color: #41d6b2;
            font-weight: 800;
            text-transform: uppercase;
            font-size: 0.78rem;
            letter-spacing: 0;
        }
        .workflow-step {
            border: 1px solid rgba(255, 255, 255, 0.10);
            background: rgba(22, 27, 37, 0.78);
            border-radius: 14px;
            padding: 1.15rem 1.25rem;
            margin: 1.1rem 0 0.85rem;
        }
        .workflow-step h2 {
            margin: 0.2rem 0 0.2rem;
            font-size: 1.25rem;
        }
        .workflow-step p {
            margin: 0;
            color: #aeb8c8;
        }
        .result-panel {
            border: 1px solid rgba(255, 255, 255, 0.10);
            background: rgba(20, 24, 33, 0.74);
            border-radius: 14px;
            padding: 1rem;
            margin-bottom: 0.9rem;
        }
        .metric-strip {
            display: flex;
            gap: 0.65rem;
            flex-wrap: wrap;
            margin: 0.8rem 0 0.4rem;
        }
        .metric-pill {
            border: 1px solid rgba(65, 214, 178, 0.28);
            background: rgba(65, 214, 178, 0.10);
            border-radius: 999px;
            padding: 0.42rem 0.68rem;
            color: #d9fff6;
            font-size: 0.88rem;
            font-weight: 700;
        }
        .rewrite-card {
            border-left: 4px solid #82aaff;
            background: rgba(130, 170, 255, 0.10);
            border-radius: 10px;
            padding: 0.9rem 1rem;
            margin-bottom: 0.75rem;
        }
        .rewrite-card strong {
            color: #ffffff;
        }
        textarea {
            font-family: "Cascadia Code", "SFMono-Regular", Consolas, monospace;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_step(number: int, title: str, description: str) -> None:
    st.markdown(
        f"""
        <div class="workflow-step">
            <span class="eyebrow">Step {number}</span>
            <h2>{title}</h2>
            <p>{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_list(items: list[str]) -> None:
    if not items:
        st.write("None listed.")
        return
    for item in items:
        st.markdown(f"- {item}")


def render_bullets(rewrites: list[dict[str, str]]) -> None:
    if not rewrites:
        st.write("No rewrites returned.")
        return
    for item in rewrites:
        st.markdown(
            f"""
            <div class="rewrite-card">
                <p><strong>Before:</strong> {item.get("before", "")}</p>
                <p><strong>After:</strong> {item.get("after", "")}</p>
                <p><strong>Why:</strong> {item.get("reason", "")}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_quality_note(label: str, text: str) -> None:
    quality = estimate_text_quality(text)
    st.caption(
        f"{label}: {quality.word_count} words, {quality.char_count} characters, signal: {quality.signal}"
    )


def main() -> None:
    st.set_page_config(
        page_title="JobFit CV Studio",
        page_icon=":briefcase:",
        layout="wide",
    )
    apply_page_style()

    st.markdown(
        """
        <section class="hero">
            <span class="eyebrow">Application studio</span>
            <h1>JobFit CV Studio</h1>
            <p>
                Turn a CV and job post into a targeted application kit:
                match score, keyword gaps, rewritten CV bullets, cover letter,
                outreach message, interview questions, checklist, and downloadable report.
            </p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    api_ready = has_api_key()
    if api_ready:
        st.info("OPENAI_API_KEY is configured. API mode is available.")
    else:
        st.warning(
            "OPENAI_API_KEY is not configured. You can still use the app with deterministic Demo Mode."
        )
    st.info(
        "Privacy note: avoid pasting sensitive personal data into deployments you do not control."
    )

    use_sample_data = st.checkbox("Use sample data", value=not api_ready)

    sample_cv = load_sample_cv() if use_sample_data else ""
    sample_job = load_sample_job_post() if use_sample_data else ""

    render_step(1, "Add CV", "Paste your CV or resume text. Sample data can be used for a quick product tour.")
    cv_text = st.text_area(
        "CV or resume text",
        value=sample_cv,
        height=280,
        placeholder="Paste your CV text here...",
    )
    render_quality_note("CV quality", cv_text)

    render_step(2, "Add job post", "Paste the job description so the app can compare requirements against your CV.")
    job_post_text = st.text_area(
        "Job description",
        value=sample_job,
        height=280,
        placeholder="Paste the job post here...",
    )
    render_quality_note("Job post quality", job_post_text)

    render_step(3, "Choose preferences", "Set the target role, output language, tone, and detail level.")
    col_role, col_language, col_tone, col_detail = st.columns([1.35, 1, 1, 1])
    with col_role:
        target_role = st.text_input(
            "Target role",
            value="Customer Success Operations Specialist" if use_sample_data else "",
            placeholder="Optional, for example Product Analyst",
        )
    with col_language:
        output_language = st.selectbox("Output language", LANGUAGES, index=0)
    with col_tone:
        tone = st.selectbox("Preferred tone", TONES, index=0)
    with col_detail:
        detail_level = st.selectbox("Detail level", DETAIL_LEVELS, index=1)

    preferences = {
        "target_role": target_role.strip(),
        "output_language": output_language,
        "tone": tone,
        "detail_level": detail_level,
    }

    render_step(4, "Generate application kit", "Run the tailored analysis and writing workflow.")
    generate_clicked = st.button("Generate application kit", type="primary", use_container_width=True)

    if generate_clicked:
        errors = validate_inputs(cv_text, job_post_text, use_sample_data)
        if errors:
            for error in errors:
                st.error(error)
        else:
            cleaned_cv = clean_text(cv_text)
            cleaned_job = clean_text(job_post_text)
            with st.spinner("Preparing your tailored application kit..."):
                generation = generate_application_kit(
                    cleaned_cv,
                    cleaned_job,
                    preferences,
                    force_demo=use_sample_data,
                )
            st.session_state["jobfit_generation"] = generation
            st.session_state["jobfit_preferences"] = preferences

    generation = st.session_state.get("jobfit_generation")
    active_preferences = st.session_state.get("jobfit_preferences", preferences)

    render_step(5, "Review and download", "Inspect each output section and export a report for your application notes.")
    if not generation:
        st.info("Generate an application kit to see the review sections here.")
        return

    result = generation.result
    if generation.source == "api":
        st.success(generation.message)
    else:
        st.warning(generation.message)

    score = int(result.get("match_score", 0))
    st.progress(score, text=f"CV-job match score: {score}/100")
    st.markdown(f"**Summary:** {result.get('summary', '')}")

    st.markdown(
        f"""
        <div class="metric-strip">
            <span class="metric-pill">{len(result.get("strong_matches", []))} strong matches</span>
            <span class="metric-pill">{len(result.get("missing_keywords", []))} missing keywords</span>
            <span class="metric-pill">{len(result.get("interview_questions", []))} interview questions</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tabs = st.tabs(
        [
            "Match",
            "CV bullets",
            "Cover letter",
            "LinkedIn",
            "Interview",
            "Checklist",
            "Report",
        ]
    )

    with tabs[0]:
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.markdown("### Strong matches")
            render_list(result.get("strong_matches", []))
        with col_b:
            st.markdown("### Missing keywords")
            render_list(result.get("missing_keywords", []))
        with col_c:
            st.markdown("### Weak areas")
            render_list(result.get("weak_areas", []))
        if result.get("warnings"):
            st.warning("\n".join(result["warnings"]))

    with tabs[1]:
        st.markdown("### Rewritten CV bullet points")
        render_bullets(result.get("cv_bullet_rewrites", []))

    with tabs[2]:
        st.markdown("### Tailored cover letter")
        st.text_area("Cover letter output", value=result.get("cover_letter", ""), height=360)

    with tabs[3]:
        st.markdown("### LinkedIn outreach message")
        st.text_area("LinkedIn message output", value=result.get("linkedin_message", ""), height=160)

    with tabs[4]:
        st.markdown("### Interview preparation questions")
        render_list(result.get("interview_questions", []))

    with tabs[5]:
        st.markdown("### Application checklist")
        render_list(result.get("application_checklist", []))

    with tabs[6]:
        st.markdown("### Downloadable report")
        markdown_report = export_markdown(result, active_preferences)
        text_report = export_text(result, active_preferences)
        base_name = filename_safe(active_preferences.get("target_role") or "jobfit-report")

        col_md, col_txt = st.columns(2)
        with col_md:
            st.download_button(
                "Download Markdown report",
                data=markdown_report,
                file_name=f"{base_name}.md",
                mime="text/markdown",
                use_container_width=True,
            )
        with col_txt:
            st.download_button(
                "Download text report",
                data=text_report,
                file_name=f"{base_name}.txt",
                mime="text/plain",
                use_container_width=True,
            )
        with st.expander("Preview report"):
            st.markdown(markdown_report)


def _running_inside_streamlit() -> bool:
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx

        return get_script_run_ctx() is not None
    except Exception:
        return False


def _launch_streamlit() -> int:
    script_path = Path(__file__).resolve()
    print("Starting JobFit CV Studio with Streamlit...")
    print("If the browser does not open automatically, visit http://localhost:8501")
    return subprocess.call([sys.executable, "-m", "streamlit", "run", str(script_path)])


if __name__ == "__main__":
    if _running_inside_streamlit():
        main()
    else:
        raise SystemExit(_launch_streamlit())
