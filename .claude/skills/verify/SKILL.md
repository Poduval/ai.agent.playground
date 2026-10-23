---
name: verify
description: Run the project's offline tests and lint and report results honestly. Use after any code change, before claiming work is done.
---
1. `cd` into the project folder (`services/` or `agents/<name>/`; run all that changed); tests must run offline.
2. Run `make test` then `make lint`. If `.venv` is missing, `make install` first.
3. Report exact pass/fail counts and any failing output. Never claim success on failure or on unrun checks; say what was skipped.
4. Note the real-LLM path is untested by the suite (fake LLM only).
5. If docs, modules, ports or env vars changed, confirm README, CLAUDE.md and `.env.example` were updated. Consider the `layer-reviewer` subagent for a convention review.
