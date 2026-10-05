# Copilot instructions

This repository's instructions for coding agents live in `AGENTS.md` at the root, with more specific `AGENTS.md` files in `legacy/billing/` and `web/`. Copilot surfaces that read AGENTS.md use them directly; this file exists for surfaces that read only this file.

Summary of the rules that matter most:
- Run `make test` and `make lint` before calling a change done; run `make billing-demo` if the billing handoff is touched.
- Money is integer minor units; never floats.
- Never edit an existing test to make it pass.
- Never change the CSV handoff columns or the billing export layout without finance's agreement.
