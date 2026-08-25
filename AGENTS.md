# FrameScout — Diretrizes para Agentes de IA & Desenvolvedores

Este repositório segue regras estritas de arquitetura, qualidade e progressão de sprints.

---

## 1. Princípios Inegociáveis

1. **Procedência e Direitos em Primeiro Lugar**: A possibilidade técnica de baixar ou exibir um arquivo nunca implica direito de reutilização. Toda mídia deve ter seu `RightsStatus` registrado e validado.
2. **Código Fortemente Tipado**: Todo modelo de backend utiliza Pydantic v2 / SQLAlchemy 2.0 com Mapped columns; todo código frontend utiliza TypeScript estrito.
3. **Desacoplamento de Provedores**: Integrações externas (Pexels, Wikimedia, etc.) devem obrigatoriamente implementar a interface `MediaProvider` (`services/api/app/providers/base.py`) e nunca contaminar os serviços de domínio.
4. **Sem Refactors Aleatórios**: Features novas não devem alterar código não relacionado ou reescrever camadas sem necessidade.
5. **Observabilidade de Erros**: Falhas de integração e exceções de provedores não devem ser silenciosamente transformadas em listas vazias.
6. **Progressão Estrita de Sprints**: O `ROADMAP.md` é a fonte da verdade. Nunca inicie o Sprint $N+1$ antes de o Sprint $N$ cumprir 100% de sua *Definition of Done*.

---

## 2. Estrutura do Monorepo

- `apps/web`: Aplicação Next.js 14 (App Router), Tailwind CSS e shadcn/ui.
- `services/api`: API principal em FastAPI com SQLAlchemy 2.0 assíncrono.
- `services/worker`: Serviço em segundo plano para jobs assíncronos (Redis/Celery/SigLIP).
- `packages/contracts`: Tipos e interfaces compartilhadas.
- `infra/docker`: Dockerfiles dedicados para cada serviço.
- `docs/adr`: Registros de Decisões de Arquitetura (ADRs).
- `tests/e2e`: Testes ponta a ponta com Playwright.

---

## 3. Comandos de Verificação Mandatórios

Antes de submeter ou finalizar qualquer sprint:

```bash
# 1. Executar testes backend
.venv/bin/pytest -v

# 2. Executar testes frontend
cd apps/web && npm run test

# 3. Validar tipagem
.venv/bin/mypy --config-file mypy.ini services/api/app
cd apps/web && npm run typecheck

# 4. Validar formatação e lint
.venv/bin/ruff check services/api
cd apps/web && npm run lint
```

---

## 4. Classificação de Direitos (RightsStatus)

```python
RightsStatus.SAFE_REUSE             # Licença aberta verificada (CC0, Pexels, Domínio Público)
RightsStatus.ATTRIBUTION_REQUIRED   # Requer atribuição/crédito formal
RightsStatus.REVIEW_REQUIRED        # Licença ambígua ou necessita revisão manual
RightsStatus.REFERENCE_ONLY         # Protegido por copyright, uso estritamente referencial
RightsStatus.BLOCKED                # Proibido para uso
```
