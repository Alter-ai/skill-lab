# web-visual-design evaluation, November 2026

## Method

Three briefs with different audiences (a, b, c). For each brief, one arm produced a design spec and a `tokens.json` with the skill loaded, and one arm produced the same without it. Both arms ran on Sonnet. Outputs were copied into blind folders (spec and tokens only, appendices excluded) and graded by a separate Opus reviewer who did not know which arm was which. The reviewer scored a rubric per output, said which output they would build from, and listed technical errors. Every `tokens.json` was also run through `palette_check`.

Round 1 used the first version of the skill. After fixes, round 2 reran only the with-skill arm on the same briefs, against the same baseline outputs, graded by a fresh Opus reviewer.

## Results

| | a | b | c | Would build from with-skill |
|---|---|---|---|---|
| Round 1 rubric (with-skill : baseline) | 7:1 | 6:3 | 7:2 | 3 of 3 |
| Round 2 rubric (with-skill : baseline) | 6:0 | 6:3 | 6:3 | 3 of 3 |

All six `tokens.json` in each round pass `palette_check`. The plan's pass condition (with-skill preferred and scoring higher on the rubric) was met in both rounds. Round 2 used a stricter reviewer on Chinese line height and weight reasons, so the totals are not directly comparable across rounds.

Spec length in words, with-skill: round 1 1001, 902, 1323; round 2 705, 824, 189. Baseline: 634, 458, 527.

## What improved from round 1 to round 2

- Length came under control (the longest spec dropped from 1323 to 824 words; the brief asked for one page).
- Object rules (tables, code blocks, badges and similar) are now present.
- Fewer technical errors. Round 1 had, for example, a font-stack trick that cannot be built as written and chroma limits wrongly attributed to contrast.

## Limits

- Convergence is still there. In round 2 the with-skill neutrals all sit at hue 160 to 200 with dark lightness .20 to .23, for three different audiences, with the same six token names and eleven pairs in the same order. Warm grey was replaced by teal, which is a new default. The baseline also converges (same blue links, grey and mono font), so part of this is a model tendency rather than the skill alone.
- The rubric rewards writing things down, so part of the score gap comes from the skill asking for explicit statements.
- Sample of 3 briefs, one run per arm per round.
- Nothing was rendered. Appearance, and whether a system-font choice looks right, could not be judged.
- No human saw any output.
- A pass does not show professional-designer quality.
- Errors still seen in round 2: a column-width sum that exceeds its stated breakpoint, a code width that does not fit its column, contradictions about where the accent or mono font is used, a missing size and an undeclared text colour in one spec, and a light accent described as amber that is actually brown. No output gave a reason for its Chinese line height or weights.
- The guidance edits in the commit that adds this file (three contrasting hue candidates, no reuse of example token names, reasons for Chinese line height and weight, an arithmetic and "used only for" self-check) came after round 2 and are NOT measured.
