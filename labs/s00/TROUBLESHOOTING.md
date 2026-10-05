# Troubleshooting: Section 0

| Symptom | Likely cause | Fix |
|---|---|---|
| `make: command not found` (Windows) | No make outside WSL | Use WSL, or run the command shown under each target in the Makefile |
| `python3 -m venv` fails on Debian or Ubuntu | The venv package is missing | `sudo apt install python3-venv`, then `make setup` again |
| `javac: command not found` but `java` works | Only a runtime (JRE) is installed | Install a JDK 11 or newer (for example Eclipse Temurin) and check `javac -version` |
| `make doctor` says a package is missing | Dependencies installed into a different Python | Delete `.venv`, run `make setup`, and use `.venv/bin/python` |
| `run_batch.sh: Permission denied` | The execute bit was lost (for example on a Windows checkout) | `chmod +x legacy/billing/*.sh`, or run `git config core.autocrlf input` and check out again |
