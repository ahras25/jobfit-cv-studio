# Privacy Notes

CVs, resumes, and job applications can contain sensitive personal information.

## User Guidance

Users should not paste sensitive personal data into deployments they do not control. This includes identity numbers, home addresses, private phone numbers, salary details, or confidential employer information.

## API Mode

API mode may send user-provided CV text, job post text, and preferences to OpenAI so the app can create structured output.

## Demo Mode

Demo Mode does not call the OpenAI API. It uses deterministic local analysis from the Python code and can run without an API key.

## API Keys

API keys must not be committed to GitHub. Local development should use a private `.streamlit/secrets.toml` file or an environment variable. Public deployments should use Streamlit secrets.

