# Lab s02 hints (open one level at a time)

## find_instruction_files
1. Walk the tree with the `_walk` helper; it already skips `.venv`, `.git` and build folders.
2. Match on the file name for AGENTS.md, CLAUDE.md and CLAUDE.local.md; match on the relative path for the `.github` and `.cursor` files.
3. Return `sorted(...)` of `path.relative_to(root).as_posix()` values.

## claude_code_loads
1. Use `_ancestors(root, cwd)`. First decide whether any of CLAUDE.md, .claude/CLAUDE.md or CLAUDE.local.md exists in those directories.
2. AGENTS.md is "on" in the default mode only when none exist; in `claude-md-and-agents-md` it is always on; in `claude-md` never.
3. Add files in this order per directory: the CLAUDE files (expanding `@` imports with `_imports`), then AGENTS.md if on. For `opened`, walk the directories between cwd and the file's folder.

## copilot_loads and cursor_loads
1. Start from the docstring's table; github-chat returns early.
2. `_frontmatter` and `_matches` already handle `applyTo`, `globs` and `alwaysApply`.
3. Nested AGENTS.md: root first, then each directory down to the file's folder.

## check_required_sections, check_commands, check_no_secrets
1. Use `re.finditer(r"^##\s+(.+)$", text, flags=re.M)` for headings; compare lower-case prefixes.
2. Only commands inside backticks count: prose like "make it pass" is not a command.
3. Loop over lines with `enumerate(..., start=1)`; stop at the first pattern that matches a line.
