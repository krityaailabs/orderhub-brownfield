# Lab s07 troubleshooting

**The scanner reports dozens of findings in files I didn't write.** Read each one. In this repository they are test fixtures, a recorded diff and a labelled example, plus one real problem. Triage, don't silence: fix real ones; mark fixtures narrowly (inline marker or one ignore glob) with a reason.

**`/sandbox` says dependencies are missing.** On Linux and WSL2 the sandbox needs `bubblewrap` and `socat`. On native Windows there is no sandbox; use WSL2. The permission check reports a missing sandbox as a warning only.

**My agent can't run `make setup` any more.** Correct: it needs the network and installs packages, both denied. Run setup yourself; that's the point.

**The agent asks before every commit.** That's the `ask` list. If you want fewer prompts, move `git add` to `allow`, but keep `git commit` and `git push` where they are.

**The commit hook passes but CI's gate fails.** The hook scans staged files; the gate scans every tracked file and checks the profile, dependencies and canary too. Run `make security` locally before pushing.

**ruff S-rules flag subprocess calls in my own tools.** S603/S607 are known false positives for fixed argument lists; the gate ignores them for `tools/`. Don't add a new subprocess call that builds its arguments from untrusted text.
