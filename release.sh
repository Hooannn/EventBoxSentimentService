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
docker buildx build --platform=linux/amd64 -f "$DOCKERFILE_PATH" -t "$FULL_IMAGE" "$CONTEXT_PATH"

echo "Pushing ${FULL_IMAGE}"
docker push "$FULL_IMAGE"

echo "Released ${FULL_IMAGE}"
