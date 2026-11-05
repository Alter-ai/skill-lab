# Colour

Read this before choosing or reviewing colours. Tags give the evidence grade and a source key from `sources.md`. `[working default]` means no source supports it: it is a starting point, so change it when the brief or the render disagrees.

## Contrast: the gate

- AA is 4.5:1 for text and 3:1 for large text. `[normative: WCAG-143]`
- For Latin, large means at least 18pt, or 14pt bold, about 24px and 18.5px. `[normative: WCAG-143]`
- **For CJK, those sizes do not carry over.** The definition asks for an equivalent size, which a note ties to the minimum large-print size for that language, and it gives no number. `[normative definition with an informative note: WCAG-143]` No concrete Chinese value was found. So **Chinese text uses `body` (4.5) at any size** until one is sourced. `[working default]`
- Ratio = (L1 + 0.05) / (L2 + 0.05), where L is relative luminance after sRGB linearisation. `[normative: WCAG-143]`
- No rounding. 4.499 fails 4.5. `[normative, explained in the informative Understanding page: WCAG-143]`
- Controls, focus indicators and meaningful graphics need 3:1 against adjacent colours. `[normative: WCAG-1411]`
- A button label is text, so it falls under 1.4.3, not 1.4.11. Declare it `body`. `ui` is only for non-text. `[normative: WCAG-1411]`
- Exempt: disabled controls, pure decoration, logotypes. Choosing low contrast for looks is not an exemption. `[normative: WCAG-143]`
- Thin faces can render fainter than their nominal colour, so leave margin for light weights. `[informative: WCAG-143]`
- Colour must not be the only cue. A link told apart from surrounding text by colour alone needs another cue, such as an underline. `[normative: WCAG-141]`

### What `palette_check` proves, and what it does not

`python <skill-dir>/scripts/palette_check.py tokens.json` exits 0 (pass), 1 (problems) or 2 (unreadable file or bad usage).

**Empty or missing `pairs` fail. Listing only some pairs still passes, so list them all:**

- `text`, `muted` and `accent` on every surface, as `body`
- button label on the filled accent, as `body`
- borders that identify a control or a data boundary, and focus rings, against what they touch, as `ui`

It sees only named colours. So **a border or focus ring that carries meaning must be a named token.** Derive only what is decorative or exempt, such as a hairline that nothing depends on. `[derived from WCAG-1411 and how the script works]` The format allows 6 names per mode, which fits bg, surface, text, muted, accent and border. A focus ring can reuse one of them. For a code theme or other extra colours, write a second tokens file and check that too.

It rejects alpha and anything outside sRGB, so it says nothing about text over images, gradients or translucent layers. Check those by hand and say so.

It prints only problems. For real ratios, and for the maximum chroma at a given L and H:

```python
import json, sys; sys.path.insert(0, "<skill-dir>/scripts"); import palette_check as p
for name, m in json.load(open("tokens.json", encoding="utf-8-sig"))["modes"].items():
    c = {k: p.parse_color(v) for k, v in m["colors"].items()}
    for x in m["pairs"]:
        print(name, x["fg"], "on", x["bg"], x["use"], int(p.contrast(c[x["fg"]], c[x["bg"]]) * 100) / 100)

def max_c(L, H):
    best = 0
    for i in range(401):
        try: p.parse_color(f"oklch({L} {i / 1000} {H})"); best = i / 1000
        except ValueError: break
    return best
```

## Contradictions you must not hide

**WCAG 2.2 versus APCA.**

| | WCAG 2.2 | APCA |
|---|---|---|
| Status | W3C Recommendation, the conformance target | Not in WCAG 2.x. Its author presents it as a WCAG 3 candidate `[expert opinion: APCA]` |
| WCAG 3 draft | Not deprecated by WCAG 3 `[background: WCAG3-WD]` | The 2026-09-10 Working Draft says its contrast algorithm is still to be determined, and the part read does not name APCA `[background: WCAG3-WD]` |
| Independence | Standards body | The source is the author's own site, not an independent review |

Rule for this skill: **WCAG 2.2 is the pass or fail gate. APCA is a secondary look only.** It can make you raise contrast, never lower it below WCAG. `[working default]` APCA suggests Lc 90 preferred for body, 75 minimum for body columns, 60 for other content, 45 for large headlines, 30 absolute minimum for text, 15 for non-text `[expert opinion: APCA]`. Its author argues that WCAG 2 overstates contrast near black. That is a reason to keep dark-mode margin above 4.5, not a measured fact in this skill.

**Radix's guarantee is APCA, not WCAG.** Steps 11 and 12 promise Lc 60 and Lc 90 against step 2 `[vendor guidance: RADIX-SCALE]`. A Radix scale can meet that and still need its WCAG ratio computed.

**OKLCH L is not contrast, yet contrast depends mainly on lightness.** L is perceived lightness `[vendor guidance: MDN-OKLCH]`. The Evil Martians article's changelog replaced "contrast" with "lightness" and says OKLCH alone is not enough to detect contrast `[expert opinion: EM-OKLCH]`. Computed with `palette_check` `[measured: COMPUTED]`:

