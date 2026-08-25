# FrameScout 🎬

> **Do roteiro à mídia certa — com procedência, contexto e confiança.**

O **FrameScout** transforma roteiros de vídeo em planos visuais de cenas e ajuda criadores a encontrar imagens, vídeos, B-rolls e referências visuais com classificação rigorosa de direitos (`RightsStatus`) e fidelidade factual.

---

## 🏗️ Arquitetura & Stack

- **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind CSS, Lucide Icons.
- **Backend**: Python, FastAPI, SQLAlchemy 2.0 (Async), Pydantic v2.
- **Banco de Dados**: PostgreSQL 16.
- **Worker**: Serviço dedicado para tarefas assíncronas (scaffold no Sprint 0).
- **Testes & Qualidade**: Pytest, Vitest, Playwright, Ruff, Mypy, ESLint.
- **Infraestrutura Local**: Docker Compose com healthchecks determinísticos.
- **CI**: GitHub Actions.

---

## 🚀 Como Executar Localmente

### Pré-requisitos
- Docker & Docker Compose (versão 2.20+)
- Python 3.11+ e Node.js 20+ (para desenvolvimento local fora de containers)

### 1. Iniciar com Docker Compose (Recomendado)

```bash
# 1. Clone o repositório e configure as variáveis de ambiente
cp .env.example .env

# 2. Suba todos os serviços
make up
# ou: docker compose up -d --build

# 3. Verifique o status de saúde
make health
```

Serviços disponíveis:
- **Frontend**: [http://localhost:3000](http://localhost:3000)
- **API Backend**: [http://localhost:8000](http://localhost:8000)
- **Documentação Interativa da API**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Healthcheck Detalhado**: [http://localhost:8000/health](http://localhost:8000/health)

---

## 🧪 Executando Testes e Qualidade

```bash
# Executar todos os testes
make test

# Testes backend (Pytest)
make test-api

# Testes frontend (Vitest)
make test-web

# Validação de tipos (Mypy + TypeScript)
make typecheck

# Linting (Ruff + ESLint)
make lint
```

---

## 🗺️ Roadmap de Sprints

Consulte [ROADMAP.md](ROADMAP.md) para detalhes completos da evolução do produto:

- **Sprint 0**: Fundação e Arquitetura Monorepo *(Concluído)*
- **Sprint 1**: Projects & Scripts
- **Sprint 2**: Scene Engine
- **Sprint 3**: Query Generator
- **Sprint 4**: Provider Architecture
- **Sprint 5**: Pexels Integration
- **Sprint 6**: Wikimedia Commons Integration
- **Sprint 7**: Rights Engine
- **Sprint 8**: Media Browser
- **Sprint 9**: Asset Selection
- **Sprint 10**: Project Export & Manifest Generator
