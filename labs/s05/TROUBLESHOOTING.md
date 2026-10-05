# Troubleshooting: Lab s05

| Symptom | Likely cause | Fix |
|---|---|---|
| AC-1 shows stock 225 | The Q12 bug: a second cancel restores stock again | Make cancelling a cancelled order a no-op |
| AC-2 responses differ (`refunded_minor` or timestamps) | Response rebuilt on the second call instead of replayed | Return the stored response for a repeated key |
| AC-4: the key can't be reused after a 409 | Failed outcomes stored | Store only 2xx outcomes |
| `git worktree add` fails: branch already checked out | The branch is checked out in another worktree | Use a new branch name with `-b` |
| The pre-commit hook doesn't run | Not installed, or not executable | `make install-hooks`; check `.git/hooks/pre-commit` |
| The Claude Code hook doesn't run | Older version, or project settings not trusted | Check `/hooks` in the session and the hooks documentation |
