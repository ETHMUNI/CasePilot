# CasePilot – AI-understøttet sagsbehandling til B2B support

CasePilot er et AI-understøttet sagsbehandlingssystem designet til virksomheder, der håndterer mange kundehenvendelser og supportsager.

Systemet fungerer som en AI-assistent for support- og sagsbehandlere. Det analyserer nye sager, finder relevant intern dokumentation og genererer forslag til næste handling og svar.

CasePilot er designet som et supplement til eksisterende support- og sagsbehandlingssystemer. Den endelige beslutning og kommunikation med kunden forbliver hos medarbejderen.

---

## 1. Problem Statement

B2B-softwarevirksomheder modtager ofte et stort antal kundehenvendelser gennem supportportaler, e-mail eller andre kanaler.

En supportmedarbejder skal typisk:

1. Læse og forstå sagen
2. Kategorisere problemet
3. Vurdere alvorlighed og prioritet
4. Identificere relevant produktområde eller team
5. Søge efter relevant intern dokumentation
6. Undersøge tidligere kendte problemer
7. Formulere et svar eller næste handling

En stor del af denne proces består af manuelt informationsarbejde.

Det kan føre til:

- længere svartider
- forskellig kvalitet i sagsbehandlingen
- unødvendig eskalering
- længere onboarding af nye medarbejdere
- gentaget arbejde på lignende sager
- afhængighed af enkelte medarbejderes produktviden

CasePilot skal reducere dette arbejde ved at analysere sagen og samle relevant information for medarbejderen.

Systemet skal ikke automatisk træffe forretningskritiske beslutninger eller sende svar til kunder.

Målet er at gøre medarbejderen hurtigere og bedre informeret.

---

## 2. Features

### Case ingestion

Sager kan oprettes direkte i CasePilot eller modtages fra et eksisterende supportsystem gennem et API.

En sag kan blandt andet indeholde:

- titel
- beskrivelse
- kunde
- produkt
- tidspunkt
- eksisterende prioritet
- kanal
- eventuelle attachments

---

### Automatisk sagsklassifikation

CasePilot analyserer nye sager og foreslår:

- kategori
- underkategori
- prioritet
- relevant produktområde
- relevant team
- kort opsummering
- mulige næste handlinger

Eksempel:

```json
{
  "category": "Authentication",
  "subcategory": "Microsoft SSO",
  "priority": "High",
  "suggested_team": "Technical Support",
  "summary": "40 users are unable to authenticate through Microsoft SSO after a configuration change.",
  "confidence": 0.94
}
```

Medarbejderen kan ændre klassifikationen, hvis AI'ens forslag er forkert.

---

### Knowledge retrieval

CasePilot søger automatisk efter relevant intern dokumentation.

Knowledge basen kan eksempelvis indeholde:

- produktdokumentation
- troubleshooting guides
- supportprocedurer
- SLA-regler
- kendte fejl
- release notes
- interne vejledninger

Systemet skal vise hvilke dokumenter, der ligger til grund for AI'ens forslag.

---

### Suggested actions

CasePilot kan foreslå konkrete næste handlinger.

Eksempel:

```text
Suggested actions:

1. Verify the customer's Microsoft Entra tenant configuration.
2. Check whether affected users are correctly provisioned.
3. Review authentication logs for failed SSO requests.
```

Forslagene skal være baseret på den tilgængelige dokumentation.

---

### Suggested response

Systemet kan generere et forslag til svar til kunden.

Svaret baseres på:

- kundens oprindelige henvendelse
- sagens klassifikation
- relevant dokumentation
- foreslåede troubleshooting steps

AI-genererede svar må ikke automatisk sendes til kunden.

---

### Human-in-the-loop review

En medarbejder skal altid gennemgå AI'ens forslag.

Medarbejderen kan:

```text
Approve
Edit
Reject
```

Systemet gemmer medarbejderens beslutning.

Dette bruges både som audit trail og til senere evaluering af systemets kvalitet.

---

### Case history

Systemet skal kunne vise:

- AI'ens oprindelige forslag
- hvilke dokumenter der blev hentet
- hvem der behandlede sagen
- ændringer foretaget af medarbejderen
- endelig klassifikation
- endeligt svar

Dette gør processen sporbar.

---

## 3. Architecture

CasePilot designes som en separat service, der kan integreres med et eksisterende support- eller sagsbehandlingssystem.

