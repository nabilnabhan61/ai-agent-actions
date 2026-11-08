# AI Inventory Agent - Assignment 6

Django inventory assistant with Gemini tool calls, SQLite, and GitHub Actions CI/CD.

Repository: https://github.com/nabilnabhan61/ai-agent-actions

**Start with [SETUP.md](SETUP.md)** for the remaining GitHub and Windows steps.

## Pipeline

Push to `main` -> Django checks and tests -> build and smoke-test Linux Docker image -> publish to GHCR -> Windows self-hosted runner pulls the exact commit image -> replace local container -> health check.

Pull requests run checks, tests, and the container smoke test only. They do not publish or run on the local runner. Manual runs on `main` also deploy.

- Workflow: `.github/workflows/ci.yml`
- Runner label: `ai-agent-deploy` (Windows x64)
- Image: `ghcr.io/nabilnabhan61/ai-agent-actions:latest`, plus immutable commit SHA tags
- Container: `ai-agent-actions-app`
- Local app: http://localhost:8000
- Persistent database volume: `ai-agent-actions-data`
- Runtime secrets: `%USERPROFILE%\.ai-agent-actions.env`, outside the repository

The workflow follows the enclosed tutorial, adapting Python to 3.13 for this app and adding tests, automatic migrations, persistent storage, and health checks. The Django development server is used for the local lab demonstration, as in the tutorial.

## Development

With Python 3.13 installed:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
# Edit .env with your own Gemini key.
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py test
.\.venv\Scripts\python.exe manage.py runserver
```

CI tests mock Gemini and need no API key. Real chat requires a valid key and access to the configured model; the original app's model is preserved and can be overridden with `GEMINI_MODEL`.

## Validation performed locally

- Django system check: passed.
- Migration drift check: passed.
- Eight tests: passed (inventory, chat session, reset, missing key, mocked agent tool call).
- Local tests used Python 3.12; CI and Docker use Python 3.13.
- Docker build, GHCR publishing, self-hosted deployment, and live Gemini calls remain to be verified after setup. Docker's engine was unavailable during preparation.

## Attribution

Based on the existing AI Inventory Agent supplied for EECE430. AI assistance added the CI/CD workflow, deployment script, automated checks, environment-based configuration, and this documentation.
