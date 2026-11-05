---
name: oss-release-readiness
description: Use before making a private repo public, open-sourcing a project, or pushing it to a public GitHub remote. Checks HEAD and all history for forbidden strings, author emails, secrets, sensitive files, notebook outputs, large files, missing LICENSE/README/SECURITY and third-party attribution.
---

# OSS Release Readiness

Publishing exposes the whole history, not just the latest files. A string removed in a later commit is still public. Check both.

## Steps

1. **Scripted check.** Run it on the repo; each `--forbid` value is a string that must not appear anywhere (personal email, home path, real name, internal host). Use the `=` form so a value starting with `-` is not read as an option.

   `python -I scripts/release_check.py <repo> --forbid=<text> --forbid=<text>`

   Exit 0 clean, 1 findings, 2 not a git repo or no commits. Findings: `forbid[n] content|history|commit-message|author-email|tag|path-head|path-history` (n is the index of the `--forbid` value; the value itself is never printed; `content ... binary` means a binary file matches), `sensitive-path`, `notebook-output`, `notebook-unreadable`, `large-file`, `missing`, `attribution`.
2. **Secret scan.** Run `gitleaks git <repo>` over the full history. Treat any hit as leaked: rotate the credential, do not just delete it.
3. **Manual review.** Read third-party licences and each `SOURCE.md` (upstream commit SHA, modifications). Read README, SECURITY.md and docs for private names, internal URLs and anything the owner would not post publicly.
4. **Back up.** Before any rewrite make a full mirror: `git clone --mirror <repo> <backup>.git`. Keep it private and outside the repo.
5. **Rewrite history (owner only).** Warning: history rewriting is blocked by the hook, so the owner runs it in their own terminal. Do not try to run it from a Claude session or work around the hook. Use `git filter-repo` on a fresh clone: `--mailmap <file>` maps old author and committer identities to a public one, `--replace-text <file>` replaces forbidden strings in file contents with placeholders (`old==>new` per line), and `--replace-message <file>` does the same for commit messages (`--replace-text` does not touch them). Annotated tags and tagger emails need their own handling: delete and recreate the tags after the rewrite. List every spelling of a Windows path as a separate rule: backslash, forward slash, the `/c/...` form and the JSON-escaped form (`\`). Remove sensitive paths with `--path <path> --invert-paths`. Rewriting changes every commit hash, so tags and open work must be redone.
6. **Re-check.** Run steps 1 and 2 again on the rewritten repo. It must exit 0 before going on.
7. **Owner decision.** The owner confirms the findings are resolved and makes the repo public. Do not change visibility or push to a public remote on their behalf.

## Limits

- The check matches text, case-insensitively, in non-binary files. Binary content, images and encoded secrets are not searched.
- `attribution` only checks that `skills/*/` with a `LICENSE` has a `SOURCE.md` with a 40-character upstream SHA; whether the licence permits redistribution is a human call.