```text
                         Existing Support System
                         / Email / Portal / API
                                   |
                                   v
                              CasePilot API
                               (FastAPI)
                                   |
                 +-----------------+-----------------+
                 |                 |                 |
                 v                 v                 v
          Case Management     AI Processing    Knowledge Service
                 |                 |                 |
                 |                 |                 v
                 |                 |            Vector Search
                 |                 |                 |
                 |                 +-----------------+
                 |                           |
                 |                           v
                 |                          LLM
                 |
                 v
             PostgreSQL
```

### Backend API

FastAPI fungerer som systemets centrale API.

API'et håndterer blandt andet:

- sager
- brugere
- AI-analyser
- knowledge documents
- reviews
- integrationskald

---

### Application layer

Forretningslogikken holdes adskilt fra AI-integrationen.

Eksempel:

```text
CaseService
ClassificationService
KnowledgeService
SuggestionService
ReviewService
```

På den måde kan dele af systemet fungere, selv hvis AI-servicen ikke er tilgængelig.

---

### AI layer

AI-komponenten håndterer:

- classification
- summarization
- query generation
- retrieval
- response generation

LLM-output skal valideres, før det anvendes af resten af systemet.

---

### Data layer

PostgreSQL anvendes til almindelige relationelle data.

`pgvector` anvendes til embeddings og semantic search.

Det betyder, at systemet ikke behøver en separat vector database i den første version.

---

### Integration layer

CasePilot skal på sigt kunne integreres med eksisterende systemer gennem:

```text
REST API
Webhooks
```

Eksempelvis kunne et eksisterende supportværktøj sende en ny sag til CasePilot og modtage AI'ens analyse retur.

---

## 4. Tech Stack

### Backend

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic

### Database

- PostgreSQL
- pgvector

### AI

- LangChain (LLM-integration, embeddings og retrieval)
- LangGraph (AI-workflow og state management)
- LLM API eller lokal model via Ollama
- Structured output via Pydantic
- Retrieval-Augmented Generation (RAG)
- Semantic search med pgvector

LangChain og LangGraph er planlagte teknologier; de introduceres, når AI-workflowet implementeres.

### Lokal backendudvikling

Backendmiljøet bruger Python 3.12.2 og uv. Installér uv, og kør derefter:

```bash
cd backend
uv sync --dev
cp .env.example .env
uv run --env-file .env uvicorn casepilot.main:app --reload --app-dir src
```

API'et kører som standard på `http://127.0.0.1:8000`, og `GET /health` returnerer
`{"status":"ok"}`. Udviklingsværktøjer køres fra `backend/` med `uv run pytest`,
`uv run ruff check .`, `uv run ruff format --check .` og `uv run mypy`.

### Testing og AI-evaluering

- pytest
- Unit tests
- Integration tests
- AI evaluation tests (klassifikation, retrieval og groundedness)
- Versionerede evalueringsdatasæt og sammenligning af modeller/prompts

### Infrastructure

- Docker
- Docker Compose

### Observability

Mulige senere komponenter:

- structured logging
- request tracing
- AI latency metrics
- token usage
- error monitoring

### Frontend

En simpel frontend kan i første omgang bygges med Streamlit.

En senere version kan erstattes af en dedikeret frontend såsom:

- React
- Angular

---

## 5. Database Entities

### Customer

Repræsenterer virksomheden, der har oprettet sagen.

Mulige felter:

```text
id
name
external_id
created_at
```

---

### User

Repræsenterer en supportmedarbejder eller administrator.

Mulige felter:

```text
id
name
email
role
team_id
created_at
```

---

### Team

Repræsenterer et support- eller produktteam.

Eksempel:

```text
Technical Support
Billing
Customer Success
Product Support
```

Mulige felter:

```text
id
name
description
```

---

### Case

Repræsenterer en kundehenvendelse.

Mulige felter:

```text
id
external_id
customer_id
title
description
status
category
subcategory
priority
assigned_user_id
assigned_team_id
source
created_at
updated_at
closed_at
```

---

### AIAnalysis

Gemmer AI'ens analyse af en sag.

Mulige felter:

```text
id
case_id
summary
suggested_category
suggested_subcategory
suggested_priority
suggested_team
confidence_score
model
prompt_version
created_at
```

---

### KnowledgeDocument

Repræsenterer intern dokumentation.

Mulige felter:

```text
id
title
document_type
source
version
content
created_at
updated_at
```

---

### DocumentChunk

