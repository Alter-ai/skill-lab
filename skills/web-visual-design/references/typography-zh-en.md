# Typography: Chinese and Latin

Read this before setting type or specifying fonts. Tags give the evidence grade and a source key from `sources.md`.

`CLREQ` is a W3C Group Note Draft dated 2026-11-04. It marks itself as work in progress that should not be formally cited, so treat it as expert opinion, not a standard. Most of its numbers describe **books**. No authoritative web-specific number was found for Chinese line length, leading, body size or weight.

## Latin numbers apply to Latin only

Web body 15 to 25px, line spacing 120 to 145%, 45 to 90 characters per line. `[expert opinion: BUTTERICK-10, BUTTERICK-LL; Latin only]` Do not apply these to Han text.

Contradiction: in the owner's benchmark sample, two Latin sites use about 1.65 and 1.75 line-height, above Butterick's range `[measured: D7, n=2]`. Pick by testing with your content, and say which you followed. `[working default]`

## Region and `lang`

- Rules follow **region**, not Simplified versus Traditional. Regions have their own standards for glyph forms and layout. `[expert opinion: CLREQ §1.2]`
- Punctuation position: Taiwan and Hong Kong centre marks in the square; mainland China sets them after the character they mark. `[expert opinion: CLREQ §2.1.2, §5.1]`
- Those marks share code points, so a typeface matching the locale, or the layout engine, has to supply the right form. `[expert opinion: CLREQ §5.1]`
- By default the browser uses the glyph forms for the `lang` language if the font has them. `font-language-override` is not Baseline, so do not rely on it. `[vendor guidance: MDN-FLO]`
- Keep tags as short as is useful, and add subtags only when they make a distinction you need. `[vendor guidance: W3C-LANG]` Here region is that distinction. `[derived]`

**Name a region and a `lang` value.** `zh-Hant-TW` for Taiwan and `zh-Hant-HK` for Hong Kong, each with a font of that region; Noto Sans has separate TC and HK cuts `[vendor guidance: NOTO-DIR]`. Plain `zh-Hant` leaves the region open. If the brief names none, assume one, say so, and say what changes if wrong. Mark English runs `lang="en"`, inline ones included. `:lang(zh)` matches all of these tags `[vendor guidance: MDN-LANG]`.

## Han setting

- Han characters and punctuation are 1:1 squares set solid `[expert opinion: CLREQ §1.2]`, so `max-width: 34em` holds 34 characters. `[derived]`
- `ch` measures the `0` glyph, about half a Han character; `ic` measures 水 (Chrome 106, Firefox 97, Safari 15.4). `[vendor guidance: MDN-LEN, BCD-IC]` `62ch` is not 62 Han characters.
- **Line length.** Book references, in a Note: most books 17 to 40 characters per line; at least 10; at most 48 horizontal. `[expert opinion: CLREQ §7.1.1.5, books only]` **No authoritative web figure found.** Choose from the device and reading length. A 360px screen with 16px gutters and 16px type holds 20. `[derived]`
- **Line height.** Book line gap is commonly 50 to 100% of the character height, which is CSS `line-height` 1.5 to 2.0. Short lines or small sizes can use less, and going past 100% does not help reading. `[expert opinion: CLREQ §7.1.1.5, books only]` So Chinese usually sits above Latin's range. Long reading tends to the upper part, short phone lines and headings below it. `[working default]`
- **Set `line-height` on block elements.** `:lang(en)` also matches inline English, so a line-height there changes the line box inside a Chinese paragraph. `[derived]`
- **Why weight is adjusted.** Han characters pack many strokes into one square, and small sizes get hard to read for that reason `[expert opinion: CLREQ §7.1.1.5 item 2]`. No authoritative figure exists for how weights should differ on screen. Check by eye that Han and Latin at one nominal weight read as the same grey. `[working default]`
- **Body size.** Print body is commonly 10.5pt `[expert opinion: CLREQ §7.1.1.5 item 2]`, which does not transfer to screens. Starting point: 16 to 18px, metadata not under 14px. `[working default]`
- **Letter spacing.** Han is set solid by default. Leave body at 0; say why if you add tracking to headings. `[working default]` `letter-spacing` and `word-spacing` add on top of `text-autospace`. `[vendor guidance: MDN-AUTOSPACE]`

