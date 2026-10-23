# Agent Instructions

Guidance for any AI coding agent in this repo (Claude Code reads it via CLAUDE.md).

- Repo = independent teaching projects: `services/` and one folder per agent in `agents/<name>/`. Work inside one project at a time; never import across projects. Read that project's README and CLAUDE.md first.
- Teaching template: keep code short, readable, and commented where a learner would ask "why". No speculative abstraction.
- Config only through the project's settings module; document new env vars in its `.env.example` and README.
- Never commit or print secrets; don't read `.env`.
- Tests must run offline. Run the project's `make test` and `make lint` after changes and report results honestly.
- Update docs when behavior, modules or ports change.
- Log changes in RELEASE.md with each major commit (changes only).
- Don't commit or push unless asked.
