# Lab s00: Set up OrderHub Brownfield (Lecture 0.4)

**Objective:** run the full test suite, the legacy batch and the doctor check, and set a spend guard.
**Time:** 20–30 minutes. **Agent usage:** none required.
**Start and end tag:** `s00` (no learner stubs in this lab).

## Steps

1. Clone the repository and check out the baseline:
   ```bash
   git checkout s00
   ```
2. Create the environment and install pinned dependencies:
   ```bash
   make setup
   ```
3. Check your machine:
   ```bash
   make doctor
   ```
   Every required line must say `OK`.
4. Run all tests:
   ```bash
   make test
   ```
   Expected: `27 passed` for Python and `all checks passed` for the legacy self-test.
5. Run the billing demo, which goes from order service to CSV handoff to the Java nightly batch:
   ```bash
   make billing-demo
   ```
   Expected: a `BILLyyyymmdd.DAT` file with 5 records, every record 80 characters.
6. Fill in `docs/course/tool-and-cost-worksheet.md`.

Compare your output with `EXPECTED_OUTPUT.md`. If something fails, see `TROUBLESHOOTING.md`.

## Break it (2 minutes)

Open `legacy/billing/docs/RECORD_LAYOUT.txt` and compare the documented width of the net amount with the `zero(r.totalMinor, 11)` call in `FixedWidthExport.java`. Which one is right? You'll come back to this in Section 8.

## Done when

- [ ] `make doctor` passes
- [ ] `make test` shows 0 failures
- [ ] `make billing-demo` writes a file whose records are all 80 characters
- [ ] The worksheet is filled in
