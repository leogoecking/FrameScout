# ADR 0001: Arquitetura Inicial do FrameScout

- **Status**: Aceito
- **Data**: 2026-08-24
- **Contexto**: Sprint 0 — Fundação

## Contexto e Problema
O FrameScout é uma plataforma para criadores de vídeo que transforma roteiros em planos visuais de cenas, integrando múltiplos provedores de mídia com avaliação rigorosa de direitos de uso (`RightsStatus`) e fidelidade factual. A plataforma precisa nascer como um sistema extensível, tipado e com separação clara de responsabilidades.

## Decisões Tomadas

1. **Estrutura em Monorepo Modular**:
   - `apps/web`: Frontend em Next.js (App Router), TypeScript, Tailwind CSS.
   - `services/api`: Backend em FastAPI assíncrono, SQLAlchemy 2.0 e Pydantic v2.
   - `services/worker`: Serviço desacoplado para tarefas em background (SigLIP, FFmpeg, extração futura).
   - `packages/contracts`: Contratos tipados compartilhados.

2. **Banco de Dados Relacional com Suporte a Vetores**:
   - PostgreSQL 16 como banco primário para persistência de Projetos, Cenas, Queries, Mídias e Assets Selecionados.
   - Suporte futuro a `pgvector` para ranking semântico multimodal.

3. **Isolamento Total de Provedores de Mídia**:
   - Interface `MediaProvider` obrigatória. Nenhuma lógica específica de API externa (Pexels, Wikimedia) pode existir no domínio de negócios.

4. **Direitos de Uso como Cidadão de Primeira Classe**:
   - O enum `RightsStatus` é obrigatório em qualquer candidato de mídia e nunca é presumido como seguro sem dados formais de licença.

5. **Infraestrutura Local via Docker Compose**:
   - Todos os serviços orquestrados com healthchecks determinísticos (`pg_isready`, endpoints `/health`).

## Consequências
- **Positivas**: Separação clara de domínio, desenvolvimento local simplificado sem dependência de serviços pagos, código fortemente tipado de ponta a ponta.
- **Riscos & Mitigações**: Manter a tipagem sincronizada entre Python e TypeScript através de contratos unificados em `packages/contracts`.
