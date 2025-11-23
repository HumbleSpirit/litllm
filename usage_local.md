# LiteLLM Gateway — Local Development Guide

![Docker](https://img.shields.io/badge/Docker-ready-blue?logo=docker)
![Local Development](https://img.shields.io/badge/Local-Development-green)
![LiteLLM](https://img.shields.io/badge/LiteLLM-Gateway-orange)

## 🚀 Base Usage for Local Development

### 1. Clone the repository
```bash
git clone <repo_url>
cd <project_folder>
cp .env.example .env
docker build -t litellm-gateway:latest -f dockerfile .

docker run -d \
  --name litellm-gateway \
  --env-file .env \
  -p 8080:8080 \
  litellm-gateway:latest
```