Repræsenterer den del af dokumentet, der anvendes til retrieval.

Mulige felter:

```text
id
document_id
content
embedding
chunk_index
metadata
```

---

### RetrievalResult

Gemmer hvilke dokumenter der blev fundet for en bestemt sag.

Mulige felter:

```text
id
case_id
document_chunk_id
similarity_score
retrieval_rank
created_at
```

Dette gør det muligt senere at undersøge, hvorfor AI'en fik bestemt kontekst.

---

### AISuggestion

Gemmer AI'ens forslag til handling og svar.

Mulige felter:

```text
id
case_id
suggested_action
suggested_response
model
prompt_version
created_at
```

---

### Review

Gemmer medarbejderens vurdering af AI-forslaget.

Mulige felter:

```text
id
ai_suggestion_id
user_id
decision
edited_response
feedback
reviewed_at
```

Mulige værdier:

```text
approved
edited
rejected
```

---

## 6. AI / RAG Flow

AI-flowet opdeles i flere separate trin.

Dette gør det lettere at teste og identificere fejl.

### Step 1 – Case classification

Den nye sag analyseres af en LLM.

Input:

```text
Case title
Case description
Customer information
```

Output:

```text
Category
Subcategory
Priority
Suggested team
Summary
Confidence
```

Outputtet returneres som struktureret data og valideres gennem Pydantic.

---

### Step 2 – Retrieval query

Der genereres en søgeforespørgsel baseret på sagen.

Eksempel:

```text
Microsoft SSO users unable to authenticate after tenant configuration change
```

---

### Step 3 – Embedding

Søgeforespørgslen konverteres til en embedding.

Embeddings bruges til at sammenligne betydningen af tekst frem for kun at matche præcise ord.

---

### Step 4 – Knowledge retrieval

Embedding sammenlignes med dokumentchunks i `pgvector`.

Eksempel:

```text
1. Microsoft SSO Troubleshooting Guide
2. User Provisioning Documentation
3. Known Authentication Issues
```

Kun de mest relevante dokumenter sendes videre.

---

### Step 5 – Context construction

Systemet samler:

```text
Original case
+
AI classification
+
Relevant documentation
```

Konteksten skal holdes så begrænset og relevant som muligt.

---

### Step 6 – Suggested action

LLM'en genererer konkrete næste handlinger baseret på dokumentationen.

Eksempel:

```text
1. Check user provisioning.
2. Verify tenant configuration.
3. Inspect authentication logs.
```

---

### Step 7 – Response generation

LLM'en genererer et forslag til kundesvar.

Svaret skal være baseret på den dokumentation, der blev retrieved.

Systemet skal kunne vise kilder sammen med svaret.

---

### Step 8 – Human review

Medarbejderen kan:

```text
Approve
Edit
Reject
```

Den endelige beslutning gemmes.

AI'en sender aldrig automatisk svaret til kunden.

---

## 7. Milestones

### V1 – Core Case Management

Målet er at bygge et fungerende backend-system uden AI.

Features:

- FastAPI setup
- PostgreSQL
- SQLAlchemy
- Alembic migrations
- Customers
- Users
- Teams
- Cases
- Case assignment
- Case status
- REST API
- pytest
- Docker

Denne version etablerer systemets grundlæggende domænemodel og API.

---

### V2 – AI Case Classification

Målet er at automatisere den første analyse af nye sager.

Features:

- LLM integration
- Structured output
- Category classification
- Priority suggestion
- Team suggestion
- Case summarization
- Confidence score
- Pydantic validation
- Persist AI analysis
- Error handling

Medarbejderen skal stadig kunne tilsidesætte AI'ens klassifikation.

---

### V3 – Knowledge Base and Retrieval

Målet er at koble AI'en til virksomhedens interne dokumentation.

Features:

- Import af knowledge documents
- Document chunking
- Embedding generation
- pgvector
- Semantic search
- Top-K retrieval
- Retrieval result logging

Systemet skal kunne vise hvilke dokumenter, der blev fundet.

---

### V4 – AI Suggested Actions and Responses

Målet er at hjælpe medarbejderen med selve sagsbehandlingen.

Features:

- Suggested actions
- Suggested response
- Grounded generation
- Source references
- Persist suggestions
- Prompt versioning

AI'en må ikke sende noget direkte til kunden.

---

### V5 – Human Review and Audit Trail

Målet er at gøre systemet sikkert og anvendeligt i en realistisk virksomhedskontekst.

