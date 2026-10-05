"""Issue-to-pull-request pipeline for unattended agents (Section 9, Project 3).

A small, readable stand-in for what a CI system plus a cloud agent does, so every guardrail can be
seen and tested locally: kill switch, rate limits, deduplication, scope, budgets, required checks,
a human merge gate and a tamper-evident audit log. The agent itself is any command: a real
headless agent (`claude --bare -p ...`) or the deterministic `fake_agent.py` used in tests.
"""
