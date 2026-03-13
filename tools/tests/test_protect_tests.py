import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from protect_tests import find_test_edits  # noqa: E402

TAMPERED = """diff --git a/services/orders/tests/test_returns_acceptance.py
--- a/services/orders/tests/test_returns_acceptance.py
+++ b/services/orders/tests/test_returns_acceptance.py
@@ -30 +30 @@ def test_ac2_discount_share_is_allocated_by_value(client):
-    assert ret(client, order["id"], [{"sku": "STAND-LAP", "quantity": 1}]).json()["refund_minor"] == 4095
+    assert ret(client, order["id"], [{"sku": "STAND-LAP", "quantity": 1}]).json()["refund_minor"] == 4550
"""

NEW_FILE = """diff --git a/services/orders/tests/test_new.py b/services/orders/tests/test_new.py
new file mode 100644
--- /dev/null
+++ b/services/orders/tests/test_new.py
@@ -0,0 +1,2 @@
+def test_x():
+    assert True
"""

ADDITION_ONLY = """--- a/tools/tests/test_x.py
+++ b/tools/tests/test_x.py
@@ -10,0 +11,2 @@
+def test_more():
+    assert 1
"""


def test_changed_assertion_is_reported():
    assert find_test_edits(TAMPERED) == [
        (
            "services/orders/tests/test_returns_acceptance.py",
            '    assert ret(client, order["id"], [{"sku": "STAND-LAP", "quantity": 1}]).json()["refund_minor"] == 4095',
        ),
    ]


def test_new_test_files_and_pure_additions_are_fine():
    assert find_test_edits(NEW_FILE) == []
    assert find_test_edits(ADDITION_ONLY) == []


def test_deleted_test_lines_are_reported_and_blank_lines_ignored():
    diff = (
        "--- a/legacy/billing/test/X.java\n+++ b/legacy/billing/test/X.java\n@@ -3,2 +2,0 @@\n-        check(a);\n-\n"
    )
    assert find_test_edits(diff) == [("legacy/billing/test/X.java", "        check(a);")]


def test_several_files_keep_their_own_names():
    diff = TAMPERED + "--- a/tools/tests/test_y.py\n+++ b/tools/tests/test_y.py\n@@ -1 +0,0 @@\n-assert 2\n"
    assert [f for f, _ in find_test_edits(diff)] == [
        "services/orders/tests/test_returns_acceptance.py",
        "tools/tests/test_y.py",
    ]
