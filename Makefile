# OrderHub Brownfield: common tasks. Run `make help` for the list.
# Windows: use WSL. Without make, run the commands shown under each target.

PY ?= .venv/bin/python
ifeq ($(OS),Windows_NT)
PY = .venv/Scripts/python
endif

.PHONY: help setup doctor test test-py test-tools test-java lint billing-demo clean

help:
	@echo "setup         create .venv and install pinned dependencies"
	@echo "doctor        check this machine can run the labs"
	@echo "test          run all tests (Python service and legacy Java self-test)"
	@echo "test-py       Python tests only"
	@echo "test-tools    tests for the course tools"
	@echo "test-java     legacy billing build and self-test only"
	@echo "lint          ruff lint for the Python service"
	@echo "billing-demo  place orders, write the CSV handoff, run the legacy nightly batch"

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

billing-demo:
	$(PY) tools/e2e_billing.py

clean:
	rm -rf out legacy/billing/build services/orders/.pytest_cache
