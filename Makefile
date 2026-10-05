# OrderHub Brownfield: common tasks. Run `make help` for the list.
# Windows: use WSL. Without make, run the commands shown under each target.

PY ?= .venv/bin/python
ifeq ($(OS),Windows_NT)
PY = .venv/Scripts/python
endif

.PHONY: help setup doctor test test-py test-tools test-java lint install-hooks precommit mutate protect-tests spec-check context-check billing-demo review-flags clean

help:
	@echo "setup         create .venv and install pinned dependencies"
	@echo "doctor        check this machine can run the labs"
	@echo "test          run all tests (Python service and legacy Java self-test)"
	@echo "test-py       Python tests only"
	@echo "test-tools    tests for the course tools"
	@echo "test-java     legacy billing build and self-test only"
	@echo "lint          ruff lint for the Python service"
	@echo "install-hooks install the git pre-commit hook"
	@echo "precommit     run the checks the staged files need"
	@echo "mutate        mutation tests for the returns feature"
	@echo "protect-tests fail if existing test lines changed without approval"
	@echo "spec-check    check specs and slice plans in docs/specs"
	@echo "context-check check the agent context pack (AGENTS.md and friends)"
	@echo "billing-demo  place orders, write the CSV handoff, run the legacy nightly batch"
	@echo "review-flags  point a reviewer at the risky lines of a diff (BASE=ref or DIFF=file)"

setup:
	python3 -m venv .venv
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install -r requirements.lock

doctor:
	$(PY) tools/doctor.py

test: test-py test-tools test-java

test-py:
	cd services/orders && ../../$(PY) -m pytest -q

test-tools:
	$(PY) -m pytest -q -p no:cacheprovider tools/tests

test-java:
	legacy/billing/build.sh

lint:
	$(PY) -m ruff check services/orders tools

install-hooks:
	cp tools/hooks/pre-commit .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit
	@echo "pre-commit hook installed"

precommit:
	$(PY) tools/precommit.py

mutate:
	$(PY) tools/mutate.py

protect-tests:
	$(PY) tools/protect_tests.py

spec-check:
	$(PY) tools/spec_check.py

context-check:
	$(PY) tools/context_check.py

billing-demo:
	$(PY) tools/e2e_billing.py

review-flags:
	$(PY) tools/review_flags.py $(if $(BASE),--base $(BASE),) $(if $(DIFF),--diff $(DIFF),)

clean:
	rm -rf out legacy/billing/build services/orders/.pytest_cache
