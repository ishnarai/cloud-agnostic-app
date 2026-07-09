# =============================================================================
# Dockerfile for the Cloud-Agnostic PoC FastAPI application
# =============================================================================
#
# This file now lives at the REPOSITORY ROOT (moved here as part of the
# enterprise-style two-repo split - previously at docker/Dockerfile in the
# single-repo layout). Build from the repo root:
#   docker build -t cloud-agnostic-app:latest .
#
# All deployment concerns (Kubernetes manifests, Terraform) have moved to the
# separate cloud-agnostic-deploy repository - this repo only knows how to
# build and test the application itself.

# -----------------------------------------------------------------------------
# Base image
# -----------------------------------------------------------------------------
# "python:3.12-slim" is a minimal Debian-based image with Python pre-installed.
# We choose "slim" over the full "python:3.12" image because:
#   1. Smaller image size -> faster to push/pull across any cloud registry
#      (ECR, ACR, GAR) and faster container startup.
#   2. Fewer pre-installed OS packages -> smaller attack surface, which
#      security-conscious teams (and your mentor) will specifically look for.
# We pin the EXACT version (3.12-slim, not just "python:latest") so that a
# build today and a build six months from now produce the same environment -
# the same discipline as pinning requirements.txt versions.
FROM python:3.12-slim

# -----------------------------------------------------------------------------
# Metadata
# -----------------------------------------------------------------------------
LABEL maintainer="Ishna"
LABEL description="Cloud-agnostic FastAPI PoC for internship - AWS/Azure/GCP"

# -----------------------------------------------------------------------------
# Working directory
# -----------------------------------------------------------------------------
# Sets the default directory for all subsequent instructions (COPY, RUN, CMD).
# Using /app (rather than leaving it at the image default of /) keeps our
# application files cleanly separated from system directories - standard
# convention across nearly all production Dockerfiles.
WORKDIR /app

# -----------------------------------------------------------------------------
# Install dependencies FIRST, before copying application code
# -----------------------------------------------------------------------------
# This ordering is deliberate and exploits Docker's layer caching:
# requirements.txt changes far less often than app/ source code. By copying
# ONLY requirements.txt first and installing it, Docker caches this layer.
# On future builds, if you only changed a .py file, Docker skips re-running
# "pip install" entirely and reuses the cached layer - massively speeding up
# your build/test/iterate loop.
COPY requirements.txt .

# --no-cache-dir keeps pip from storing its own download cache inside the
# image, which would otherwise bloat the final image size for no benefit
# (we're not going to reinstall inside a running container).
RUN pip install --no-cache-dir -r requirements.txt

# -----------------------------------------------------------------------------
# Now copy the actual application source code
# -----------------------------------------------------------------------------
# This happens AFTER dependency installation for the caching reason above.
# The .dockerignore file (Section 2) ensures tests/, terraform/, k8s/, and
# other non-runtime files never even reach this COPY instruction.
COPY app/ ./app/

# -----------------------------------------------------------------------------
# Security: run as a non-root user
# -----------------------------------------------------------------------------
# By default, Docker containers run as the "root" user, which is unnecessary
# risk: if an attacker ever exploited a vulnerability in your app, running as
# root inside the container gives them more capability than they need.
# Creating and switching to an unprivileged user is a standard production
# hardening step that both AWS, Azure, and GCP security scanners check for.
RUN useradd --create-home appuser
USER appuser

# -----------------------------------------------------------------------------
# Document the port the app listens on
# -----------------------------------------------------------------------------
# EXPOSE is documentation, not enforcement - it does not actually publish the
# port. It tells humans (and tools like `docker inspect`) which port the
# containerized process expects to be reachable on. We still need `-p` when
# running the container, and Kubernetes will read this convention too.
EXPOSE 8000

# -----------------------------------------------------------------------------
# Container health check
# -----------------------------------------------------------------------------
# Docker (and later, Kubernetes) can periodically probe this endpoint to
# determine if the container is actually healthy, not just "running".
# This directly reuses the /health endpoint we built in Section 3.
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# -----------------------------------------------------------------------------
# Start command
# -----------------------------------------------------------------------------
# CMD (rather than RUN) defines the process that runs when the CONTAINER
# starts, not when the IMAGE builds. We use the "exec form" (JSON array
# syntax) rather than the "shell form" (a plain string) because exec form
# runs uvicorn as PID 1 directly, allowing it to correctly receive and handle
# OS signals like SIGTERM - important for graceful shutdowns when Kubernetes
# terminates a pod.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
