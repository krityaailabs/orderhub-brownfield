# Upgrade plan: legacy/billing from Java 8 bytecode to Java 21 (Lecture 8.5)

**Goal:** build and run the billing batch as Java 21, with a modern build tool, without changing a byte of the output finance receives.
**Safety net:** `python tools/billing_golden.py check` (52 records, byte for byte), `tools/tests/test_billing_contracts.py` (11 implicit contracts), `python tools/billing_compare.py` (old vs new tax path), `make billing-demo`.
**Rule:** one batch per pull request; each batch has a rollback that is a single revert; the golden check passes at the end of every batch.

| Batch | Change | Verify | Rollback | Status |
|---|---|---|---|---|
| 1 | Compile with `--release 11` (`JAVA_RELEASE=11 ./build.sh`); fix any warnings; no source changes expected | golden check `--release 11`; contracts; self-test | `JAVA_RELEASE` back to 8 | **Done in s08**: 52 records identical; self-test passes |
| 2 | `--release 17`; replace `SimpleDateFormat` (not thread-safe) with `java.time` in `NightlyBatch` and the header | golden check; contracts (header `ddMMyy`) | revert the PR | Planned |
| 3 | Introduce a build tool (Maven or Gradle) alongside `build.sh`; same compiler flags; CI runs both | both builds produce identical class output for the golden run | delete the build file | Planned (needs the team's artifact mirror) |
| 4 | `--release 21` as the default; production JVM to 21 | golden check on the production JVM in staging; one night in parallel with the old JVM, outputs compared | switch the scheduler back to the old JVM | Planned |
| 5 | Remove `build.sh`'s release-8 path | — | revert | Planned |

## What the agent does and doesn't do

- Does: make the mechanical changes in each batch, run every check, write the PR with the check output.
- Doesn't: change output formats, rounding or encodings (AGENTS.md boundary); add libraries; skip a batch; re-record golden files.

## Risks noticed while planning

- `SimpleDateFormat` and default time zone: the header date depends on the server's zone; batch 2 must keep `ddMMyy` and the same zone.
- Default charset changed to UTF-8 in Java 18 (JEP 400). The export sets ISO-8859-1 explicitly and the reader sets UTF-8 explicitly, so this module is safe; any new I/O code must set the charset too.
