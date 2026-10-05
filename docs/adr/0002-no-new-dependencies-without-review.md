# ADR 0002: No new dependencies without review

- **Status:** Accepted
- **Date:** 2026-10-05

## Context

Coding agents add packages readily, sometimes suggesting names that do not exist or that duplicate one already installed. Every dependency is code we did not review, with its own licence and update cadence.

## Decision

A change that adds a dependency must say why, in the pull request: what it does that existing code or the standard library cannot, its licence, and its maintenance status. A human approves it. `requirements.lock` changes only as part of such a change.

## Consequences

- Agents should prefer the standard library and existing dependencies.
- Section 7 adds an automated dependency check in CI.

## Applies to

`requirements.lock`, `services/orders/pyproject.toml`, `legacy/billing/` (no dependency manager yet).
