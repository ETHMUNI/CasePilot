# CasePilot architecture

## Purpose and system boundary

CasePilot is an AI assistance layer that complements a company's existing
ticketing or support system. It is not intended to replace that system or become
the authoritative owner of customer conversations. The existing system remains
the source of support cases and the channel for customer communication.

CasePilot is intended to analyze case information and present traceable
suggestions to a support employee. A human remains responsible for reviewing,
changing, or rejecting suggestions and for deciding what is communicated to a
customer. CasePilot must not autonomously make final business-critical decisions
or send customer replies.

The architecture is a **modular monolith**: one backend application, with
responsibilities separated into Python modules. It is not a collection of
services. Modules and integration adapters should be introduced when their
behavior is implemented, rather than creating empty layers in advance.

Packages are organized by responsibility and dependency direction, rather than
putting every module for a broad feature or technology into one package. For
example, request and response contracts belong in `requests` and `responses`,
application logic in `services`, provider-specific code in `integrations/llm`,
and exceptions in `exceptions`. This is a lightweight convention, not a
requirement to introduce every Clean Architecture layer or a package for each
class.

## Current implementation

The repository provides Customer/Case persistence, a case-management REST API,
and an optional LLM-based case-analysis endpoint:

| Area | Implemented responsibility |
| --- | --- |
| `casepilot.main` | Creates the FastAPI application, checks database connectivity at startup, disposes the engine at shutdown, and registers health, case-management, and case-analysis routes. |
| `casepilot.config` | Reads environment settings and constructs the PostgreSQL connection URL. |
| `casepilot.database` | Creates the SQLAlchemy engine and session factory, exposes a session dependency, and checks connectivity. |
| `casepilot.models` | Defines Customer and Case persistence models, enum values, timestamps, and their relationship. |
| `casepilot.requests` and `casepilot.responses` | Define API and analysis input/output data contracts. |
| `casepilot.daos.customer_dao` and `casepilot.daos.case_dao` | Provide create/read/update access patterns for their respective entity. |
| `casepilot.services` | Coordinates case operations and case analysis independently of HTTP transport. |
| `casepilot.integrations.llm` | Builds the configured LLM provider and adapts LangChain models to the analysis-provider contract. |
| `casepilot.exceptions` | Defines application and configuration exceptions. |
| Alembic migrations | Establish the PostgreSQL `vector` extension and create the Customer/Case schema. |
| Docker Compose | Runs local PostgreSQL with pgvector. |
| Tests and GitHub Actions | Run unit and database/API integration tests, Ruff, and mypy. |

Case-management routes use request-scoped database sessions and delegate case
operations to services and DAOs. The analysis route reads a case, invokes the
configured provider, and returns a validated suggestion without changing the
case. Analysis is disabled by default; provider errors do not affect ordinary
case endpoints.

## Intended module and infrastructure boundaries

The following boundaries describe the implemented structure and planned work.

| Boundary | Responsibility | Status |
| --- | --- | --- |
| HTTP/API | FastAPI routes and Pydantic request/response validation. | Health, case-management, and case-analysis endpoints are implemented. |
| Application/domain | Coordinates use cases and keeps business rules independent of HTTP, SQL, and model providers. | Case services are implemented; broader AI and review workflows remain future work. |
| Persistence | SQLAlchemy sessions and PostgreSQL access; Alembic owns schema changes. | Customer and Case models and DAOs exist; user and other domain models do not. |
| AI integration | Calls a model for analysis and validates structured output before application logic uses it. | Optional OpenAI and Ollama providers are available through a LangChain adapter; disabled by default. |
| Knowledge retrieval | Loads approved internal material and retrieves supporting passages. PostgreSQL with pgvector is the initial storage/search choice. | Planned; no document ingestion, embeddings, or vector queries exist. |
| External integrations | Connects to the existing ticketing system and LLM providers through explicit adapters. | LLM adapters exist; ticketing-system integration is not implemented. |
| Human review | Presents suggestions with their sources and records an employee's decision. | Planned; no suggestions, review flow, or audit records exist. |

As the product grows, code should remain in this backend and these boundaries
should become concrete modules when a feature needs them. The first version uses
PostgreSQL for structured data and pgvector for a future embedding search,
avoiding a separate vector database at this stage.

## Intended data flow

The future case-assistance flow is:

1. Case information comes from the existing ticketing system through an API or
   integration adapter.
2. Application logic stores and prepares the information for analysis.
3. The AI layer returns validated suggestions; retrieval results and supporting
   sources remain traceable.
4. CasePilot presents the suggestions to a support employee for review.
5. The employee decides what to change or communicate in the existing support
   workflow.

Case management and a minimal analysis call are implemented. Analysis results
are not persisted; ingestion, retrieval, human review, and audit history remain
future work.

## Local setup

Use the [local database and backend setup instructions](../README.md#database)
and the [local backend development commands](../README.md#lokal-backendudvikling).
The README also documents [local testing and GitHub Actions checks](../README.md#github-actions-og-pull-requests).
