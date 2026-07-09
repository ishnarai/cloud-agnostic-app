# cloud-agnostic-app

The **application repository** for the Orion cloud-agnostic PoC. This repository owns the FastAPI application, its Dockerfile, and its CI pipeline — and **nothing else**. It has no knowledge of Kubernetes, Terraform, or any specific cloud provider.

> Deployment infrastructure (Terraform, Kubernetes manifests, deployment scripts) lives in the companion repository: [`cloud-agnostic-deploy`](../cloud-agnostic-deploy).

## Why this repo contains no deployment code

Separating application code from deployment/infrastructure code is a standard enterprise pattern for a few concrete reasons:

- **Different release cadence**: application code might change many times a day; infrastructure changes far less often and needs more careful review.
- **Different audiences/permissions**: application developers don't necessarily need (or want) write access to production Terraform state or cloud credentials, and vice versa.
- **Blast radius isolation**: a mistake in a Kubernetes manifest can't be introduced by an app-focused pull request, because that file doesn't exist in this repo.
- **Independent versioning**: the deployment repo can roll back to a previous image tag without touching application source history at all.

## Repository structure

```
cloud-agnostic-app/
├── .github/workflows/
│   ├── test.yml      # Reusable: runs pytest
│   ├── build.yml      # Reusable: builds + pushes the Docker image
│   └── ci.yml          # Orchestrator: calls test.yml -> build.yml -> notifies deploy repo
├── app/                 # FastAPI application source
├── tests/                # Automated tests
├── Dockerfile            # Moved here from docker/Dockerfile in the original PoC
├── requirements.txt
├── .env.example
└── README.md
```

## What the CI pipeline does (and does not do)

`ci.yml` runs on every push/PR to `main`:

1. Calls `test.yml` — runs the full pytest suite.
2. Calls `build.yml` — builds the Docker image and pushes it to GHCR, tagged with the commit SHA.
3. On pushes to `main` only, dispatches an `app-image-built` event to the `cloud-agnostic-deploy` repository, carrying the new image tag.

**This repository never runs `kubectl`, `terraform`, or connects to any cloud provider.** Its only output is a tested, pushed container image and a notification that it exists.

## Running locally

```bash
pip install -r requirements.txt
CLOUD_PROVIDER=local uvicorn app.main:app --reload
```

## Running with Docker

```bash
docker build -t cloud-agnostic-app:latest .
docker run -d -p 8000:8000 -e CLOUD_PROVIDER=aws cloud-agnostic-app:latest
```

## Testing

```bash
python -m pytest tests/ -v
```

## Required GitHub Secrets (this repository)

| Secret | Purpose |
|---|---|
| `GITHUB_TOKEN` | Auto-provided by GitHub; used to push images to GHCR |
| `DEPLOY_REPO_PAT` | A Personal Access Token (repo scope) allowing this repo to dispatch events to `cloud-agnostic-deploy` |
