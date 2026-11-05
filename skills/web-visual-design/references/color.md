# Colour

Read this before choosing or reviewing colours. Tags give the evidence grade and a source key from `sources.md`. `[working default]` means no source supports the number: it is this skill's starting point, so change it when the render disagrees.

## Contrast: the gate

- AA is 4.5:1 for text and 3:1 for large text. Large means at least 18pt, or 14pt bold, which is about 24px and 18.5px; CJK uses the same sizes. `[normative: WCAG-143]`
- Ratio = (L1 + 0.05) / (L2 + 0.05), where L is relative luminance after sRGB linearisation. `[normative: WCAG-143]`
- No rounding. 4.499 fails 4.5. `[normative, explained in the informative Understanding page: WCAG-143]`
- Controls, focus indicators and meaningful graphics need 3:1 against adjacent colours. `[normative: WCAG-1411]`
- A button label is text, so it falls under 1.4.3, not 1.4.11. In `tokens.json`, declare it `body` unless it is large. `ui` is only for non-text. `[normative: WCAG-1411]`
- Exempt: disabled controls, pure decoration, logotypes. Choosing low contrast for looks is not an exemption. `[normative: WCAG-143]`
- Thin faces can render fainter than their nominal colour. Leave margin above the minimum for light weights. `[informative: WCAG-143]`
- Colour must not be the only cue. A link told apart from surrounding text by colour alone needs another cue, such as an underline. `[normative: WCAG-141]`

### What `palette_check` proves, and what it does not

`python <skill-dir>/scripts/palette_check.py tokens.json` exits 0 (pass), 1 (problems) or 2 (unreadable file or bad usage).

It checks only the pairs you declare. **A file with empty `pairs` passes.** Declare every pair you use:

- `text`, `muted` and `accent` on every surface, as `body`
- button label on the filled accent, as `body`
- focus ring and control border against what they touch, as `ui`

It also rejects alpha and anything outside sRGB, so it says nothing about text over images, gradients or translucent layers. Check those by hand and say so.

It prints only problems. To report real ratios rather than estimates, run this from Python:

```python
import json, sys; sys.path.insert(0, "<skill-dir>/scripts"); import palette_check as p
for name, m in json.load(open("tokens.json", encoding="utf-8-sig"))["modes"].items():
    c = {k: p.parse_color(v) for k, v in m["colors"].items()}
    for x in m["pairs"]:
        print(name, x["fg"], "on", x["bg"], x["use"], int(p.contrast(c[x["fg"]], c[x["bg"]]) * 100) / 100)
```

## Contradictions you must not hide

**WCAG 2.2 versus APCA.**

| | WCAG 2.2 | APCA |
|---|---|---|
| Status | W3C Recommendation, the conformance target | Not in WCAG 2.x. Its author presents it as a WCAG 3 candidate `[expert opinion: APCA]` |
| WCAG 3 draft | Not deprecated by WCAG 3 `[background: WCAG3-WD]` | The 2026-09-10 Working Draft says its contrast algorithm is still to be determined, and the part read does not name APCA `[background: WCAG3-WD]` |
| Independence | Standards body | The source is the author's own site, not an independent review |

Rule for this skill: **WCAG 2.2 is the pass or fail gate. APCA is a secondary look only.** It can make you raise contrast, never lower it below WCAG. APCA suggests Lc 90 preferred for body, 75 minimum for body columns, 60 for other content, 45 for large headlines, 30 absolute minimum for text, 15 for non-text `[expert opinion: APCA]`. Its author argues that WCAG 2 overstates contrast near black. That is a reason to keep dark-mode margin well above 4.5, not a measured fact in this skill.

**Radix's guarantee is APCA, not WCAG.** Steps 11 and 12 promise Lc 60 and Lc 90 against step 2 `[vendor guidance: RADIX-SCALE]`. A Radix scale can meet that and still need its WCAG ratio computed.

**OKLCH L is not contrast.** L is perceived lightness `[vendor guidance: MDN-OKLCH]`. The Evil Martians article corrected itself on this: its changelog replaced "contrast" with "lightness" and says OKLCH alone is not enough to detect contrast `[expert opinion: EM-OKLCH]`. Numbers computed with `palette_check` on 2026-11-05:

| Colour on white | Ratio |
|---|---|
| `oklch(0.6 0.1 150)` | 3.77 |
| `oklch(0.6 0.1 330)` | 4.15 |
| `oklch(0.6 0.15 30)` | 4.23 |
| `oklch(0.6 0 0)` | 3.95 |

The same L spans 3.77 to 4.23, and the same L also behaves differently by polarity: grey at L 0.6 gets 3.95 on white and 5.32 on black, while L 0.5 gets 6.00 on white and 3.50 on black. So never infer a pass from an L difference. Compute it.

## OKLCH fields

- `L` 0 to 1 (or 0 to 100%), perceived lightness. `C` from 0, chroma; in practice it stays under about 0.5, and 100% means 0.4. `H` 0 to 360, hue. `[vendor guidance: MDN-OKLCH]`
- Hue angles are not HSL's: HSL red at 0deg is about 29 in OKLCH. Do not reuse HSL hue numbers. `[vendor guidance: MDN-OKLCH]`
- Baseline widely available since May 2023. `[vendor guidance: MDN-OKLCH]`
- Why not HSL: HSL lightness varies by hue, so the same `l` looks very different across hues. OKLCH makes lightness steps comparable. `[expert opinion: EM-OKLCH]`
- Derive variants in CSS: `oklch(from var(--accent) calc(l + 0.08) c h)`. `[vendor guidance: MDN-OKLCH]`
- Each L has its own maximum C per hue. Browsers map out-of-gamut values and some clipping shifts hue `[expert opinion: EM-OKLCH]`, and `palette_check` refuses them. Maximum in-sRGB C, computed on 2026-11-05:

| H | 30 | 90 | 150 | 210 | 270 | 330 |
|---|---|---|---|---|---|---|
| L 0.50 | 0.200 | 0.102 | 0.137 | 0.086 | 0.281 | 0.228 |
| L 0.85 | 0.082 | 0.173 | 0.234 | 0.137 | 0.074 | 0.134 |

So a blue accent that is vivid at L 0.5 has little chroma left at L 0.85. That is why dark-mode accents usually lose chroma.

## Procedure: derive, do not pick

Write every token as `oklch(...)` in `tokens.json`, and record its derivation.

1. **Anchor hue.** Take H from the subject of this brief and say why in one clause. If you cannot tie it to the subject, you have not chosen one yet.
2. **Neutrals.** Same or nearby H, very low chroma, C 0 to 0.02. Light: bg L about 0.97 to 0.995, text L about 0.2 to 0.3, muted L about 0.45 to 0.52. `[working default]`
3. **Accent.** Pick C inside the gamut for the hue, then move L until the `body` pair passes on every surface. At C 0.12 on white, the highest passing L was about 0.55 to 0.58 for hues 30, 150, 270 and 330. Hues 90 and 210 had no L that was both in gamut at C 0.12 and passing, so they need lower chroma (computed). Do not expect one L to work for every hue.
4. **Dark mode.** Rebuild, see below.
5. **Check.** Run `palette_check`. Report the command and exit code. Then print the ratios with the snippet. Never write hand-estimated ratios.

Record it as a table. The hue here is arbitrary; do not reuse it.

| Token | Light | Dark | Role | Derivation |
|---|---|---|---|---|
| bg | `oklch(0.985 0.004 300)` | `oklch(0.2 0.012 300)` | Page | Anchor hue, near-zero C. Dark bg is not the inverse: L 0.2 keeps room for a raised surface |
| surface | `oklch(0.955 0.008 300)` | `oklch(0.25 0.015 300)` | Grouped content | bg moved 0.03 to 0.05 in L, so grouping reads without borders |
| text | `oklch(0.26 0.015 300)` | `oklch(0.93 0.008 300)` | Body | Text 14.92 light, 14.73 dark on bg |
| muted | `oklch(0.46 0.02 300)` | `oklch(0.74 0.02 300)` | Metadata | L set to stay well clear of 4.5 on surface: 6.28 light, 6.92 dark |
| accent | `oklch(0.46 0.16 300)` | `oklch(0.76 0.12 300)` | Action | C lowered from 0.16 to 0.12 in dark because high L has less gamut; 6.73 light, 7.19 dark on surface |

