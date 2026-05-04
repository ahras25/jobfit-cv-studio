# JobFit CV Studio

JobFit CV Studio is a Streamlit web app that helps job applicants tailor a CV, cover letter, LinkedIn outreach message, and interview preparation plan to a specific job post.

The user pastes a CV or resume, a job description, and a few preferences. The app returns a match score, strong matches, missing keywords, weak areas, rewritten CV bullet points, a tailored cover letter, a short LinkedIn message, interview questions, an application checklist, and downloadable reports.

## Who It Is For

- Job applicants who want a structured application review
- Career changers comparing their experience to a job post
- Coaches helping applicants prepare role-specific materials
- Developers looking for a practical Streamlit product example

## Features

- Step-by-step application studio workflow
- CV-job match score
- Keyword extraction and missing keyword detection
- Strong match and weak area analysis
- CV bullet rewrite suggestions
- Tailored cover letter
- LinkedIn outreach message
- Interview preparation questions
- Application checklist
- Downloadable Markdown and text reports
- Demo Mode with deterministic local output
- OpenAI API mode with structured JSON output

## Local Setup

Create and activate a virtual environment, then install requirements:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## How To Run

```bash
streamlit run app.py
```

On Windows, you can also double-click `run_app.bat`.

The app also supports:

```bash
python app.py
```

When started this way, it launches Streamlit for you.

## How To Test

```bash
python -m unittest discover tests
```

## OpenAI API Configuration

The app checks for `OPENAI_API_KEY` in this order:

1. Streamlit secrets
2. Environment variable

For local Streamlit secrets, copy:

```text
.streamlit/secrets.example.toml
```

to:

```text
.streamlit/secrets.toml
```

Then set your own key in the private `secrets.toml` file. Do not commit real API keys.

You can also use an environment variable:

```powershell
$env:OPENAI_API_KEY = Read-Host "OPENAI_API_KEY"
```

On macOS or Linux:

```bash
read -s OPENAI_API_KEY
export OPENAI_API_KEY
```

## Demo Mode

If no API key is configured, the app still works. Demo Mode uses deterministic local analysis from the Python code. The checkbox labeled `Use sample data` loads the included sample CV and sample job post.

Demo Mode does not call the OpenAI API.

## Deploy To Streamlit Community Cloud

1. Push this repository to GitHub.
2. Open Streamlit Community Cloud.
3. Create a new app.
4. Select the repository and branch.
5. Set the entry file to `app.py`.
6. Add `OPENAI_API_KEY` in Streamlit secrets if you want API mode.
7. Deploy.

## Privacy Notes

CVs and job descriptions may contain personal information. Users should avoid pasting sensitive personal data into deployments they do not control. API mode may send the provided CV and job text to OpenAI. Demo Mode runs locally and does not call the API.

Never commit API keys to GitHub. Public deployments should use Streamlit secrets.

## Project Structure

```text
jobfit-cv-studio/
  README.md
  app.py
  requirements.txt
  .gitignore
  .streamlit/
    config.toml
    secrets.example.toml
  core/
    __init__.py
    analyzer.py
    openai_client.py
    prompt_builder.py
    schemas.py
    demo_data.py
    report_exporter.py
    validators.py
  tests/
    test_analyzer.py
    test_prompt_builder.py
    test_report_exporter.py
    test_validators.py
  docs/
    usage.md
    deployment.md
    privacy_notes.md
  assets/
    sample_cv.txt
    sample_job_post.txt
```
