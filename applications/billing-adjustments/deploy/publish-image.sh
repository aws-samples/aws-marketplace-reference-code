#!/bin/bash
# Build the app container image and push it to a PRIVATE Amazon ECR repository in
# the current AWS account. Run this from the repo root (the directory that
# contains the 'webapp' and 'deploy' folders).
#
# Usage:
#   ./deploy/publish-image.sh [REPO_NAME] [REGION] [TAG]
#
# Defaults: REPO_NAME=billing-adjustments  REGION=us-east-1  TAG=latest
#
# Container engine: auto-detected (Docker if its daemon is reachable, else
# Finch). Force one with CONTAINER_ENGINE=docker or CONTAINER_ENGINE=finch.
#
# After it finishes, it prints the image URI to pass as the ImageUri parameter
# (with ImageRepositoryType=ECR) when you deploy deploy/cloudformation.yaml.

set -euo pipefail

REPO_NAME="${1:-billing-adjustments}"
REGION="${2:-us-east-1}"
TAG="${3:-latest}"

ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"
REGISTRY="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"
IMAGE_URI="${REGISTRY}/${REPO_NAME}:${TAG}"

echo "Account:  ${ACCOUNT_ID}"
echo "Region:   ${REGION}"
echo "Image:    ${IMAGE_URI}"
echo ""

# 1. Ensure the ECR repository exists
aws ecr describe-repositories --repository-names "${REPO_NAME}" --region "${REGION}" >/dev/null 2>&1 \
  || aws ecr create-repository --repository-name "${REPO_NAME}" --region "${REGION}" >/dev/null

# 2. Pick a container engine. Prefer Docker when its daemon is reachable,
#    otherwise fall back to Finch. Override explicitly with
#    CONTAINER_ENGINE=docker|finch if you have both installed.
ENGINE="${CONTAINER_ENGINE:-}"
if [ -z "${ENGINE}" ]; then
  if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
    ENGINE="docker"
  elif command -v finch >/dev/null 2>&1; then
    ENGINE="finch"
  elif command -v docker >/dev/null 2>&1; then
    ENGINE="docker"
  else
    echo "ERROR: no container engine found. Install Docker or Finch (and start it)." >&2
    exit 1
  fi
fi
echo "Engine:   ${ENGINE}"
echo ""

# Make sure the engine can reach its daemon before we try to build.
if ! "${ENGINE}" info >/dev/null 2>&1; then
  echo "ERROR: '${ENGINE}' is installed but its daemon isn't reachable." >&2
  if [ "${ENGINE}" = "finch" ]; then
    echo "       Start it with: finch vm start   (or 'finch vm init' the first time)." >&2
  else
    echo "       Start Docker Desktop (or the docker daemon) and retry." >&2
  fi
  exit 1
fi

# 3. Authenticate the engine to ECR
aws ecr get-login-password --region "${REGION}" \
  | "${ENGINE}" login --username AWS --password-stdin "${REGISTRY}"

# 4. Build for the App Runner platform (linux/amd64) and push.
#    Docker with buildx can build+push in one step (and keep a simple manifest
#    via --provenance=false). Finch (or Docker without buildx) builds then pushes.
if [ "${ENGINE}" = "docker" ] && docker buildx version >/dev/null 2>&1; then
  docker buildx build \
    --platform linux/amd64 \
    --provenance=false \
    -f deploy/Dockerfile \
    -t "${IMAGE_URI}" \
    --push \
    .
else
  "${ENGINE}" build \
    --platform=linux/amd64 \
    -f deploy/Dockerfile \
    -t "${IMAGE_URI}" \
    .
  "${ENGINE}" push "${IMAGE_URI}"
fi

echo ""
echo "Done. Deploy with:"
echo "  ImageUri=${IMAGE_URI}"
echo "  ImageRepositoryType=ECR"