### Emphasis

- Many CJK fonts lack bold and italic cuts, and synthesised ones can hurt legibility or meaning, so `font-synthesis: none` under `:lang(zh)` is reasonable. `[vendor guidance: MDN-SYNTH]` No italics on Han. `[derived]`
- Use a real heavier cut `[expert opinion: CLREQ §3.1.1.3]` or emphasis dots. Dots go below in horizontal text `[expert opinion: CLREQ §5.3.1]`.
- **Set the position explicitly: `text-emphasis: filled dot; text-emphasis-position: under right`.** The value `auto` is not in Chrome or Safari `[vendor guidance: BCD-EMPHPOS]`, and with no position set, Chrome 152 computed `over` `[measured: BROWSER]`, which puts the dots above.
- Some families stop short: LXGW WenKai TC ships Light, Regular and Medium only `[vendor guidance: LXGW-REL]`, so with synthesis off, Medium is its heaviest.
- **Check for two Chinese bold designs on one page.** A web font for headings with body emphasis falling back to a system bold shows two different bolds. Check each target device. `[derived]`

## Punctuation

- Use Chinese punctuation in Chinese sentences, even around English words. Technical text with many formulas may use the Western full stop and ellipsis. `[expert opinion: CLREQ §4.1]`
- **Quotes.** Taiwan: 「」 first, 『』 nested; some Taiwanese publications use the other order. Mainland: “” first. `[expert opinion: CLREQ §5.2]` The part read gave no separate rule for Hong Kong.
- **Ellipsis.** Two U+2026, two characters wide, centred, never split across lines. `[expert opinion: CLREQ §5.4.1]`
- **Dash.** Two em, centred, never split. CLREQ recommends U+2E3A; two U+2014 are also common. `[expert opinion: CLREQ §5.1]` Check the font has what you use. `[derived]`
- `text-spacing-trim` trims adjacent full-width marks, but it is experimental and Chromium only (Chrome and Edge 123), and needs `halt` or `chws` in the font. `[vendor guidance: MDN-TRIM, BCD-TRIM]` Use it only as an enhancement. `[derived]`

## Latin in Han text

- **Latin font:** proportional. Numerals proportional or monospaced. `[expert opinion: CLREQ §6.3.3]`
- **Spacing:** no more than 1/4 em between Han and Latin or digits; none at line start or end; none beside Chinese stops, pauses, or inside Chinese brackets. A U+0020 is an allowed alternative, of variable width. `[expert opinion: CLREQ §6.3.3]`
- **`text-autospace`** adds this spacing in layout, without changing the text. `[vendor guidance: MDN-AUTOSPACE]` Baseline 2025: Chrome and Edge 140, Firefox 145, Safari 18.4. `[vendor guidance: BCD-AUTOSPACE]`
- **Contradiction, and it changes what you write.** The draft spec gives the initial value as `normal` `[normative draft: CSS-TEXT-4]` and the working group reaffirmed that on 2025-12-10 `[expert opinion: CSSWG-12386]`. Browser data says shipped browsers start at `no-autospace` `[vendor guidance: BCD-AUTOSPACE]`, and Chrome 152 computed exactly that, adding no gap until told to `[measured: BROWSER]`. **So set `text-autospace: normal` explicitly.**
- In Chrome 152 `normal` added 1/8 em per boundary, inside CLREQ's ceiling. `[measured: BROWSER]`
- **Do not use the finer keywords yet.** `normal` and `no-autospace` work across engines; `ideograph-alpha`, `ideograph-numeric`, `auto` and `insert` are not in Chromium. `[vendor guidance: BCD-AUTOSPACE]`
- **No double space.** Without a keyword, spacing behaves like `insert`, adding nothing where a space already exists. `[normative draft: CSS-TEXT-4; vendor guidance: MDN-AUTOSPACE]` Chrome 152 confirmed this `[measured: BROWSER]`; Firefox and Safari were not tested. For new content, do not type literal spaces. Older browsers then show no gap, which is acceptable because CLREQ gives a ceiling, not a minimum. `[derived]`
- **Code needs its own rule.** The spec's UA stylesheet is an informative appendix, which browsers may ignore `[normative draft: CSS-TEXT-4]`, and in Chrome 152 `code` inherited `normal` from its parent `[measured: BROWSER]`. Add `pre, code, kbd, samp { text-autospace: no-autospace }`.
- **Words:** Western words do not split except at hyphenation points. `[expert opinion: CLREQ §6.1.4]` Long identifiers on a phone may need `overflow-wrap: anywhere`. `[working default]`

