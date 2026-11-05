# Security Policy

## Reporting a vulnerability

Email **lericai0705@gmail.com** with the subject `skill-lab security`. Please do not open a public issue for a vulnerability.

Include what you found, the file or command involved, and steps to reproduce.

## What to expect

This is a one-person project. I aim to acknowledge a report within 7 days and to say whether I will fix it within 30 days. There is no bug bounty and no formal SLA.

## Scope

In scope: `tools/gate.py` and the scripts under `skills/*/scripts/`. These run on your machine and read your repo.

Out of scope: the third-party skills under `skills/` that carry a `SOURCE.md` (report those upstream), and the fact that the tier gate only applies to Claude Code sessions (documented in the README).
