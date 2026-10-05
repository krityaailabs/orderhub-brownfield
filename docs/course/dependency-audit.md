# Dependency audit worksheet (Lecture 7.4)

Three questions for every package an agent (or a person) adds. Answer from the package's real page and repository, not from the agent's summary. `make security` checks pins, recorded decisions and duplicates; it can't answer these.

| Question | How to check |
|---|---|
| **Exists, and is the one we mean?** | Search the official index (pypi.org) for the exact name. Check the project links point to the expected repository and organisation. Watch for look-alike names (hyphen vs underscore, a missing letter, an extra suffix). A name that doesn't exist is a red flag twice: the agent invented it, and anyone could register it. |
| **Maintained?** | Recent releases; open security issues and how fast they're answered; more than one maintainer; a security policy. |
| **Needed?** | What exactly does it do that the standard library or an existing dependency can't? How many lines would it save? ADR 0002 asks for this in `docs/dependencies.md`. |

## Exercise: three suggestions an agent made for OrderHub

Checked on 5 October 2026. Re-check on the day: the answers can change, which is the point.

| Suggested for | Package | Exists? | Maintained? | Needed? | Decision |
|---|---|---|---|---|---|
| Return-window date arithmetic | `python-dateutil` | | | | |
| Calling the warehouse webhook | `requests` | | | | |
| Storing money as integer minor units in SQLAlchemy | `sqlalchemy-minor-units` | | | | |
