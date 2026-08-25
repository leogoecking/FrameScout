# FrameScout — Product & Engineering Roadmap

> **Status:** Pre-MVP  
> **Objetivo atual:** entregar um MVP vertical utilizável por criadores reais.  
> **Princípio:** primeiro provar que encontramos mídia melhor e mais rápido; depois escalar inteligência, integrações e monetização.

---

# 1. Visão do Produto

O **FrameScout** é uma ferramenta para criadores de conteúdo que transforma um roteiro em um plano visual e ajuda a encontrar as melhores imagens, vídeos, B-rolls e referências para cada cena.

O sistema deve responder três perguntas para cada mídia encontrada:

1. **Esta mídia representa fielmente o que está sendo narrado?**
2. **A fonte é confiável?**
3. **O criador possui direito de reutilizá-la?**

A possibilidade técnica de visualizar ou baixar um arquivo **nunca implica automaticamente permissão de reutilização**.

---

# 2. Proposta de Valor

Fluxo desejado:

```text
ROTEIRO
   ↓
ANÁLISE
   ↓
CENAS
   ↓
ENTIDADES + FATOS + INTENÇÃO VISUAL
   ↓
QUERIES DE BUSCA
   ↓
PROVIDERS
   ↓
MÍDIAS ENCONTRADAS
   ↓
FONTE + DIREITOS + FIDELIDADE
   ↓
SELEÇÃO
   ↓
ORGANIZAÇÃO
   ↓
EXPORTAÇÃO PARA EDIÇÃO
```

Exemplo:

```text
Cena:
"Em julho de 2024, uma atualização da CrowdStrike
afetou milhões de computadores Windows."

↓

Resultado A:
Imagem real do incidente.
Fidelidade: 96/100
Fonte: imprensa
Direitos: REFERENCE_ONLY

Resultado B:
Vídeo de computadores em escritório.
Fidelidade: 61/100
Fonte: Pexels
Direitos: SAFE_REUSE
Uso sugerido: B-roll
```

---

# 3. Público-Alvo Inicial

Primeiro público:

- YouTubers;
- criadores de TikTok;
- criadores de Instagram Reels;
- canais faceless/dark;
- canais documentais;
- canais de notícias e tecnologia;
- produtores de vídeo independentes.

O primeiro ambiente de validação será o próprio fluxo de produção do **LOG FATAL**.

---

# 4. Stack

## Frontend

```text
Next.js
TypeScript
Tailwind CSS
shadcn/ui
```

## Backend

```text
Python
FastAPI
SQLAlchemy
Pydantic
```

## Dados

```text
PostgreSQL
pgvector — etapa futura
```

## Processamento

```text
FFmpeg
Pillow
SigLIP / OpenCLIP — etapa futura
```

## Background Jobs

```text
Redis
Celery — etapa futura
```

## Storage

```text
S3-compatible storage — etapa futura
```

## Qualidade

```text
pytest
Vitest
Playwright
GitHub Actions
```

## Ambiente local

```text
Docker Compose
```

---

# 5. Estrutura do Monorepo

```text
framescout/
├── apps/
│   └── web/
│
├── services/
│   ├── api/
│   └── worker/
│
├── packages/
│   └── contracts/
│
├── infra/
│   ├── docker/
│   └── migrations/
│
├── docs/
│   ├── architecture/
│   └── adr/
│
├── tests/
│
├── docker-compose.yml
├── Makefile
├── AGENTS.md
├── ROADMAP.md
├── README.md
└── .env.example
```

---

# 6. Domínio Inicial

Entidades principais:

```text
Project
Script
Scene
SearchQuery
MediaCandidate
SelectedAsset
MediaProvider
RightsStatus
```

## RightsStatus

```text
SAFE_REUSE
ATTRIBUTION_REQUIRED
REVIEW_REQUIRED
REFERENCE_ONLY
BLOCKED
```

Licença, autoria, fonte e procedência são dados de primeira classe e não podem ser tratados apenas como texto auxiliar.

---

# 7. Regras Arquiteturais

1. Providers externos não devem ser acoplados ao domínio.

2. Toda integração de mídia deve implementar contrato comum.

3. Credenciais devem existir apenas em variáveis de ambiente.

4. Nenhum provider deve transformar automaticamente conteúdo desconhecido em conteúdo reutilizável.

5. Falhas externas precisam permanecer observáveis.

