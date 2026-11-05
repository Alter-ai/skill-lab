# OpenSSF Scorecard estimate

Estimate for `Alter-ai/skill-lab` as a one-person repo with the files added in the public-release change. Nothing was run against the real Scorecard tool, since the repo is not public yet. Check list, risk levels and rules are from https://github.com/ossf/scorecard/blob/main/docs/checks.md (read 2026-11-09): 20 checks.

Overall score = weighted mean of the checks that return a score. Weights by risk: Critical 10, High 7.5, Medium 5, Low 2.5 (the weights are the tool's documented scheme, not stated on the checks page). The checks page does not say how Packaging, Signed-Releases and Webhooks score when there is nothing to inspect, so this estimate models Packaging and Signed-Releases as 0 and Webhooks as 10 (no webhooks exist). The real tool may mark them inconclusive instead, which would change the mean slightly.

| # | Check | Risk | Day 1 | Why |
|---|---|---|---|---|
| 1 | Binary-Artifacts | High | 10 | No binaries tracked; `*.pyc` is ignored. |
| 2 | Branch-Protection | High | 0 | Not configured. Without an admin token only non-admin settings are read. A rule against force-push and deletion would give some points (about 3); required reviews do not work for a solo owner. |
| 3 | CI-Tests | Low | 1 | Looks for CheckRuns or Statuses (for example github-actions) on the ~30 most recent commits. On day 1 only the newest commit(s) have a run, so close to 0. Rises toward 10 as most recent commits get a passing `test.yml` run. |
| 4 | CII-Best-Practices | Low | 0 | No OpenSSF Best Practices badge (in progress 2, passing 5). |
| 5 | Code-Review | High | 0 | Solo repo: commits are not approved by anyone else. Expected deduction. |
| 6 | Contributors | Low | 0 | Needs 3 companies with 5 commits each in the last 30. Not achievable. |
| 7 | Dangerous-Workflow | Critical | 10 | `test.yml` has no `pull_request_target` and no untrusted input in `run:`. |
| 8 | Dependency-Update-Tool | High | 10 | `.github/dependabot.yml` is present. |
| 9 | Fuzzing | Medium | 0 | No fuzzing; not worth it here. |
| 10 | License | Low | 10 | Plain MIT `LICENSE` at the root. |
| 11 | Maintained | High | 0 | Only succeeds if the repo is more than 90 days old; full score needs at least one commit per week for the previous 90 days. |
| 12 | Packaging | Medium | 0 | Nothing is published as a package. |
| 13 | Pinned-Dependencies | Medium | 8 | Actions pinned by SHA; `pip install matplotlib` is unpinned and without hashes, a small deduction. |
| 14 | SAST | Medium | 0 | No CodeQL or similar. A CodeQL workflow would score. |
| 15 | SBOM | Medium | 0 | No SBOM in the source or release. A file in the source gives 5 of 10. |
| 16 | Security-Policy | Medium | 10 | `SECURITY.md` has a contact email, free text and the word vulnerability more than twice. |
| 17 | Signed-Releases | High | 0 | No releases. |
| 18 | Token-Permissions | High | 10 | `permissions: contents: read` at the top of `test.yml`. |
| 19 | Vulnerabilities | High | 10 | No dependencies in the repo. |
| 20 | Webhooks | Critical | 10 | No webhooks (needs an admin token to read, so it may be inconclusive). |

## Estimate

- Day 1: about **5.1 / 10**.
- After 90 days with a commit every week and `test.yml` passing on recent commits (Maintained and CI-Tests reach 10): about **6.0**.
- Plus a CodeQL workflow and a force-push/deletion rule on `master`: about **6.6**. Plus an SBOM file in the source: about 6.8.
- The rest needs other people (Code-Review, Contributors) or releases and are not realistic targets.

**Target score for the spec (D10): 6.0 by day 90 with no extra work; 6.5 as a stretch with CodeQL and a branch rule. At least 5 at launch.**
