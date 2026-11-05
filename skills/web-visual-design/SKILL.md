---
name: web-visual-design
description: Use when choosing a website's colours or fonts, writing design tokens or a type and layout spec, setting Chinese or bilingual Chinese-English typography, deciding layout hierarchy, or reviewing a site's visual design. Triggers include 配色, 挑字體, 字型, 中文排版, 中英混排, 版面層次, palette, dark mode colours, contrast, font loading, type scale.
---

# Web Visual Design

Sourced knowledge and checks for web colour, type and hierarchy. It turns taste into statements someone else can check.

## Boundary with `frontend-design`

`frontend-design` owns aesthetic direction: the concept, the point of view, what makes this page unlike others. This skill owns the knowledge and the checks: how each colour was derived, whether the pairs pass, how Chinese is set, how fonts load, whether the hierarchy holds. Use both when building something new; direction first, then this. Use this alone when reviewing, or when direction is already set. Component and CSS engineering belong to `frontend-ui-engineering`.

## What to read when

| Doing | Read |
|---|---|
| Choosing or reviewing colours, dark mode | `references/color.md` |
| Any Chinese content, or specifying or loading any font | `references/typography-zh-en.md` |
| Sizes, spacing, memorable element, squint test | `references/layout-hierarchy.md` |
| Checking where a claim comes from | `references/sources.md` |

Those files tag each rule by evidence grade. Keep the grade when you repeat a rule. Say "working default" or "no authoritative source" where that is what the file says; do not present it as a standard.

## Procedure

Do every step and show the result in the output. A step you could not do gets a line saying so. Do not skip silently.

1. **Frame.** Name the subject, the audience, the primary reading device, and the language and region. If the brief is silent on any of these, assume and say so.
2. **Name one memorable element.** Use this form: "Memorable element: X. It appears in N places and takes Y. Held back so it can stand out: A, B, C." Tie it to the subject.
3. **Derive the colours in OKLCH.** Write `tokens.json` with `oklch(...)` values. Give a table with a row per token: token, light value, dark value, role, how it was derived (where the hue comes from; why this L and C). Rebuild dark mode rather than inverting it. If you land on Tailwind slate, or on blue-black neutrals with a blue accent, give this brief's reason or move the hue.
4. **Check them.** Declare every pair you use: `text`, `muted` and `accent` on every surface as `body`; a button label on the accent as `body`, since it is text; focus and control borders as `ui`. An empty pair list passes, so that proves nothing. Then run:

   ```
   python <skill-dir>/scripts/palette_check.py tokens.json
   ```

   Report the command and the exit code. Fix until it exits 0. Print the real ratios with the snippet in `references/color.md`. Never write hand-estimated ratios. If you cannot run it, write "palette_check not run" and report no ratios.
5. **Set the type.** Name the fonts and what each one is for. Give the line length, line height and weights, and the reason for each. Inter across the whole site is the reflex; if you keep it, give this brief's reason.
6. **Set the Chinese.** If the site has Chinese, state all of these:
   - the region and the `lang` value, for example `zh-Hant-TW`, and a font of that region
   - punctuation: the position for that region, which quotation marks, how ellipsis and dash are handled
   - Latin-Han mixing: `text-autospace: normal` set explicitly, and the no-typed-spaces convention
   - shared punctuation in the font stack: which font draws — and … in Chinese runs
   - line height and weight for Chinese, each with its reason, and how emphasis works without italics

   If there is no Chinese, state the `lang` value and say so in one line.
7. **Specify font loading.** Give all four, per font:
   - subset: which method and which character source
   - `font-display` value and why
   - size budget: the number and how it is measured; label it "target, not measured" if nothing is built
   - licence: licence name, whether a Reserved Font Name applies, what this means for a subset

   If using only system fonts, say so and why; subset and budget then become "none".
8. **Count the hierarchy.** State the type sizes with a count, the weights with a count, and the spacing steps with their rule. Anything past 3 sizes needs a reason. Then write the squint description: what you see at 10px of blur, in order. Label it `predicted, not rendered` unless you actually rendered and blurred it.
9. **Self-check against the table below.** For each row, cite the line in your output that meets it. Fix any you cannot cite, or list it under "Not met". Then list what you did not verify.

## Reviewing an existing site

Same checks, on what is there: read computed colours into a `tokens.json` and run `palette_check`; read `lang`, font stacks, `@font-face` rules and transfer sizes; count the sizes and spacing in use; blur the page for real. Report findings with the selector or value and its measured number.

## Self-check

| Item | Met when |
|---|---|
| Colour | `palette_check` exits 0, with both modes and all pairs in use declared |
| Colour rationale | Every colour has a role and an OKLCH or perceptual reason for its lightness |
| Memorable element | Exactly one is named, and the things held back are named too |
| Avoid defaults | Not Inter across the site with Tailwind slate and a glow background. Any default you keep has a reason from this brief |
| Chinese type | `lang` and regional glyphs; punctuation and mixing handled; line height and weight have reasons |
| Font loading | Subset, `font-display`, size budget and licence check, per font |
| Hierarchy | Sizes and spacing are counted and follow a rule; a squint description is present and honestly labelled |

## Limits

These checks show that stated conditions are met. They do not certify quality, and attractive pages can still be hard to use (`references/layout-hierarchy.md`). Do not describe the result with quality labels of your own. Say what was checked, what was not, and that a person makes the final call on taste.