6. Erros não devem ser silenciosamente convertidos em listas vazias.

7. Código novo deve receber testes proporcionais ao risco.

8. Features não devem introduzir refactors não relacionados.

9. Modelos e contratos devem ser tipados.

10. O MVP deve continuar executável localmente sem dependência obrigatória de serviços de IA pagos.

---

# 8. Roadmap de Desenvolvimento

## SPRINT 0 — Fundação

**Status:** NEXT

### Objetivo

Criar uma fundação confiável e reproduzível.

### Entregas

```text
Monorepo
Next.js
FastAPI
PostgreSQL
Docker Compose
.env.example
healthchecks
lint
format
pytest
Vitest
GitHub Actions
README
AGENTS.md
```

### Validação

```bash
docker compose up
```

deve iniciar todo o ambiente.

API:

```text
GET /health
```

deve responder com sucesso.

### Definition of Done

Build passa.

Lint passa.

Testes passam.

Frontend conecta com API.

API conecta com PostgreSQL.

README permite que outro desenvolvedor execute o projeto.

---

## SPRINT 1 — Projects & Scripts

### Objetivo

Permitir criar e persistir um projeto.

### Modelos

```text
Project
Script
```

### Funcionalidades

```text
Criar projeto
Listar projetos
Abrir projeto
Editar projeto
Salvar roteiro
```

### UI mínima

```text
Novo Projeto

Nome:
[                     ]

Idioma:
[Português ▼]

Roteiro:
[                                   ]
[                                   ]

[Salvar]
```

### Definition of Done

Projeto permanece disponível após reiniciar a aplicação.

---

## SPRINT 2 — Scene Engine

### Objetivo

Transformar roteiro em cenas.

### Modelo

```text
Scene

id
project_id
position
title
narration
visual_intent
start_estimate
end_estimate
created_at
updated_at
```

### Primeira versão

Implementar:

```text
divisão manual
+
heurística automática simples
```

LLM não será obrigatório nesta fase.

### UI

```text
CENA 01
CENA 02
CENA 03
...
```

O criador poderá:

```text
editar
dividir
unir
reordenar
```

### Definition of Done

Um roteiro consegue virar uma sequência editável de cenas.

---

## SPRINT 3 — Query Generator

### Objetivo

Transformar cenas em buscas úteis.

### Modelo

```text
SearchQuery

query
type
priority
scene_id
```

Tipos:

```text
official
event
company
person
location
concept
broll
```

### Exemplo

Entrada:

```text
"Take-Two tenta identificar o responsável
pelo vazamento de GTA VI."
```

Saída:

```text
GTA VI Take-Two leak investigation
Take-Two GTA 6 court leak
GTA VI legal action
Take-Two Interactive official
gaming leak investigation broll
```

### Definition of Done

Cada cena consegue produzir consultas diferentes para:

```text
fidelidade
fonte oficial
B-roll
```

---

## SPRINT 4 — Provider Architecture

### Objetivo

Criar o contrato central de provedores de mídia.

Contrato conceitual:

```python
class MediaProvider:
    async def search(
        self,
        query: SearchQuery
    ) -> list[MediaCandidate]:
        ...
```

### Não implementar lógica específica de provider dentro de services de domínio.

### Definition of Done

Um provider mock pode ser adicionado ou removido sem alterar o domínio.

---

## SPRINT 5 — Pexels

### Objetivo

Primeira fonte funcional de mídia reutilizável.

Implementar:

```text
PexelsProvider
```

Suporte inicial:

```text
Fotos
Vídeos
Preview
Autor
URL original
Dimensões
Duração
Licença
```

Mapeamento padrão:

```text
RightsStatus = SAFE_REUSE
```

quando as condições da licença aplicáveis estiverem devidamente identificadas.

### Definition of Done

Uma cena consegue pesquisar mídia real no Pexels.

---

## SPRINT 6 — Wikimedia Commons

### Objetivo

Adicionar mídia documental/histórica.

Implementar:

```text
WikimediaProvider
```

Capturar:

```text
arquivo
descrição
autor
licença
atribuição
página de origem
```

RightsStatus deve ser derivado dos metadados encontrados e nunca assumido.

### Definition of Done

Resultados Pexels e Wikimedia aparecem pelo mesmo contrato interno.

---

## SPRINT 7 — Rights Engine

### Objetivo

Tornar direitos e procedência parte essencial da experiência.

Cada resultado deve exibir:

