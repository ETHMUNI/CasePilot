# ADR 0001: Python backend with FastAPI and PostgreSQL

- Status: Accepted
- Date: 2026-10-12

## Context

CasePilot needs a backend for a human-reviewed support-assistance workflow. The
initial work should provide a small, reproducible API and database foundation
without introducing services for features that are not implemented yet. The
system will handle structured support records and may later search document
embeddings.

## Decision

- Use Python for the backend implementation.
- Use FastAPI for the HTTP API and Pydantic validation at API boundaries.
- Use PostgreSQL for structured application data and pgvector for planned
  embedding storage and similarity search.
- Use SQLAlchemy for database connections and sessions, and Alembic for schema
  migrations.
- Keep the backend a modular monolith. Integrations and AI behavior will be
  added behind module boundaries as their requirements are implemented.

## Rationale

Python provides a direct path to the planned AI and data ecosystem. FastAPI
provides typed request/response validation and an HTTP API without requiring a
separate application server layer. PostgreSQL supports relational data and can
host pgvector, so the first version can use one database. SQLAlchemy and Alembic
provide explicit session handling and repeatable schema changes.

## Consequences

- The first release has one backend process and one PostgreSQL database to
  develop and operate.
- PostgreSQL remains responsible for reliable relational records; vector search
  is an additional planned capability, not a reason to store all data as
  documents.
- Python's runtime typing is supplemented by mypy and tests.
- The decision did not define the full case-management feature set. Basic
  Customer/Case persistence is implemented separately; HTTP case routes,
  ticketing connectors, an LLM framework, retrieval, and human review still
  require separate implementation work.

## Alternatives considered

- A separate service per feature was rejected for the initial scope because the
  application does not yet have independently deployable components.
- A separate NoSQL or vector database was not selected because the current
  structured data and initial embedding-search plan fit PostgreSQL.
- LangChain and LangGraph are deferred until a concrete AI workflow requires
  them.
