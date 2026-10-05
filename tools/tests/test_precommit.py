import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from precommit import select_checks  # noqa: E402


def test_python_service_change():
    assert select_checks(["services/orders/orderhub/pricing.py"]) == ["lint", "python-tests"]


def test_orders_module_also_runs_the_billing_demo():
    assert select_checks(["services/orders/orderhub/orders.py"]) == ["lint", "python-tests", "billing-demo"]


def test_test_file_change_runs_the_guard():
    assert select_checks(["services/orders/tests/test_orders.py"]) == ["lint", "python-tests", "protect-tests"]


def test_legacy_java_change():
    assert select_checks(["legacy/billing/src/com/orderhub/billing/InvoiceCalculator.java"]) == [
        "java", "billing-demo"]
    assert select_checks(["legacy/billing/test/com/orderhub/billing/BillingSelfTest.java"]) == [
        "java", "billing-demo", "protect-tests"]


def test_context_and_spec_files():
    assert select_checks(["AGENTS.md"]) == ["context"]
    assert select_checks(["legacy/billing/AGENTS.md"]) == ["java", "billing-demo", "context"]
    assert select_checks([".github/copilot-instructions.md"]) == ["context"]
    assert select_checks(["docs/specs/returns.md"]) == ["specs"]


def test_tools_change_runs_tool_tests_and_lint():
    assert select_checks(["tools/mutate.py", "tools/tests/test_precommit.py"]) == [
        "lint", "tool-tests", "protect-tests"]


def test_unrelated_files_need_nothing_and_order_is_stable():
    assert select_checks(["README.md", "docs/adr/0001-money-in-integer-minor-units.md"]) == []
    many = ["docs/specs/a.md", "AGENTS.md", "legacy/billing/build.sh", "services/orders/orderhub/api.py"]
    assert select_checks(many) == ["lint", "python-tests", "java", "billing-demo", "context", "specs"]
