---
name: release-entry
description: Add an entry to RELEASE.md for a major commit. Use when finishing a major change or when asked to log/update the release notes.
---
RELEASE.md lists changes only, newest first, no rationale.

1. Get the hash and date: `git log -1 --format='%h — %cs'` (for an uncommitted change, ask the user whether to wait for the commit hash).
2. Insert below the intro, above the previous entry: `## <hash> — <YYYY-MM-DD>` then terse past-tense bullets (`- Added …`, `- Renamed …`, `- Removed …`).
3. Base bullets on `git diff` / `git log`, not memory. No secrets. Don't commit or push unless asked.