## Font stack: which font draws shared punctuation

Browsers pick a font per character. With a Latin font first, the code points Chinese shares with Latin (U+2014, U+2018 to U+201D, U+2026, U+00B7) come from the Latin font, where they sit on the baseline and are narrow. In Chrome 152 at 20px, with Segoe UI first, `……` measured 29.3px and `“` 7.5px; with the Han face drawing them, 40px and 20px. `[measured: BROWSER]` CLREQ says Western-style ellipses and stops keep Western positioning. `[expert opinion: CLREQ §4.1]`

`unicode-range` exists only in `@font-face`. `local()` takes the name of an installed face, not `system-ui`, and browsers may ignore user-installed fonts there. `[vendor guidance: MDN-SRC]` So **a system Latin font cannot be range-limited in a portable way.** Choose a path you can build:

| Fonts | Path | Cost |
|---|---|---|
| System fonts only | Put the Chinese face first in `:lang(zh)` | Latin letters come from the Han face |
| System Latin must lead | Accept the Latin punctuation result, and say so | Ellipsis and dash look wrong in Chinese runs; less exposed if copy uses 「」 and avoids them |
| Web Latin font | Range-limit it, as below | One more `@font-face`; the same file serves both |

```css
/* Letters only in Chinese runs, so shared punctuation falls through to the Han face */
@font-face { font-family: "Site Latin zh"; src: url(latin.woff2) format("woff2");
             unicode-range: U+0020-007E, U+00C0-00FF; font-display: optional; }
@font-face { font-family: "Site Latin"; src: url(latin.woff2) format("woff2"); font-display: optional; }
:root { text-autospace: normal; }
pre, code, kbd, samp { text-autospace: no-autospace; }
:lang(zh) { font-synthesis: none; }
html:lang(zh) { font-family: "Site Latin zh", "Your Han face", sans-serif; line-height: var(--leading-zh); }
html:lang(en) { font-family: "Site Latin", system-ui, sans-serif; line-height: var(--leading-en); }
/* Inline English in a Chinese page needs no rule. A whole block in the other language
   gets its own font-family and line-height on that block element. */
```

The recipe is `[derived, no authoritative source]`. The range-limiting behaviour was tested in Chrome 152 on Windows only, with a local face standing in for `latin.woff2` `[measured: BROWSER]`. Test Firefox and Safari by rendering 「引號」“引號”……——.

For a Han system face, PingFang TC on Apple systems and Microsoft JhengHei on Windows are general knowledge, not sourced here; check them on your targets. Do not list a mainland face first on a Traditional Chinese page. `[derived]`

## Font loading

**First weigh whether to load one.** Full CJK fonts cannot be sent as they are: Noto Sans TC Regular OTF is 5.68 MB `[vendor guidance: NOTO-DIR]`, LXGW WenKai TC Regular TTF 15.3 MB `[vendor guidance: LXGW-REL]`. CJK fonts can exceed 10,000 glyphs `[vendor guidance: WEBDEV-FONT]`, and Chinese webfonts stay rare largely because of size `[background: ALMANAC]`. A web font for only a few headlines has to earn it: load one when it carries the memorable element, and say so. Otherwise system fonts are a real choice. `[working default]`

For each web font, state these four in a line. Do not paste commands into the spec.

**1. Subset.** WOFF2 only `[vendor guidance: WEBDEV-FONT]`. Choose by content `[derived]`:

| Text | Approach | Why |
|---|---|---|
| Fixed, known at build: headings, a logo word | Static subset from the real strings | Smallest result |
| Changes: CMS, posts, schedule edits | `unicode-range` slices, or a system-font body | A static subset leaves new characters to a fallback, mixing faces in one line |
| Long Chinese body | System fonts | Nothing to load |

