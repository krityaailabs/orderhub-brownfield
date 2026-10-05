# OrderHub Brownfield

The course repository for **AI Coding Agents in Production** (Kritya AI Labs).

OrderHub is a small order and fulfilment platform with a history. Like most real systems, it was built by several people over several years:

- `services/orders/` is the order service: Python, FastAPI and SQLAlchemy. It is reasonably modern and reasonably tested.
- `legacy/billing/` is the nightly billing batch: Java, written for Java 8 and built with a shell script. It reads a CSV handoff from the order service and writes a fixed-width file for the finance system. It has very few tests, and its documentation is out of date.
- `web/` is a small optional frontend, added later in the course.

All data is synthetic. No real company, customer or system is represented.

## Quick start

```bash
make setup     # create .venv and install pinned dependencies
make doctor    # check Python, Java and the packages
make test      # Python tests and the legacy self-test; expect 0 failures
```

Without `make`, open the `Makefile` and run the command under each target. On Windows, use WSL.

Requirements: Python 3.11 or newer, a JDK 11 or newer (with `javac`), and Git. No paid AI subscription is needed for any lab; see `docs/course/tool-and-cost-worksheet.md`.

## Commands

| Command | What it does |
|---|---|
| `make test-py` | Python tests (`cd services/orders && python -m pytest -q`) |
| `make test-java` | Builds the legacy module and runs its self-test |
| `make lint` | Lints the Python code with ruff |
| `make billing-demo` | Places sample orders, writes the CSV handoff and runs the Java nightly batch |
| `make doctor` | Checks this machine |

Run the order service locally:

```bash
cd services/orders
../../.venv/bin/python -m orderhub.seed
../../.venv/bin/python -m uvicorn orderhub.api:app --reload   # optional: pip install uvicorn
```

## Layout

```
services/orders/   order service (Python)
legacy/billing/    nightly billing batch (Java)
data/              synthetic seed data
docs/issues/       open issues (start here in Section 0)
docs/adr/          architecture decision records (from Section 2)
docs/specs/        specifications (from Section 3)
docs/course/       course one-pagers and worksheets
labs/              lab instructions per section
tools/             doctor, demos and course tooling
web/               optional frontend
```

## Course tags

Each section's lab starts at a `-start` tag and ends at a solved tag, for example `s02-start` and `s02`. This snapshot is tag `s00`, the baseline.

```bash
git checkout s00
```
