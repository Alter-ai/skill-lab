---
name: oss-release-readiness
description: Use before making a private repo public, open-sourcing a project, or pushing it to a public GitHub remote. Checks HEAD and all history for forbidden strings, author emails, secrets, sensitive files, notebook outputs, large files, missing LICENSE/README/SECURITY and third-party attribution.
---

# OSS Release Readiness

Publishing exposes the whole history, not just the latest files. A string removed in a later commit is still public. Check both.

## Steps

1. **Scripted check.** Run it on the repo; each `--forbid` value is a string that must not appear anywhere (personal email, home path, real name, internal host). Use the `=` form so a value starting with `-` is not read as an option. Each spelling needs its own `--forbid=` (a Windows path as backslash, forward slash and `/c/...` are three values). Under Git Bash set `MSYS2_ARG_CONV_EXCL='*'` first, or run from PowerShell, because Git Bash rewrites backslash paths. A bare user name can false-positive on third-party names; prefer the longer form.

   `python -I scripts/release_check.py <repo> --forbid=<text> --forbid=<text>`

   Exit 0 clean, 1 findings, 2 not a git repo, no commits, bad usage or a git failure. Findings: `forbid[n] content|history|commit-message|author-email|ref|tag|path-head|path-history` (n is the index of the `--forbid` value; the value itself is never printed; `content ... binary` means a binary file matches; `author-email` covers author and committer name and email), `shallow-clone` (history is partial; fetch it in full and rerun), `sensitive-path` (`.env.example`, `.env.sample` and `.env.template` are not flagged), `notebook-output`, `notebook-unreadable`, `large-file`, `missing`, `attribution`.
2. **Secret scan.** Run `gitleaks git <repo>` over the full history. Treat any hit as leaked: rotate the credential, do not just delete it.
3. **Manual review.** Read third-party licences and each `SOURCE.md` (upstream commit SHA, modifications). Read README, SECURITY.md and docs for private names, internal URLs and anything the owner would not post publicly.
4. **Back up.** Before any rewrite make a full mirror: `git clone --mirror <repo> <backup>.git`. Keep it private and outside the repo.
5. **Rewrite history (owner only).** By rule, the owner runs the rewrite in their own terminal, on a fresh clone. The tier hook does not list `git filter-repo`, so nothing technical stops an agent: do not run it from a Claude session. Use `git filter-repo` on a fresh clone: `--mailmap <file>` maps old author and committer identities to a public one, `--replace-text <file>` replaces forbidden strings in file contents with placeholders (`old==>new` per line), and `--replace-message <file>` does the same for commit messages (`--replace-text` does not touch them). Annotated tags and tagger emails need their own handling: delete and recreate the tags after the rewrite. List every spelling of a Windows path as a separate rule: backslash, forward slash, the `/c/...` form and the JSON-escaped form (`\`). `--replace-text` skips blobs with a NUL byte in the first 8 KB, so tracked binaries such as `.pyc` keep their strings: remove those paths with `--invert-paths --path-glob '<glob>'` and rerun the check. Remove sensitive paths the same way (`--path <path> --invert-paths`). Rewriting changes every commit hash, so tags and open work must be redone.
6. **Re-check.** Run steps 1 and 2 again on the rewritten repo. It must exit 0 before going on.
7. **Owner decision.** The owner confirms the findings are resolved and makes the repo public. Do not change visibility or push to a public remote on their behalf.

## Limits

- The check matches text case-insensitively, in text and binary files at HEAD (binary matches are reported as `binary`), in diffs across history, commit messages, annotated tags and file names. Encoded or obfuscated secrets are not found.
- Author and committer names and emails, ref names and annotated tags (message and tagger) are scanned.
- On exit 2 git's own error message is printed (truncated) and may contain a path; do not paste it into a public place without reading it.
- A bare or mirror clone returns 2; scan a normal clone.
- A directory nested inside another git repo scans that outer repo.
- `attribution` only checks that `skills/*/` with a `LICENSE` has a `SOURCE.md` with a 40-character upstream SHA; whether the licence permits redistribution is a human call.