With fontTools, run `pyftsubset <font> --text-file=<chars> --flavor=woff2 --name-IDs='*'`. WOFF2 output needs the Brotli module. `[vendor guidance: FONTTOOLS]`

- **Leave `--layout-features` alone.** The default already keeps `locl`, and its `vertical` and `east_asian_spacing` groups cover `vert`, `halt`, `chws`, `vhal`, `vchw` and `palt`. `[vendor guidance: FONTTOOLS-SRC]` Add single features you use, such as `--layout-features+=tnum` for tabular figures, which is not in the default. `[measured: BROWSER]`
- **Keep `--name-IDs='*'`.** The default keeps only IDs 0 to 6 and drops the licence fields, IDs 13 and 14. `[vendor guidance: FONTTOOLS]`
- Run on the installed Noto Sans TC variable font with a 44-character text: default 12,516 bytes, with name IDs 13,188, with `--layout-features='*'` as well 16,964. That last flag added only `aalt`, `dlig`, `fwid`, `hwid` and `pwid`, for 29% more. `[measured: BROWSER]`

**2. `font-display`.** `optional` for body avoids layout shift, `swap` for brand or display, and mixing the two works `[vendor guidance: WEBDEV-FONT]`. `size-adjust` on a fallback reduces the shift from `swap` (Chrome 92, Firefox 92, Safari 17) `[vendor guidance: BCD-SIZEADJ]`. Preload ignores `unicode-range`, so preload at most one critical file `[vendor guidance: WEBDEV-FONT]`.

**3. Size budget.** State a number and how it is measured. **No authoritative budget exists.** Set it from the number of faces, the device and the network. As an unsourced anchor, about 150 KB of font bytes on first view. `[working default]` For scale, the median font file is about 35 KB across all sites, not CJK-specific `[background: ALMANAC]`. Measure from DevTools Network filtered to Font, or the built files. If nothing is built, write "target, not measured".

**4. Licence.** Read the licence before specifying the font. `[vendor guidance: WEBDEV-FONT]`

- Pages may load OFL fonts with `@font-face`, from your own server or a service. `[vendor guidance: OFL-FAQ Q2.1]` Hosting fonts for others to use is allowed "as long as you make the full font package available". `[vendor guidance: OFL-FAQ Q1.8]`
- **Subsetting counts as modification.** It is allowed, but a modified font normally may not keep a Reserved Font Name. The Functional Equivalence exception needs the same character coverage, so a subset does not qualify. `[vendor guidance: OFL-FAQ Q2.5 to Q2.8]`
- WOFF2 compression alone is not modification only if the font data is unchanged and metadata is intact; tools do not automatically ensure that. `[vendor guidance: OFL-FAQ Q2.2.1, Q2.2.2]`
- Keep copyright and licence information in the metadata, and ship the licence text with the font. `[vendor guidance: OFL-FAQ Q1.10, Q2.4]`
- **This is a reading of the FAQ, not legal advice.** Whether a given font needs renaming is a human decision. State it as an open item.

| Font | Read 2026-11-05 | Note |
|---|---|---|
| Noto Sans TC | OFL 1.1, Reserved Font Name 'Source' `[normative: LIC-NOTO-GF]`; also in name ID 0 of the Windows-installed file `[measured: BROWSER]` | The family name does not contain "Source". Read the name table of the file you use, and have a person decide on renaming. The noto-cjk `LICENSE` has no copyright line, so its silence proves nothing `[normative: LIC-NOTO]` |
| LXGW WenKai TC | OFL 1.1; the copyright line names no reserved name `[normative: LIC-LXGW]` | Confirm in the file you use |
| Inter | OFL 1.1; the copyright line names no reserved name `[normative: LIC-INTER]` | Confirm in the file you use |
| IBM Plex | OFL 1.1, Reserved Font Name "Plex" `[normative: LIC-PLEX]` | The family name contains it, so per the FAQ a subset needs a new name |
| Source Han Sans | OFL 1.1, Reserved Font Name "Source" `[normative: LIC-SOURCE]` | Same |

For anything else, including paid fonts, read its licence; do not extend this table from memory. Self-hosting is not automatically faster, so test it. `[vendor guidance: WEBDEV-FONT]`