```text
Provider
Source URL
Author
License
Attribution
RightsStatus
```

### Comportamento

`SAFE_REUSE`

Download permitido.

`ATTRIBUTION_REQUIRED`

Download permitido + informação de crédito.

`REVIEW_REQUIRED`

Exibir alerta.

`REFERENCE_ONLY`

Download para reutilização não deve ser oferecido automaticamente.

`BLOCKED`

Não disponibilizar para seleção.

### Definition of Done

Nenhuma mídia aparece sem informação explícita de procedência/status.

---

## SPRINT 8 — Media Browser

### Objetivo

Construir a primeira experiência que demonstra valor real.

Layout:

```text
┌──────────────┬─────────────────────────────┐
│ SCENES       │ CENA SELECIONADA            │
│              │                             │
│ 01 Hook      │ [Official] [B-roll] [Todos]│
│ >02 Falha    │                             │
│ 03 Impacto   │ [MEDIA][MEDIA][MEDIA]       │
│              │ [MEDIA][MEDIA][MEDIA]       │
└──────────────┴─────────────────────────────┘
```

Filtros:

```text
Todos
Fotos
Vídeos
Safe Reuse
Attribution
Reference
```

### Definition of Done

O usuário consegue navegar pelos resultados sem sair do contexto da cena.

---

## SPRINT 9 — Asset Selection

### Objetivo

Permitir curadoria humana.

Ações:

```text
Preview
Favoritar
Selecionar
Remover
Abrir fonte
Ver licença
```

Modelo:

```text
SelectedAsset
```

Uma cena pode possuir múltiplos assets.

### Definition of Done

Seleções persistem após fechar o projeto.

---

## SPRINT 10 — Project Export

### Objetivo

Entregar valor fora do FrameScout.

Exportação:

```text
project-name/
├── 01_scene/
├── 02_scene/
├── 03_scene/
├── references/
├── manifest.json
├── sources.csv
└── licenses.csv
```

### manifest.json

Deve relacionar:

```text
scene
narration
query
selected assets
source
rights
attribution
```

### Definition of Done

O criador consegue sair do FrameScout e iniciar sua edição usando o pacote exportado.

---

# 9. 🎯 MVP BETA

O produto alcança o primeiro MVP quando executar completamente:

```text
CRIAR PROJETO
      ↓
COLAR ROTEIRO
      ↓
GERAR CENAS
      ↓
GERAR QUERIES
      ↓
PEXELS + WIKIMEDIA
      ↓
RESULTADOS
      ↓
DIREITOS
      ↓
SELEÇÃO
      ↓
EXPORTAÇÃO
```

Nesse momento, iniciar testes com criadores reais.

---

# 10. Fase de Inteligência

Somente após validar o MVP.

---

## SPRINT 11 — Semantic Ranking

Adicionar:

```text
SigLIP ou OpenCLIP
```

Comparar:

```text
descrição da cena
↕

imagem
```

Resultado:

```text
semantic_similarity
0.00 → 1.00
```

---

## SPRINT 12 — Fidelity Score

Criar métrica própria:

```text
Fidelity Score
0 → 100
```

Primeiro modelo:

```text
40% similaridade semântica
25% correspondência de entidades
15% autoridade da fonte
10% data/contexto
10% qualidade técnica
```

Não misturar Fidelity Score com RightsStatus.

Um resultado pode ser:

```text
Fidelity: 98
Rights: REFERENCE_ONLY
```

ou:

```text
Fidelity: 61
Rights: SAFE_REUSE
```

---

## SPRINT 13 — Entity Extraction

Extrair automaticamente:

```text
pessoas
empresas
produtos
lugares
datas
eventos
tecnologias
```

Exemplo:

```text
CrowdStrike
Microsoft Windows
Falcon Sensor
19 July 2024
```

Usar entidades para melhorar queries.

---

## SPRINT 14 — Official Source Discovery

Adicionar descoberta de:

```text
sites oficiais
newsrooms
press kits
governo
documentação
GitHub
canais oficiais
```

Novo indicador:

```text
SourceAuthority
```

Exemplo inicial:

```text
OFFICIAL     100
GOVERNMENT   100
PRIMARY       95
NEWS          80
STOCK         70
UNKNOWN       20
```

---

## SPRINT 15 — Multimodal Reranking

Pipeline:

