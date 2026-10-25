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

## Current implementation

The repository currently provides the backend foundation and basic
Customer/Case persistence. It does not yet expose case-management or AI APIs:

| Area | Implemented responsibility |
| --- | --- |
| `casepilot.main` | Creates the FastAPI application, checks database connectivity at startup, disposes the engine at shutdown, and exposes `GET /health`. |
| `casepilot.config` | Reads environment settings and constructs the PostgreSQL connection URL. |
| `casepilot.database` | Creates the SQLAlchemy engine and session factory, exposes a session dependency, and checks connectivity. |
| `casepilot.models` | Defines Customer and Case persistence models, enum values, timestamps, and their relationship. |
| `casepilot.daos.customer_dao` and `casepilot.daos.case_dao` | Provide create/read/update access patterns for their respective entity. |
| Alembic migrations | Establish the PostgreSQL `vector` extension and create the Customer/Case schema. |
| Docker Compose | Runs local PostgreSQL with pgvector. |
| Tests and GitHub Actions | Run unit and database/API integration tests, Ruff, and mypy. |

`get_session` is available for routes that need a database session, but no
current route depends on it. Customer and Case can be persisted through their
DAOs, but HTTP CRUD endpoints are not part of this issue. The
health route returns application health after the startup database connectivity
check; it does not use a request-scoped session.

## Intended module and infrastructure boundaries

The following boundaries describe where later behavior belongs. They are design
guidance, not claims that these features already exist.

| Boundary | Responsibility | Status |
| --- | --- | --- |
| HTTP/API | FastAPI routes and Pydantic request/response validation. | Health endpoint only today; case and integration endpoints are future work. |
| Application/domain | Coordinates use cases and keeps business rules independent of HTTP, SQL, and model providers. | Not implemented yet. |
| Persistence | SQLAlchemy sessions and PostgreSQL access; Alembic owns schema changes. | Customer and Case models and DAOs exist; user and other domain models do not. |
| AI | Calls a model for analysis and validates structured output before application logic uses it. | Planned; no model provider or AI workflow is installed. |
| Knowledge retrieval | Loads approved internal material and retrieves supporting passages. PostgreSQL with pgvector is the initial storage/search choice. | Planned; no document ingestion, embeddings, or vector queries exist. |
| External integrations | Connects to the existing ticketing system and, later, an LLM provider through explicit adapters. | Not implemented yet. |
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

Only the database connectivity and basic HTTP health check are implemented now.
The ingestion, analysis, retrieval, suggestion, and review steps above are
future work.

## Local setup

Use the [local database and backend setup instructions](../README.md#database)
and the [local backend development commands](../README.md#lokal-backendudvikling).
The README also documents [local testing and GitHub Actions checks](../README.md#github-actions-og-pull-requests).
