import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from review_flags import flag, lock_packages, main, parse_diff, render  # noqa: E402

PRS = ROOT / "labs" / "s06" / "prs"
LOCK = (ROOT / "requirements.lock").read_text()


def names(results):
    return [f[0] for f in results]


def diff(path, removed=(), added=(), new=False):
    old = "/dev/null" if new else f"a/{path}"
    body = "".join(f"-{r}\n" for r in removed) + "".join(f"+{a}\n" for a in added)
    return f"diff --git a/{path} b/{path}\n--- {old}\n+++ b/{path}\n@@ -1 +1 @@\n{body}"


def test_parse_diff_tracks_new_files_and_lines():
    files = parse_diff(diff("x.py", ["a"], ["b", "c"]) + diff("y.py", added=["z"], new=True))
    assert [(f.path, f.is_new, f.added, f.removed) for f in files] == [
        ("x.py", False, ["b", "c"], ["a"]), ("y.py", True, ["z"], [])]


def test_deleted_check_in_domain_code_is_flagged_but_a_moved_line_is_not():
    d = diff("services/orders/orderhub/orders.py", ["    if order.status == SHIPPED:", "        raise Conflict('x')"])
    assert names(flag(d, LOCK)) == ["DELETED-CHECK", "DELETED-CHECK"]
    moved = diff("services/orders/orderhub/orders.py", ["    raise Conflict('x')"], ["    raise Conflict('x')"])
    assert flag(moved, LOCK) == []


def test_deleted_check_outside_domain_code_is_not_flagged():
    assert flag(diff("tools/doctor.py", ["    if x:"]), LOCK) == []


def test_removed_bound_is_flagged():
    d = diff("services/orders/orderhub/api.py",
             ["        return f(limit=min(limit, 200))"], ["        return f(limit=limit)"])
    assert names(flag(d, LOCK)) == ["DELETED-CHECK"]


def test_changed_existing_test_is_flagged_new_test_file_is_not():
    assert names(flag(diff("services/orders/tests/test_a.py", ["    assert x == 1"], ["    assert x == 2"]), LOCK)) \
        == ["TEST-CHANGE"]
    assert flag(diff("services/orders/tests/test_b.py", added=["    assert y"], new=True), LOCK) == []


def test_mock_in_test_ignores_client_patch():
    d = diff("services/orders/tests/test_c.py", added=["    monkeypatch.setattr(notify, 'x', f)",
                                                         "    client.patch('/customers/1', json={})"], new=True)
    assert names(flag(d, LOCK)) == ["MOCK-IN-TEST"]


def test_phantom_import_is_flagged_and_known_imports_are_not():
    d = diff("services/orders/orderhub/x.py", added=["import yaml", "import json", "import httpx",
                                                      "from sqlalchemy import select", "from . import orders"])
    assert flag(d, LOCK) == [("NEW-IMPORT", "services/orders/orderhub/x.py", "yaml is not in requirements.lock")]


def test_duplicate_http_client_is_flagged():
    results = flag(diff("requirements.lock", added=["requests==2.32.5"]), LOCK)
    assert names(results) == ["DEPENDENCY", "DUPLICATE-DEP"]
    assert "httpx" in results[1][2]


def test_out_of_scope_and_size():
    d = diff("services/orders/orderhub/customers.py", added=["x = 1"] * 301)
    assert names(flag(d, LOCK, files=["services/orders/orderhub/orders.py"])) == ["SIZE", "OUT-OF-SCOPE"]


def test_lab_prs_flag_what_a_tool_can_see():
    def run(name):
        return set(names(flag((PRS / name).read_text(), LOCK)))
    assert run("R4.diff") == {"DELETED-CHECK"}
    assert run("R5.diff") == {"MOCK-IN-TEST", "DEPENDENCY", "DUPLICATE-DEP"}
    assert run("R8.diff") == {"API-SURFACE"}
    assert {"DELETED-CHECK", "TEST-CHANGE", "SIZE"} <= run("R3.diff")


def test_render_collapses_long_runs():
    results = [("TEST-CHANGE", "t.py", str(i)) for i in range(6)]
    assert render(results) == ["TEST-CHANGE   t.py: 0", "TEST-CHANGE   t.py: 1", "TEST-CHANGE   t.py: 2",
                               "TEST-CHANGE   t.py: ... and 3 more"]


def test_lock_packages_normalises_names():
    assert lock_packages("SQLAlchemy==2.1.3\ntyping_extensions==4\n# c\n") == {"sqlalchemy", "typing-extensions"}


def test_unknown_base_ref_is_an_error_not_zero_flags(capsys):
    assert main(["--base", "no-such-branch-anywhere"]) == 2
    assert "unknown ref 'no-such-branch-anywhere'" in capsys.readouterr().out
