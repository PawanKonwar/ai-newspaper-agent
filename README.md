# AI Newspaper Agent

A browser-based application that automates the journalistic process through a three-stage LLM pipeline: **Research (DeepSeek)** → **Draft (OpenAI)** → **Edit (Google Gemini)**.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

## Features

- **Three-stage pipeline**: Research with DeepSeek, draft with OpenAI GPT-4, polish with Google Gemini
- **Web UI**: Topic input, target word count, collapsible stage results, regenerate per stage
- **Export**: Download article as `.txt` with metadata (headline, date, word count, LLMs used)
- **Edit before download**: In-browser text editor for the final article
- **Research transparency**: Facts displayed with source attributions when the model follows the requested format

## Project structure

```
ai_newspaper_agent/
├── app/                    # Backend application
│   ├── __init__.py
│   ├── config.py           # Loads from .env (no secrets in code)
│   ├── main.py             # FastAPI app and API routes
│   └── pipeline.py         # Three-stage LLM pipeline
├── frontend/
│   ├── static/             # CSS, JS
│   └── templates/          # HTML
├── tests/
│   ├── test_app.py
│   └── test_pipeline.py
├── .github/workflows/ci.yml # CI: pytest, flake8, isort (Python 3.12)
├── .env.example            # Template for environment variables
├── .flake8                 # flake8 config (max-line-length 88)
├── config_template.py     # Documents expected config (no secrets)
├── requirements.txt       # Pinned dependencies
├── requirements-dev.txt   # Dev/CI: flake8, isort
├── run.py                 # Entry: python run.py
├── start.py               # Entry with env check: python start.py
├── README.md
└── LICENSE                # MIT
```

## Prerequisites

- **Python 3.10+**
- **API keys** (all required for full pipeline):
  - [OpenAI](https://platform.openai.com/api-keys)
  - [DeepSeek](https://platform.deepseek.com/)
  - [Google Gemini](https://aistudio.google.com/apikey)

## Setup

### 1. Clone and enter the project

```bash
git clone <repository-url>
cd ai_newspaper_agent
```

### 2. Create a virtual environment (recommended)

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

**Never commit real API keys.** Use a `.env` file (ignored by git).

```bash
cp .env.example .env
```

Edit `.env` and set your keys:

```env
OPENAI_API_KEY=sk-...
DEEPSEEK_API_KEY=...
GOOGLE_API_KEY=...
```

Optional server settings:

```env
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=False
```

See `config_template.py` for the full list of supported variables.

### 5. Run the application

**Option A – with env check (recommended)**

```bash
python start.py
```

**Option B – direct**

```bash
python run.py
```

**Option C – uvicorn**

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Then open **http://localhost:8000** in your browser.

## Running tests

From the project root:

```bash
pip install pytest pytest-asyncio
python -m pytest tests/ -v
```

## CI / GitHub Actions

The repo includes a workflow at `.github/workflows/ci.yml` that runs on **push** and **pull_request** to `main`/`master`:

- **Python 3.12** – installs dependencies and runs tests/lint
- **pytest** – runs `tests/test_app.py` and `tests/test_pipeline.py` (tests work without API keys; stages may report "error" or "skipped" if keys are missing)
- **isort** – checks import order (`--check-only --diff --profile black`)
- **flake8** – lint (max line length 88; uses `.flake8`)

**Secrets (optional):** To run the pipeline against real APIs in CI, add these repository secrets in **Settings → Secrets and variables → Actions**:

- `OPENAI_API_KEY`
- `DEEPSEEK_API_KEY`
- `GOOGLE_API_KEY`

If secrets are not set, env vars are empty and tests still pass.

**Local lint:** Install dev deps and run:

```bash
pip install -r requirements-dev.txt
isort --check-only --diff --profile black app/ tests/ start.py run.py config_template.py
flake8 app/ tests/ start.py run.py config_template.py
```

## Environment variables reference

| Variable           | Required | Description                          |
|--------------------|----------|--------------------------------------|
| `OPENAI_API_KEY`   | Yes      | OpenAI API key (draft stage)         |
| `DEEPSEEK_API_KEY` | Yes      | DeepSeek API key (research stage)    |
| `GOOGLE_API_KEY`   | Yes      | Google Gemini API key (edit stage)   |
| `APP_HOST`         | No       | Bind address (default: 0.0.0.0)      |
| `APP_PORT`         | No       | Port (default: 8000)                 |
| `DEBUG`            | No       | Enable reload (default: False)       |

## API endpoints

- `GET /` – Web UI
- `GET /health` – Health check
- `POST /generate` – Run full pipeline (topic, max_length)
- `POST /regenerate-research` – Regenerate research only
- `POST /regenerate-draft` – Regenerate draft from existing research
- `POST /regenerate-edit` – Regenerate edit from existing draft

## Security

- **No API keys in code.** All secrets are read from the `.env` file.
- `.env` is listed in `.gitignore`; never commit it.
- Use `.env.example` and `config_template.py` as templates only; they contain no real keys.

## License

MIT License. See [LICENSE](LICENSE) for details.
