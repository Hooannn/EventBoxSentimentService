# Docker and Release Setup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add repository guidance, a production-ready Docker image, and a release script that builds and pushes to Docker Hub using credentials loaded from `.env`.

**Architecture:** Keep the app code unchanged and add deployment support as small, focused files at the repo root. Docker should build from the existing FastAPI entrypoint in `main.py`, and the release script should only orchestrate Docker login, build, and push.

**Tech Stack:** Bash, Docker, Python 3.11, FastAPI.

---

### Task 1: Repository guidance and ignore files

**Files:**
- Create: `AGENTS.md`
- Create: `.gitignore`
- Create: `.dockerignore`
- Create: `.env.example`

- [ ] **Step 1: Add the repo instructions and environment contract**

```markdown
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
```

- [ ] **Step 2: Ignore local and build artifacts**

```gitignore
.env
.venv/
venv/
env/
__pycache__/
*.py[cod]
.pytest_cache/
.mypy_cache/
.ruff_cache/
.coverage
coverage.xml
htmlcov/
build/
dist/
*.egg-info/
.DS_Store
*.log
```

- [ ] **Step 3: Add Docker build exclusions**

```dockerignore
.git
.gitignore
.env
.venv
venv
env
__pycache__
.pytest_cache
.mypy_cache
.ruff_cache
build
dist
*.pyc
*.pyo
*.pyd
.DS_Store
docs
```

- [ ] **Step 4: Document the Docker Hub variables**

```dotenv
DOCKERHUB_USERNAME=your-dockerhub-username
DOCKERHUB_TOKEN=your-dockerhub-token
DOCKERHUB_REPOSITORY=eventboxsentiment
IMAGE_TAG=latest
DOCKERFILE=Dockerfile
CONTEXT=.
```

### Task 2: Docker image and release script

**Files:**
- Create: `Dockerfile`
- Create: `release.sh`

- [ ] **Step 1: Build a container image that runs the FastAPI app**

```dockerfile
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       gcc \
       git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 2: Add a release script that loads `.env`, logs in, builds, and pushes**

```bash
#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ -f "$ROOT_DIR/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.env"
  set +a
fi

if [[ -z "${DOCKERHUB_USERNAME:-}" ]]; then
  echo "DOCKERHUB_USERNAME is required" >&2
  exit 1
fi

DOCKERHUB_REPOSITORY="${DOCKERHUB_REPOSITORY:-eventboxsentiment}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
DOCKERFILE_PATH="${DOCKERFILE:-Dockerfile}"
CONTEXT_PATH="${CONTEXT:-.}"

if [[ -z "${DOCKERHUB_TOKEN:-}" && -z "${DOCKERHUB_PASSWORD:-}" ]]; then
  echo "Set DOCKERHUB_TOKEN or DOCKERHUB_PASSWORD in .env" >&2
  exit 1
fi

DOCKER_PASSWORD="${DOCKERHUB_TOKEN:-${DOCKERHUB_PASSWORD:-}}"
IMAGE_NAME="${DOCKERHUB_USERNAME}/${DOCKERHUB_REPOSITORY}"
FULL_IMAGE="${IMAGE_NAME}:${IMAGE_TAG}"

echo "Logging in to Docker Hub as ${DOCKERHUB_USERNAME}"
printf '%s' "$DOCKER_PASSWORD" | docker login --username "$DOCKERHUB_USERNAME" --password-stdin

cd "$ROOT_DIR"

echo "Building ${FULL_IMAGE}"
docker build -f "$DOCKERFILE_PATH" -t "$FULL_IMAGE" "$CONTEXT_PATH"

echo "Pushing ${FULL_IMAGE}"
docker push "$FULL_IMAGE"
```

- [ ] **Step 3: Make the release script executable**

```bash
chmod +x release.sh
```

### Task 3: Verify the setup

**Files:**
- Inspect: `AGENTS.md`
- Inspect: `.gitignore`
- Inspect: `.dockerignore`
- Inspect: `.env.example`
- Inspect: `Dockerfile`
- Inspect: `release.sh`

- [ ] **Step 1: Confirm the files exist and contain the expected defaults**

```bash
sed -n '1,220p' AGENTS.md
sed -n '1,220p' .gitignore
sed -n '1,220p' .dockerignore
sed -n '1,220p' .env.example
sed -n '1,220p' Dockerfile
sed -n '1,220p' release.sh
```

- [ ] **Step 2: Check the shell script syntax**

```bash
bash -n release.sh
```

### Coverage Check

- Repo guidance: covered by `AGENTS.md`.
- Docker build: covered by `Dockerfile`.
- Release and Docker Hub push: covered by `release.sh`.
- Secret hygiene and build hygiene: covered by `.gitignore`, `.dockerignore`, and `.env.example`.

### Placeholder Scan

- No placeholder text remains in the plan.

### Type Consistency

- Variable names are consistent across the plan and the files: `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`, `DOCKERHUB_PASSWORD`, `DOCKERHUB_REPOSITORY`, `IMAGE_TAG`, `DOCKERFILE`, and `CONTEXT`.
