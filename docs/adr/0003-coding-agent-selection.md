# ADR 0003: Coding agent for feature slices (reference answer for Lab s10)

- **Status:** Accepted (illustrative: based on the lab's synthetic recordings of "tool A" and "tool B")
- **Date:** 2026-10-06
- **Re-evaluate:** in three months, or when either tool changes its model or pricing, with at least 20 tasks

## Context

We want one coding agent for day-to-day feature slices (autonomy L2–L3) on OrderHub. Opinions differed; demos and public benchmarks didn't match our work. We ran the evaluation harness (`tools/eval_harness`) on five real tasks with held-out acceptance tests, the full suite, lint and scope, and logged review time and findings for every change.

Constraints checked first: both tools may process this repository's code under our data agreement (synthetic data only; no customer data in prompts); both support the permission policy from Section 7 and our context file (AGENTS.md).

## Results

| | Tool A | Tool B |
|---|---|---|
| Harness success | 5/5 | 3/5 (T2 missed validation; T4 incomplete) |
| Model cost, all 5 tasks | $1.59 | $0.34 |
| Cost per successful task | $0.32 | $0.11 |
| Review minutes, all tasks | 30 | 15 |
| Defects found in review in "successful" changes | 0 | 1 (T3 merges quantities before validating them: −1 and +2 of one SKU passes as 1) |
| Changes we'd merge after review | 5 | 2 |
| Rework needed | none | redo T2, T3, T4: with tool A that adds $1.11 and 22 review minutes (its recorded runs) |

## Decision

Use tool A for feature slices. Don't adopt tool B for feature work. Tool B's lower price per call is outweighed by rework and by a defect the held-out tests didn't catch; the person's time dominates the cost of both.

## Consequences

- Model spend for slices is higher per task; total cost per merged change is lower once review and rework are counted.
- Five tasks is a small sample. The decision is provisional; the harness and tasks are kept so the comparison can be re-run in minutes.
- The T3 defect shows our held-out tests can be passed by a wrong change: add a test for negative quantities in merged lines to T3.
- We keep one tool per row of the landscape map (no second editor agent).

## Applies to

Interactive and headless agent use on OrderHub feature work (Sections 4–6 workflow). Automated reviewers and CI agents are separate decisions.
