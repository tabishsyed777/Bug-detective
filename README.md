# Bug-detective

Reproduce a percentage-calculation bug, diagnose it, propose an arithmetic fix, and verify four regression cases. Failed candidates receive feedback, up to two attempts. Restricted AST evaluation does not execute generated code. This version supports the bundled calculator, not arbitrary repositories.

Requires Python 3.10+. No third-party dependencies.

```bash
python bug_detective.py
python -m unittest discover -s tests -v
```

Default mode uses scripted demo responses, not live AI. Reports and decision traces are saved under `work/`.

For live AI, set `OPENAI_API_KEY` in your environment, optionally `OPENAI_MODEL` (default `gpt-4.1-mini`), then run:

```bash
python bug_detective.py --live
```

Live mode sends supplied code/evidence to OpenAI and incurs API usage. Live API calls have not been verified with credentials. Errors stop the run; there is no silent demo fallback. Never commit credentials. Use `--out` to choose the report directory.

Tests and CI cover the bundled workflow and invalid inputs. Earlier user-specific test steps were unavailable and remain pending.