```text
100 resultados
      ↓
filtros
      ↓
SigLIP
      ↓
Top 20
      ↓
modelo multimodal
      ↓
Top 5
```

O modelo deve diferenciar:

```text
DIRECT MATCH
BROLL
REFERENCE
IRRELEVANT
```

---

# 11. Assistente de Produção

---

## SPRINT 16 — Storyboard Generator

Para cada cena:

```text
narração
visual recomendado
alternativas
texto na tela
tipo de mídia
duração sugerida
```

Exemplo:

```text
00:12–00:18

Narração:
"Mas não havia hacker nenhum."

Visual:
silhueta hacker → corte

Asset:
NÃO FOI UM ATAQUE

SFX:
glitch curto
```

---

## SPRINT 17 — Timeline Planning

Criar mapa:

```text
00:00 — Asset A
00:05 — B-roll B
00:12 — Asset C
00:18 — B-roll D
```

Preparar arquitetura para exportações futuras:

```text
Kdenlive
DaVinci Resolve
Premiere
Final Cut
```

---

# 12. SaaS

Somente iniciar após confirmação de Product-Market Fit.

Possíveis funcionalidades:

```text
Authentication
Cloud projects
Storage
Billing
Plans
Usage limits
Teams
Sharing
Analytics
```

Não implementar antes da validação do produto central.

---

# 13. Integrações Futuras

Providers possíveis:

```text
Pixabay
Magnific
Adobe Stock
Shutterstock
Getty
YouTube
News providers
Official media APIs
```

Outras integrações:

```text
Kdenlive
DaVinci Resolve
Premiere Pro
browser extension
YouTube transcript import
Whisper
```

---

# 14. Métricas do Produto

Desde os testes iniciais medir:

```text
tempo para encontrar mídia
mídias pesquisadas
mídias selecionadas
taxa de seleção
mídias descartadas
queries por cena
tempo até exportação
percentual de mídia SAFE_REUSE
```

Principal métrica inicial:

> **Quanto tempo o FrameScout economiza na etapa de pesquisa visual?**

Secundária:

> **Qual porcentagem das primeiras sugestões é realmente útil?**

---

# 15. Datasets de Validação

## Dataset #001

```text
LOG FATAL
GTA VI Leak
```

Objetivo:

Validar tema recente, games e notícias.

## Dataset #002

```text
LOG FATAL
CrowdStrike Global Outage
```

Objetivo:

Validar tecnologia, documentação oficial, eventos reais, imprensa e B-roll.

Comparar o resultado do FrameScout com a pesquisa manual já realizada.

---

# 16. Fora do Escopo Atual

Não implementar antes do MVP:

```text
Pagamentos
Planos comerciais
Marketplace
Mobile app
Desktop app
Browser extension
15+ providers
Video generation
AI avatars
Voice generation
Automatic full video editing
Team collaboration
Cloud infrastructure complexa
```

---

# 17. Política de Atualização deste Roadmap

O `ROADMAP.md` representa direção de produto.

Agentes e desenvolvedores podem atualizar:

```text
status
checkboxes
notas de implementação
riscos encontrados
datas
links para PRs
```

Mudanças significativas em:

```text
stack
arquitetura
escopo
domínio
ordem dos milestones
```

devem ser justificadas e documentadas em:

```text
docs/adr/
```

Não remover objetivos futuros apenas porque ainda não foram implementados.

---

# 18. Status

```text
SPRINT 0    NEXT
SPRINT 1    PLANNED
SPRINT 2    PLANNED
SPRINT 3    PLANNED
SPRINT 4    PLANNED
SPRINT 5    PLANNED
SPRINT 6    PLANNED
SPRINT 7    PLANNED
SPRINT 8    PLANNED
SPRINT 9    PLANNED
SPRINT 10   PLANNED

MVP BETA    PENDING

SPRINT 11+  FUTURE
```

---

# 19. Próxima Ação

Executar **Sprint 0 — Fundação**.

Antes de iniciar qualquer implementação:

```text
1. Ler AGENTS.md.
2. Ler ROADMAP.md.
3. Ler README.md.
4. Inspecionar estado atual do repositório.
5. Elaborar plano do Sprint.
6. Implementar apenas o escopo aprovado.
7. Executar testes.
8. Documentar resultado.
```

Não avançar automaticamente para o próximo sprint enquanto o atual não cumprir sua Definition of Done.

---

**FrameScout**

> Do roteiro à mídia certa — com contexto, procedência e confiança.