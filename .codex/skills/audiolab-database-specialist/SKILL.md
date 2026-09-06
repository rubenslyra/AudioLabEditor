---
name: audiolab-database-specialist
description: Design, review, and evolve AudioLab Editor persistence, data models, metadata, caches, job history, migrations, retention, backup, and privacy controls. Use when a feature needs structured storage, database selection, schema design, query analysis, data lifecycle, or migration planning.
---

# AudioLab Database Specialist

## Workflow

1. Confirm whether persistence is actually required. Prefer existing JSON settings or filesystem outputs for simple local state.
2. Define entities, ownership, cardinality, lifecycle, volume, access patterns, consistency, and concurrency needs.
3. Classify personal, sensitive, derived, cached, and disposable data.
4. Select storage using evidence. Default to SQLite for relational local-first data unless requirements justify another engine.
5. Define schema, constraints, indexes, transactions, migration order, rollback or forward-fix strategy, retention, and deletion.
6. Validate representative queries and failure recovery before integration.
7. Keep persistence behind application-facing repositories or ports.

## Guardrails

- Do not store media payloads in a database by default; store controlled paths and metadata.
- Never persist secrets, tokens, transcripts, or user paths without an explicit purpose and retention policy.
- Enable foreign keys and use parameterized statements.
- Make migrations repeatable, ordered, observable, and safe against existing user data.
- Design for interrupted writes, locked files, corrupt data, downgrade attempts, and concurrent jobs.

## Deliverable

Provide requirements, model, schema or migration, query/index rationale, privacy controls, backup/recovery behavior, and tests. State why a database is preferable to the current filesystem approach.
