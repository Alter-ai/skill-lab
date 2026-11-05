# OpenSSF Scorecard estimate

Estimate for `Alter-ai/skill-lab` as a one-person repo with the files added in the public-release change. Nothing was run against the real Scorecard tool, since the repo is not public yet. The check list, weights and rules are from memory of the Scorecard docs (not re-read online), so check them against https://github.com/ossf/scorecard before relying on the numbers.

Overall score = weighted mean of the checks that return a score. A check that is inconclusive (-1) is left out. Weights: Critical 10, High 7.5, Medium 5, Low 2.5.

| # | Check | Weight | Day 1 | Why |
|---|---|---|---|---|
| 1 | Binary-Artifacts | High | 10 | No binaries tracked; `__pycache__` and `*.pyc` are ignored. |
| 2 | Branch-Protection | High | 0 | Not configured. Scorecard without an admin token only sees limited settings. A rule that blocks force-push and deletion gives some points; a required-review rule gives more but the owner cannot approve their own PR. Reachable: about 3. |
| 3 | CI-Tests | Medium | -1 | Looks at merged PRs with CI results. Direct pushes mean no PRs, so no score. Becomes 10 once changes go through PRs that pass `test.yml`. |
| 4 | CII-Best-Practices | Low | 0 | No OpenSSF Best Practices badge. A "passing" badge is possible later but costs a questionnaire. |
| 5 | Code-Review | High | 0 | Solo repo: nobody else approves. This is the expected deduction. |
| 6 | Contributors | Medium | 0 | Wants contributors from at least 3 organizations. |
| 7 | Dangerous-Workflow | Critical | 10 | `test.yml` has no `pull_request_target`, no untrusted input in `run:`. |
| 8 | Dependency-Update-Tool | Medium | 10 | `.github/dependabot.yml` updates `github-actions`. |
| 9 | Fuzzing | Medium | 0 | No fuzzing; not worth it for this repo. |
| 10 | License | Low | 10 | MIT `LICENSE` at the root. |
| 11 | Maintained | High | 0 | Needs the repo to be at least 90 days old and active in the last 90 days. Cannot pass on day 1. Becomes 10 if there are commits in a 90-day window. |
| 12 | Packaging | Medium | -1 | No package is published; not applicable. |
| 13 | Pinned-Dependencies | Medium | 8 | Actions pinned by 40-character SHA. `pip install matplotlib` is unpinned and has no hashes, which costs a little. |
| 14 | SAST | Medium | 0 | No CodeQL or similar. Adding a CodeQL workflow gives up to 10, based on the share of PR commits it analyzes. |
| 15 | Security-Policy | Medium | 10 | `SECURITY.md` with a reporting contact. |
| 16 | Signed-Releases | High | -1 | No releases. Stays out until the first release; then 0 unless releases ship signatures or provenance. |
| 17 | Token-Permissions | High | 10 | `permissions: contents: read` at the top of `test.yml`. |
| 18 | Vulnerabilities | High | 10 | No dependencies in the repo, so OSV lists nothing. |
| 19 | Webhooks | Medium | -1 | Needs an admin token to read webhook settings; no webhooks anyway. |

## Estimate

- Day 1: about **5.4 / 10**. The zeros are Branch-Protection, CII, Code-Review, Contributors, Fuzzing, Maintained and SAST.
- After 90 days of activity, with changes made through PRs that pass CI: Maintained and CI-Tests reach 10, giving about **6.5**.
- Adding a CodeQL workflow and a force-push rule on `master` gives about **7.2**. Beyond that the remaining points need other people (Code-Review, Contributors), so they are not realistic targets.

**Target score for the spec (D10): 6.5 by day 90, 5 or more at launch.** Stretch: 7.