Note muted and accent share L 0.46 in light mode yet get 6.86 and 7.36 on bg. That is the point above, in a real palette.

## Same-hue ramps and Radix's 12 steps

Hold H. Step L evenly for the role, and reduce C at both ends where the gamut narrows. Check each step with `parse_color`, which raises on out-of-gamut values. `[working default, on the OKLCH property above]`

Radix assigns each step a job `[vendor guidance: RADIX-SCALE]`:

| Step | Use |
|---|---|
| 1, 2 | App background; subtle background such as cards, code blocks, sidebars |
| 3, 4, 5 | Component background: normal, hover, pressed or selected |
| 6, 7, 8 | Border: subtle non-interactive, subtle interactive, strong and focus ring |
| 9, 10 | Solid background, logos, accent borders; its hover |
| 11, 12 | Low-contrast text; high-contrast text |

Most step 9 colours take white text; Sky, Mint, Lime, Yellow and Amber take dark text. `[vendor guidance: RADIX-SCALE]`

With 4 to 6 named tokens, this maps to bg = 1, surface = 2, muted = 11, text = 12, accent = 9 or 11. Border and hover states can be derived by relative colour syntax rather than added as new named colours. `[working default]`

## Dark mode: re-pair, do not invert

Inverting L does not preserve contrast (see the polarity numbers above). Each colour has its own dark counterpart in Radix too `[vendor guidance: RADIX-COMPOSE]`. So:

- Re-derive every token and declare every pair again in `dark`.
- Raised surfaces get lighter, not darker. `[working default]`
- Lower accent chroma as L rises, per the gamut table.
- Do not use pure white on near-black as the reflex. Choose text L by the ratio you want. `[working default; no authoritative source for a specific value]`

Material guidance was **not verified**: the pages read returned only a title, so nothing here relies on it.

## Perception: why the numbers are not enough

- **Colour is relative.** The same colour looks different by neighbour. Albers built a teaching course on this, relying on looking rather than systems `[background: ALBERS-YUP]`. Chevreul stated simultaneous contrast in 1839: adjacent colours shift as if tinted by each other's complement `[background: WP-COLOR, tertiary]`.
- **So:** judge the accent on its real surface, in both modes, at its real size. A small accent on a large field reads differently from the swatch. A contrast ratio does not predict this.
- **Warm and cool** is a relationship, not a property of one colour; sources disagree on the anchors. The claim that warm advances and cool recedes may be a side effect of warm pigments usually being lighter and more saturated `[background: WP-COLOR, tertiary]`.
- **So:** use warm and cool to separate two things by relationship. Do not state emotional meanings as fact. No authoritative source for universal colour-emotion mappings was found.
- **Harmony formulas.** Complementary or triadic recipes have limited predictive use, and harmony depends on context and culture `[background: WP-COLOR, tertiary]`. Do not offer a colour wheel relation as the justification for a palette.
- **Itten's seven contrasts** are hue, value, temperature, complements, simultaneous, saturation and extension (area) `[background: ITTEN-WP, a secondary listing citing Burton 1984]`. A peer-reviewed cartography paper treats them as useful in some cases and not others `[background: ITTEN-CJ, abstract only]`. The book itself was not read and no museum or publisher page defining them was found, so treat these as vocabulary for naming what a design does, for example "extension: accent stays under a small share of the area". They are not rules and not evidence.

## Hierarchy budget for colour

About 2 primary and 2 secondary colours in a simple design; keep bright warm colours for warnings `[expert opinion: NNG-HIER, rule of thumb]`. This skill's tokens format requires 4 to 6 named colours per mode, which fits.

## Avoid the default palette

Tailwind slate as the page's neutrals (`#0f172a`, `#1e293b`, `#64748b`, `#f1f5f9`, `#f8fafc`) `[vendor guidance: TW-COLORS]` plus a glow background is what this skill exists to avoid. In this repo's no-skill baseline, three unrelated briefs all landed on white or off-white and blue-black neutrals, with blue or teal as the main accent `[measured: BASELINE, n=3]`. If you land there, either give the reason this subject needs it, or move the anchor hue.
