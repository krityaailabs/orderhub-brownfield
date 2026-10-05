# Exercise 1.1: place these on the autonomy ladder

| Level | Name | Behaviour |
|---|---|---|
| L0 | Complete | Inline completion of the current line or block |
| L1 | Suggest | Chat proposes code; you apply it |
| L2 | Supervised agent | Edits files and runs commands, asking before each |
| L3 | Bounded agent | Acts freely inside a sandbox, branch or worktree, gated by tests |
| L4 | Background agent | Works asynchronously and opens a pull request |
| L5 | Agent fleet | Scheduled or parallel agents handle classes of work |

For each item, give the level and one control you'd want in place:

1. Tab completion in your editor
2. Pasting a stack trace into a chat panel and copying the suggested fix
3. A terminal agent that asks before every file edit and command
4. The same terminal agent with edits auto-accepted, inside a git worktree, told to stop when the tests pass
5. Assigning a GitHub issue to a cloud agent that opens a pull request
6. A nightly job where an agent bumps dependencies in every repository of your organisation
