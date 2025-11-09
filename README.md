# LiteLLM Azure Deployment Project

## Overview

This project deploys LiteLLM (LLM Gateway) in Azure, automating with Bicep, scaling to Kubernetes via Helm and CI/CD. Includes a community PR for PayPal support. Focus on basic reproducible setups for beginner DevOps.

## Expected Final Outcome

- Automated multi-environment (dev/stage/prod) LiteLLM deployment in AKS with Helm and GitHub Actions CI/CD.
- Merged PR to LiteLLM repo adding PayPal for virtual key billing.
- Basic portfolio: Demos, Bicep templates, PR.

## Plan Stages

### Stage 1: Initial Deployment
- **Objectives**: Run LiteLLM in Azure ACI with Docker.
- **Tasks**:
  - Fork/deploy repo to ACI using Docker images.
  - Configure ports/UI/API; troubleshoot with CLI/Copilot.
  - Test basic queries.
- **Deliverables**: Working ACI; Git repo notes.
- **Success**: API/UI access; errors resolved.

### Stage 2: Bicep Automation
- **Objectives**: Automate ACI/resource group with IaC.
- **Tasks**:
  - Export resources to Bicep.
  - Monorepo with Bicep/scripts/docs.
  - Params for env configs; cross-account validate.
- **Deliverables**: Reproducible Bicep deploys; shared repo.
- **Success**: One-click deploys match manual.

### Stage 3: CI/CD and Kubernetes
- **Objectives**: Migrate to AKS with pipelines.
- **Tasks**:
  - Bicep for AKS clusters (dev/stage/prod).
  - Helm charts for LiteLLM/Docker builds.
  - GitHub Actions: Build/test/deploy by branch.
  - Basic observability/rate limits.
- **Deliverables**: Helm AKS setup; pipelines.
- **Success**: Automated env deploys.

### Stage 4: Prepare PayPal PR
- **Objectives**: Develop PayPal integration for LiteLLM proxy.
- **Tasks**:
  - Research keys/budgets architecture.
  - Implement PayPal invoicing/webhooks.
  - Add tests and internal docs/examples.
- **Deliverables**: Feature branch ready for submission.
- **Success**: Code passes local tests/linting.

### Stage 5: Submit PR and Portfolio
- **Objectives**: Submit, merge PR; build portfolio.
- **Tasks**:
  - Raise issue, submit PR; iterate on reviews.
  - Achieve merge; create demos/blog.
  - Update README: Diagrams, guides; add to resume.
- **Deliverables**: Merged PR; portfolio artifacts.
- **Success**: PR accepted; clear deploy guide.

## Tools
Azure CLI/Portal, GitHub, Bicep, Helm, Python, AI
