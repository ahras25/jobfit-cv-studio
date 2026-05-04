# Deployment

JobFit CV Studio is deployable to Streamlit Community Cloud.

## Steps

1. Push the repository to GitHub.
2. Go to Streamlit Community Cloud.
3. Create a new app.
4. Select the repository and branch.
5. Set the entry file to `app.py`.
6. Add `OPENAI_API_KEY` in secrets if using API mode.
7. Deploy.

## Secrets

Use Streamlit Community Cloud secrets for API mode. Add an `OPENAI_API_KEY`
entry in the Streamlit secrets editor and store the real value there.

Do not commit `.streamlit/secrets.toml` to GitHub. The `.gitignore` file excludes it.

## Demo Mode

The app can be deployed without an API key. In that case it still runs with deterministic Demo Mode.
