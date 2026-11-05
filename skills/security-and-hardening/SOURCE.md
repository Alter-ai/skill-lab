# Source

- Upstream: https://github.com/addyosmani/agent-skills/tree/301b02b12bff98e4688e6984af6556802322bbde/skills/security-and-hardening
- License: MIT (see LICENSE)
- Copied: 2026-11-05; includes `references/hardening-patterns.md`

## Local modifications

- SKILL.md: removed the pointers to `../../references/security-checklist.md` (Destructive operations, Dependencies); `Before sign-off, walk `../../references/security-checklist.md`: it covers` -> `Before sign-off, walk these areas:`, and dropped `plus the OWASP quick-reference tables`.
- SKILL.md: removed `(the observability-and-instrumentation skill makes the same point from the ops side)`; `run the postmortem with the debugging-and-error-recovery skill` -> `run a postmortem`.
- references/hardening-patterns.md: removed the shared-checklists intro sentence, the OWASP 2021 ordering sentence, and the `Worked example in ../../../references/security-checklist.md` sentence (file not imported).
