# Repository Guide

## What this project is

- FastAPI sentiment inference service backed by a Hugging Face tokenizer and a fine-tuned PhoBERT classifier.
- Main entrypoint: `main.py`
- Python dependencies: `requirements.txt`

## Local run

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Docker build

```bash
docker build -t eventboxsentiment:latest .
```

## Local compose run

```bash
docker compose up --build
```

## Release flow

- Use `./release.sh` from the repo root.
- The script reads Docker Hub credentials from `.env` when present.
- Required variables:
  - `DOCKERHUB_USERNAME`
  - `DOCKERHUB_TOKEN` or `DOCKERHUB_PASSWORD`
- Optional variables:
  - `DOCKERHUB_REPOSITORY`
  - `IMAGE_TAG`
  - `DOCKERFILE`
  - `CONTEXT`

## Working rules

- Keep changes minimal and file-focused.
- Do not commit secrets or local environment files.
- Prefer reproducible setup files over ad hoc shell steps.
- If you add new runtime config, document it in `.env.example`.