Features:

- Approve suggestion
- Edit suggestion
- Reject suggestion
- Review history
- Original vs. final response
- User feedback
- Audit trail

Det skal være muligt at se, hvordan AI'ens forslag blev ændret af medarbejderen.

---

### V6 – Evaluation and Production Readiness

Målet er at undersøge, om systemet faktisk giver forretningsmæssig værdi.

Features:

- Evaluation dataset
- Classification metrics
- Retrieval metrics
- Human review metrics
- Response quality evaluation
- Latency measurements
- Error monitoring
- Prompt version comparison
- Model comparison
- Cost/token tracking

V6 skal bruges til at afgøre, om CasePilot realistisk ville være egnet til en pilot i en virksomhed.

---

## 8. Evaluation Plan

Evalueringen skal både måle AI-kvalitet og potentiel forretningsværdi.

Systemet bør ikke vurderes alene på, om et genereret svar "ser godt ud".

---

### Classification accuracy

Et testdatasæt oprettes med manuelt klassificerede sager.

Eksempel:

```text
Expected:
Category: Authentication
Priority: High
Team: Technical Support

Predicted:
Category: Authentication
Priority: High
Team: Technical Support
```

Metrics:

```text
Category accuracy
Priority accuracy
Team routing accuracy
```

---

### Retrieval quality

For hver testsag defineres hvilke dokumenter der forventes at være relevante.

Eksempel:

```text
Expected document:
Microsoft SSO Troubleshooting Guide
```

Systemet evalueres på, om dokumentet findes blandt de første retrieval-resultater.

Metrics kan eksempelvis være:

```text
Top-1 accuracy
Top-3 accuracy
Top-5 accuracy
```

---

### Groundedness

Det skal vurderes, om AI'ens svar faktisk kan understøttes af den dokumentation, der blev retrieved.

Eksempel på fejl:

```text
Retrieved documents:
Password Reset Guide

Generated response:
"Your subscription has already been refunded."
```

Denne information findes ikke i dokumentationen og bør markeres som en fejl.

---

### Human review metrics

Medarbejderens handling bruges som praktisk kvalitetsindikator.

Metrics:

```text
Approval rate
Edit rate
Rejection rate
```

Eksempel:

```text
Approved: 65%
Edited:   28%
Rejected:  7%
```

Der kan desuden måles hvor meget et svar typisk bliver redigeret.

---

### Time saved

En vigtig business metric er, om systemet faktisk reducerer behandlingstiden.

Der kan sammenlignes:

```text
Average handling time without AI
vs.
Average handling time with CasePilot
```

Eksempel:

```text
Without AI: 8.4 minutes
With AI:    5.1 minutes
```

---

### Escalation rate

Systemet kan måle, om AI-assistance reducerer antallet af unødvendige eskaleringer til mere specialiserede teams.

```text
Escalation rate before CasePilot
vs.
Escalation rate with CasePilot
```

---

### AI latency

En teknisk korrekt løsning er ikke nødvendigvis brugbar, hvis medarbejderen skal vente for længe.

Derfor måles:

```text
Classification latency
Retrieval latency
Response generation latency
Total AI processing time
```

---

### Cost

Hvis der bruges en ekstern LLM-provider, skal systemet måle:

```text
Input tokens
Output tokens
Estimated cost per case
Estimated monthly cost
```

Det gør det muligt at vurdere forholdet mellem:

```text
AI cost
vs.
time saved
```

---

### Failure analysis

Fejl skal opdeles efter hvor i pipeline de opstår.

```text
Incorrect classification
        |
        v
Wrong retrieval query
        |
        v
Wrong documentation
        |
        v
Poor response
```

Det gør det muligt at identificere, om et dårligt slutresultat skyldes:

- klassifikation
- retrieval
- dokumentationen
- prompten
- modellen
- selve response generation

---

## Business Success Criteria

En fremtidig pilot af CasePilot kan eksempelvis betragtes som succesfuld, hvis systemet:

- reducerer gennemsnitlig behandlingstid
- finder relevant dokumentation med høj præcision
- producerer svar, som sjældent afvises
- reducerer manuelt søgearbejde
- ikke øger antallet af fejlagtige svar
- kan forklare hvilke kilder der ligger til grund for AI'ens forslag
- giver medarbejderen fuld kontrol over den endelige beslutning

CasePilot skal derfor vurderes på både AI-performance, teknisk stabilitet og reel forretningsværdi.
