---
name: web-visual-design
description: Use when choosing a website's colours or fonts, writing design tokens or a type and layout spec, setting Chinese or bilingual Chinese-English typography, deciding layout hierarchy, or reviewing a site's visual design. Triggers include 配色, 挑字體, 字型, 中文排版, 中英混排, 版面層次, palette, dark mode colours, contrast, font loading, type scale.
---

# Web Visual Design

Sourced knowledge and checks for web colour, type and hierarchy. The goal is a short system specific to this brief, with technical claims that hold up. It is not a template to fill in.

## Boundaries

`frontend-design` owns aesthetic direction: the concept and what makes this page unlike others. This skill owns the knowledge and checks behind it, plus the visual rules for each object on the page. `frontend-ui-engineering` owns how components are implemented. For new work, set direction first, then use this.

## What to read when

| Doing | Read |
|---|---|
| Colours, dark mode, default mode | `references/color.md` |
| Any Chinese content, or specifying or loading any font | `references/typography-zh-en.md` |
| Sizes, spacing, objects, memorable element, squint test | `references/layout-hierarchy.md` |
| Checking where a claim comes from | `references/sources.md` |

Those files grade each rule. Keep the limit when you repeat one: a book figure stays a book figure, and a working default is not a standard.

## Output

- **`tokens.json`.**
- **The spec.** It obeys the length the brief gives. Treat one page as about 600 words unless told otherwise `[working default]`. State decisions and the reason specific to this brief. Do not restate the rules from the references.
- **An appendix, in a separate file or section marked as outside the length:** derivation table, `palette_check` output, self-check, what was not verified.

A step that does not apply gets one clause or nothing. A step you could not do is noted in the appendix.

## Procedure

1. **Frame.** Say who reads this, on what device, for how long, what objects the content has, and which language and region. Assume where the brief is silent, and say so.
2. **Pick one memorable element**, tied to the subject. Say what it is, where it appears, and what is held back for it.
3. **Derive the colours in OKLCH.** Write `tokens.json`. Neutrals, lightness and chroma follow this audience and content. Say what in this brief makes the result differ from the examples in `references/color.md`. Warm grey is not an escape from blue-black; it is another default. Rebuild dark mode rather than inverting it. If the brief names a primary mode, say how that mode is implemented.
4. **Check them.** Name borders and focus rings that carry meaning as tokens, because the checker sees only named colours. Declare every pair you use: `text`, `muted` and `accent` on every surface; button labels; borders and focus rings as `ui`. Empty pairs fail, but listing only some pairs still passes, so list them all. Chinese text uses `body`, not `large`. Run this, and fix until it exits 0:

   ```
   python <skill-dir>/scripts/palette_check.py tokens.json
   ```

   Put the exit code and the real ratios in the appendix. Never write estimated ratios.
5. **Set the type.** Name each font and its job, with line length, line height and weights. Inter across the whole site is a reflex; keep it only for a reason from this brief.
6. **Set the Chinese**, if there is any. Decide and state: region, `lang` and a font of that region; punctuation position and quotation marks; which font draws — and … in Chinese runs, using a path that can be built with the fonts you chose; `text-autospace` and `text-emphasis-position` set explicitly; line height and weight with reasons. With no Chinese, state the `lang` value only.
7. **Decide on web fonts.** First weigh whether a web font earns its cost at all. For each one loaded, state the subset method and character source, the `font-display` value, the size budget and how it is measured, and the licence and any Reserved Font Name. For system fonts, say so.
8. **Count the hierarchy.** State how many sizes and weights, and the spacing rule, chosen for this content. Anything past 3 sizes needs a reason. Say what shows first, second and third at 10px of blur, labelled `predicted, not rendered` unless you rendered it.
9. **Give each object its rules.** List the objects this brief actually has, such as tables, code blocks, schedule rows, portraits or badges. Give each a type, colour and spacing rule. Check any width claim fits the stated column.
10. **Self-check** against the table below, in the appendix. Fix what fails, or list it as not met.

## Reviewing an existing site

Same checks on what is there: read computed colours into a `tokens.json` and run `palette_check`; read `lang`, font stacks, `@font-face` rules and transfer sizes; count sizes and spacing; blur the page for real. Report each finding with its selector or value and measured number.

## Self-check

| Item | Met when |
|---|---|
| Colour | `palette_check` exits 0, both modes, all pairs in use declared, meaningful borders named |
| Colour rationale | Every colour has a role and a perceptual reason for its lightness; gamut, not contrast, explains its chroma limit |
| Memorable element | Exactly one, and what is held back is named |
| Avoid defaults | Not Inter across the site with Tailwind slate and a glow background; any default kept has a reason from this brief |
| Specific to this brief | No value from the reference examples is reused without a reason; another brief would get a visibly different base |
| Chinese type | `lang` and regional glyphs; punctuation and mixing handled by something buildable; line height and weight have reasons |
| Font loading | Subset, `font-display`, size budget and licence check for each web font |
| Hierarchy | Sizes and spacing are counted and follow a rule; the squint description is honestly labelled |
| Objects | Every object in the brief has type, colour and spacing rules |
| Length | The spec body fits the brief; working goes in the appendix |

## Limits

These checks show that stated conditions are met. They do not certify quality, and attractive pages can still be hard to use (`references/layout-hierarchy.md`). Do not label the result's quality yourself. Say what was checked and what was not; a person makes the final call on taste.