| Change, on white | Ratio |
|---|---|
| L 0.4 to 0.7 at C 0.08, H 150 | 8.87, 5.78, 3.81, 2.58 |
| C 0 to 0.1 at L 0.55, H 150 | 4.85 to 4.63 |
| C 0 to 0.1 at L 0.55, H 30 | 4.85 to 5.08 |
| Same L 0.6 across hue and chroma | 3.77 to 4.23 |

So lightness moves the ratio a lot and chroma moves it a little. **Chroma is not why a colour passes.** Do not write "lowered chroma so it passes"; if a pair fails, change L. Polarity matters too: grey at L 0.6 gets 3.95 on white and 5.32 on black, L 0.5 gets 6.00 and 3.50. Never infer a pass from an L difference. Compute it.

## OKLCH fields

- `L` 0 to 1 (or 0 to 100%), perceived lightness. `C` from 0, chroma; in practice under about 0.5, and 100% means 0.4. `H` 0 to 360, hue. `[vendor guidance: MDN-OKLCH]`
- Hue angles are not HSL's: HSL red at 0deg is about 29 in OKLCH. `[vendor guidance: MDN-OKLCH]`
- Baseline widely available since May 2023. `[vendor guidance: MDN-OKLCH]`
- Why not HSL: HSL lightness varies by hue. OKLCH makes lightness steps comparable. `[expert opinion: EM-OKLCH]`
- Derive variants in CSS: `oklch(from var(--accent) calc(l + 0.08) c h)`. `[vendor guidance: MDN-OKLCH]`
- Browsers map out-of-gamut values and some clipping shifts hue `[expert opinion: EM-OKLCH]`; `palette_check` refuses them.

**Maximum chroma is per hue. Look it up with `max_c`; do not assume it falls as L rises.** Maximum in-sRGB C `[measured: COMPUTED]`:

| H | 30 | 90 | 150 | 210 | 270 | 330 |
|---|---|---|---|---|---|---|
| L 0.50 | 0.200 | 0.102 | 0.137 | 0.086 | 0.281 | 0.228 |
| L 0.75 | 0.151 | 0.153 | 0.206 | 0.129 | 0.128 | 0.248 |
| L 0.85 | 0.082 | 0.173 | 0.234 | 0.137 | 0.074 | 0.134 |

Blue-violet narrows sharply at high L; yellow-green does the opposite. In a 5-degree scan, 44 of 72 hues have a maximum at L 0.75 no lower than at L 0.5. So when you state a chroma limit, give the computed value for that hue.

## Derive, do not pick

1. **Anchor hue.** Look for something in this subject's content. Test the reason: if another hue could be argued as easily, say the hue is a free choice rather than inventing a link. `[working default]`
2. **Neutrals follow the audience.** Decide from how long people read, in what light, and whether the ground should itself be visibly coloured. Chroma can be zero, or high enough to read as a colour. Lightness need not sit near white or near black. `[working default]`
3. **Accent.** Move L until each `body` pair passes on every surface, and take C up to what `max_c` allows and the design wants. At C 0.12 on white, hues 90 and 210 had no L that was both in gamut and passing `[measured: COMPUTED]`, so one recipe does not suit every hue.
4. **Dark mode.** Rebuild, see below.
5. **Check.** Run `palette_check`, then print the ratios. Never write estimated ratios.

Record it in the appendix with these fields: token, light, dark, role, where H came from, why this L, why this C (gamut limit or design choice).

### Three deliberately different results

These show range. They are not starting points; reusing a value needs a reason from your brief. Values are `L C H`, in the order bg, surface, text, muted, accent, border. Each passes `palette_check` with all pairs declared, and each button label uses bg. `[measured: COMPUTED]`

**Tide tables read outdoors on phones.** Figures must survive glare, so neutrals have no chroma and contrast is near maximum. The one hue is for warnings.

```
light  1 0 0 | .95 0 0 | .14 0 0 | .38 0 0 | .48 .19 28 | .55 0 0
dark   .13 0 0 | .2 0 0 | .98 0 0 | .8 0 0 | .75 .15 28 | .6 0 0
```

Lowest ratios: light body 6.23, ui 4.19; dark body 7.65, ui 4.58.

**A seed catalogue browsed slowly.** The page should feel like tinted paper, so the ground is visibly coloured and well below white, and the text takes a dark green instead of a neutral.

```
light  .93 .035 110 | .88 .05 110 | .27 .05 135 | .42 .05 135 | .43 .12 35 | .52 .05 135
dark   .25 .035 135 | .31 .04 135 | .92 .035 110 | .8 .04 110 | .8 .1 60 | .65 .05 120
```

Lowest ratios: light body 5.82, ui 3.79; dark body 6.8, ui 4.06.

**A late-night radio schedule, dark by default.** The ground itself is the identity, a saturated violet rather than near-black, with one yellow against it.

```
dark   .27 .09 285 | .34 .1 285 | .96 .02 95 | .84 .04 285 | .88 .16 95 | .7 .08 285
light  .96 .04 95 | .91 .06 95 | .27 .09 285 | .42 .09 285 | .42 .17 285 | .52 .1 285
```

