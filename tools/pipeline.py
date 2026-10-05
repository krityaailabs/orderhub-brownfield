"""Command line for the issue-to-PR pipeline (Section 9). See tools/agent_pipeline/pipeline.py.

Usage:
  python tools/pipeline.py run ISSUE.md -- AGENT_COMMAND...     run the agent on one issue
  python tools/pipeline.py run --config ci/jobs/JOB.json ISSUE.md -- COMMAND...   with a job's own limits
  python tools/pipeline.py approve PR-1 --by "Your Name"        the human merge gate
  python tools/pipeline.py reject PR-1 --by NAME --reason TEXT
  python tools/pipeline.py status                               PRs and the last audit events
  python tools/pipeline.py verify-audit                         check the audit hash chain
  python tools/pipeline.py stop | resume                        create or remove the kill switch
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from agent_pipeline import pipeline  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    overrides = {}
    if "--config" in args:
        i = args.index("--config")
        overrides = json.loads((ROOT / args[i + 1]).read_text())
        args = args[:i] + args[i + 2:]
    config = pipeline.load_config(ROOT, overrides)
    if not args:
        print(__doc__)
        return 2
    command = args[0]
    if command == "run" and "--" in args:
        split = args.index("--")
        result = pipeline.run(ROOT, Path(args[1]), args[split + 1:], config)
    elif command == "approve":
        by = args[args.index("--by") + 1] if "--by" in args else ""
        result = pipeline.approve(ROOT, args[1], by, config)
    elif command == "reject":
        result = pipeline.reject(ROOT, args[1], args[args.index("--by") + 1], args[args.index("--reason") + 1], config)
    elif command == "status":
        for pr in pipeline.prs(ROOT, config):
            print(f"{pr['id']:<6} {pr['issue']:<6} {pr['status']:<15} {pr['changed_lines']:>4} lines  {pr['files']}")
        for entry in pipeline.audit_entries(ROOT, config)[-5:]:
            print(f"  {entry['ts']}  {entry['event']:<16} {entry.get('issue') or entry.get('pr') or ''}")
        return 0
    elif command == "verify-audit":
        problems = pipeline.verify_audit(ROOT, config)
        print("\n".join(problems) or f"audit: {len(pipeline.audit_entries(ROOT, config))} entries, chain intact")
        return 1 if problems else 0
    elif command in ("stop", "resume"):
        switch = ROOT / config["kill_switch"]
        if command == "stop":
            switch.parent.mkdir(parents=True, exist_ok=True)
            switch.write_text("stopped by a person; delete this file (python tools/pipeline.py resume) to resume\n")
        elif switch.exists():
            switch.unlink()
        print(f"kill switch {'on' if switch.exists() else 'off'}: {config['kill_switch']}")
        return 0
    else:
        print(__doc__)
        return 2
    print(json.dumps(result, indent=2))
    success = {"run": "pr_opened", "approve": "approved", "reject": "rejected"}[command]
    return 0 if result["status"] == success else 1

if __name__ == "__main__":
    sys.exit(main())
