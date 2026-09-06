---
name: audiolab-software-engineer
description: Implement, debug, refactor, review, and test AudioLab Editor code in Python, CustomTkinter, FFmpeg, yt-dlp, Demucs, faster-whisper, edge-tts, and PyInstaller. Use for feature development, bug fixes, code quality, automated tests, concurrency, subprocess handling, or maintainability work in this repository.
---

# AudioLab Software Engineer

## Workflow

1. Read `README.md`, `pyproject.toml`, the affected code, and relevant tests.
2. Check `git status` and preserve unrelated user changes.
3. Trace behavior across `presentation`, `application`, `domain`, and `infrastructure` before editing.
4. Define observable behavior and failure cases.
5. Implement the smallest cohesive change. Keep UI operations on the Tk main thread and long-running work off it.
6. Pass external processes as argument lists with `shell=False`; validate URLs, paths, formats, and output destinations.
7. Add or update tests at the closest stable boundary. Mock expensive AI, network, GUI, and external-binary operations.
8. Run Ruff, targeted tests, the full test suite, and `compileall` when the environment supports them.
9. Report changed behavior, verification evidence, and remaining platform or manual tests.

## Engineering rules

- Keep domain types free of UI, filesystem, subprocess, and vendor imports.
- Inject infrastructure behind ports when practical; do not increase existing layer coupling.
- Use `Path` and the existing runtime-path abstractions for cross-platform paths.
- Treat cancellation, partial output, timeouts, missing binaries, network loss, and permission errors as normal cases.
- Never claim a test passed when its dependency or runtime was unavailable.
- Update documentation when behavior, dependencies, installation, or packaging changes.

## Quality gate

Require lint, unit tests, compilation, explicit security review for subprocess/path changes, and manual GUI validation for visible behavior. Follow `TESTING_PROTOCOL.md` without treating stale status statements as evidence.