Lowest ratios: dark body 7.37, ui 4.46; light body 6.67, ui 4.35.

## Same-hue ramps and Radix's 12 steps

Hold H, step L for the role, and limit C per step with `max_c`. `[working default, on the measured table above]`

Radix assigns each step a job `[vendor guidance: RADIX-SCALE]`:

| Step | Use |
|---|---|
| 1, 2 | App background; subtle background such as cards, code blocks, sidebars |
| 3, 4, 5 | Component background: normal, hover, pressed or selected |
| 6, 7, 8 | Border: subtle non-interactive, subtle interactive, strong and focus ring |
| 9, 10 | Solid background, logos, accent borders; its hover |
| 11, 12 | Low-contrast text; high-contrast text |

Most step 9 colours take white text; Sky, Mint, Lime, Yellow and Amber take dark text. `[vendor guidance: RADIX-SCALE]`

With 6 names, this roughly maps to bg = 1, surface = 2, border = 7 or 8, accent = 9 or 11, muted = 11, text = 12. Hover states can be derived with relative colour syntax; meaningful borders cannot, as above. `[working default]`

## Dark mode: re-pair, do not invert

Inverting L does not preserve contrast (see the polarity numbers). Radix gives each colour its own dark scale `[vendor guidance: RADIX-COMPOSE]`. So:

- Re-derive every token and declare every pair again in `dark`. `[derived]`
- Raised surfaces usually get lighter. `[working default]`
- Take accent chroma from `max_c` at the new L. It may go up or down depending on hue. `[measured: COMPUTED]`
- Choose text L by the ratio you want, not pure white by reflex. `[working default; no authoritative source for a value]`

Material guidance was **not verified**: the pages read returned only a title, so nothing here relies on it.

### Implementing a default mode

`prefers-color-scheme` has only `light` and `dark`, and `light` also covers a user who has expressed no preference. `[vendor guidance: MDN-PCS]` **So a page cannot tell "chose light" from "set nothing".** A dark-primary site that simply follows the query shows light to everyone who never set a preference. `[derived]` Choose one and state it:

- **Follow the system.** Primary then only means which mode was designed first.
- **Dark for everyone by default.** Dark tokens are the base with no media query deciding first paint. Add a visible toggle, store the choice, and apply it from a small inline script in `<head>` before first paint. `[derived]`

`<meta name="color-scheme" content="dark light">` states dark is preferred and light acceptable; the order carries the preference. `[vendor guidance: MDN-META-CS]` `color-scheme` only changes browser-drawn parts such as the canvas, scrollbars and form controls, so your own styles still have to switch. `[vendor guidance: MDN-CS]` `light-dark()` returns its first value for light and second for dark, needs `color-scheme` to include both, and is Baseline 2024. `[vendor guidance: MDN-LD]`

## Perception: why the numbers are not enough

- **Colour is relative.** The same colour looks different by neighbour. Albers built a teaching course on this, relying on looking rather than systems `[background: ALBERS-YUP]`. Chevreul stated simultaneous contrast in 1839: adjacent colours shift as if tinted by each other's complement `[background: WP-COLOR, tertiary]`.
- **So** judge the accent on its real surface, in both modes, at its real size. A contrast ratio does not predict this. `[derived]`
- **Warm and cool** is a relationship, and sources disagree on the anchors. The claim that warm advances and cool recedes may be a side effect of warm pigments usually being lighter and more saturated `[background: WP-COLOR, tertiary]`.
- **So** use warm and cool to separate two things. Do not state emotional meanings as fact: no authoritative source for universal colour-emotion mappings was found. `[derived]`
- **Harmony formulas.** Complementary or triadic recipes have limited predictive use, and harmony depends on context and culture `[background: WP-COLOR, tertiary]`. Do not offer a colour wheel relation as the justification for a palette. `[derived]`
- **Itten's seven contrasts** are hue, value, temperature, complements, simultaneous, saturation and extension (area) `[background: ITTEN-WP, a secondary listing citing Burton 1984]`. A peer-reviewed cartography paper finds them useful in some cases and not others `[background: ITTEN-CJ, abstract only]`. The book was not read and no museum or publisher page defining them was found, so treat them as vocabulary for naming what a design does. They are not rules and not evidence.

## Colour count

About 2 primary and 2 secondary colours in a simple design; keep bright warm colours for warnings `[expert opinion: NNG-HIER, rule of thumb]`. The tokens format requires 4 to 6 named colours per mode.

## Defaults to notice

- Tailwind slate neutrals (`#0f172a`, `#1e293b`, `#64748b`, `#f1f5f9`, `#f8fafc`) `[vendor guidance: TW-COLORS]` with a glow background.
- White or off-white with blue-black neutrals and one blue or teal accent: all three no-skill runs landed here. `[measured: BASELINE, n=3]`
- **Warm grey near H 85 to 90, L about .98 and .20, surface a few hundredths away:** all three runs with an earlier version of this skill landed here on unrelated briefs, because it taught avoiding blue-black and gave one example. `[measured: EVAL-R1, n=3]`

None is wrong in itself. Each needs a reason from this brief.
