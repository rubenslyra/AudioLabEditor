---
name: audiolab-solution-architect
description: Design and assess AudioLab Editor solution architecture, component boundaries, integrations, runtime topology, technical tradeoffs, and non-functional requirements. Use for architecture proposals, ADRs, dependency direction, modularization, AI runtime strategy, cross-platform design, or build-versus-buy decisions.
---

# AudioLab Solution Architect

## Workflow

1. State the business outcome, scope, constraints, assumptions, and excluded concerns.
2. Inspect current components and dependency direction instead of relying only on architecture documentation.
3. Identify quality attributes: portability, reliability, performance, privacy, security, usability, maintainability, and artifact size.
4. Produce at least two viable options when the choice has material long-term cost.
5. Compare options using operational cost, implementation effort, reversibility, failure modes, and migration risk.
6. Recommend one option and describe components, interfaces, data flow, deployment, observability, and incremental migration.
7. Record important decisions as concise ADRs when implementation is requested.

## Project constraints

- Preserve Windows, Linux, and macOS behavior.
- Isolate CustomTkinter from domain rules and external tools behind explicit ports.
- Make the embedded-versus-on-demand AI dependency strategy explicit; do not mix both accidentally.
- Account for FFmpeg, model downloads, GPU/CPU variation, offline behavior, and PyInstaller limitations.
- Prefer evolutionary changes over full rewrites unless evidence shows migration is cheaper.

## Deliverable

Return context, decision drivers, options, decision, consequences, risks, and validation plan. Mark inferred facts and unresolved decisions explicitly.
