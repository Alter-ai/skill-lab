# Typography: Chinese and Latin

Read this before setting type or specifying fonts. Tags give the evidence grade and a source key from `sources.md`.

`CLREQ` is a W3C Group Note Draft dated 2026-11-04. It marks itself as work in progress that should not be formally cited, so treat it as expert opinion, not a standard. Most of its numbers describe **books**. No authoritative web-specific number was found for Chinese line length, leading, body size or weight.

## Latin numbers apply to Latin only

Web body 15 to 25px, line spacing 120 to 145%, 45 to 90 characters per line. `[expert opinion: BUTTERICK-10, BUTTERICK-LL; Latin only]` Do not apply these to Han text.

Contradiction: in the owner's benchmark sample, two Latin sites use about 1.65 and 1.75 line-height, above Butterick's range `[measured: D7, n=2]`. Those are sites with narrow columns and short texts. Pick by testing, and say which you followed.

## Region and `lang`

- Rules follow **region**, not Simplified versus Traditional. Regions have their own standards for glyph forms and layout. `[expert opinion: CLREQ §1.2]`
- Punctuation position: Taiwan and Hong Kong centre marks in the square; mainland China sets them after the character they mark. `[expert opinion: CLREQ §2.1.2, §5.1]`
- Those marks share code points, so a typeface matching the locale, or the layout engine, has to supply the right form. `[expert opinion: CLREQ §5.1]`
- By default the browser uses the glyph forms for the `lang` language if the font has them. `font-language-override` is not Baseline, so do not rely on it. `[vendor guidance: MDN-FLO]`
- Keep tags as short as is useful, and add subtags only when they make a distinction you need. `[vendor guidance: W3C-LANG]` Here region is that distinction.

**Rule: name a region and a `lang` value.** Use `zh-Hant-TW` for Taiwan and `zh-Hant-HK` for Hong Kong, and pair each with a font of that region (Noto Sans has separate TC and HK cuts `[vendor guidance: NOTO-DIR]`). Plain `zh-Hant` leaves the region open; if the brief does not name one, assume one, say so, and name what changes if wrong. Put `lang="en"` on English runs too, inline ones included. `:lang(zh)` matches all of these `[vendor guidance: MDN-LANG]`, so CSS can stay simple.

## Han setting

- Han characters and punctuation are 1:1 squares set solid. `[expert opinion: CLREQ §1.2]` So size in `em` counts characters: `max-width: 34em` is 34 characters. `[derived]`
- `ch` measures the `0` glyph, about half a Han character; `ic` measures 水 (Chrome 106, Firefox 97, Safari 15.4). `[vendor guidance: MDN-LEN, BCD-IC]` `62ch` is not 62 Han characters.
- **Line length.** Book references: most books 17 to 40 characters per line; at least 10; at most 48 horizontal. `[expert opinion: CLREQ §7.1.1.5, a Note about books]` **No authoritative web figure found.** Working use: 30 to 38 on desktop, whatever fits on a phone as long as it stays above 10. A 360px screen with 16px gutters and 16px type gives 20 characters. `[working default]`
- **Line height.** Book line gap is commonly 50 to 100% of the character height, which is CSS `line-height` 1.5 to 2.0. Short lines or small sizes can use less, and going past 100% does not help reading. `[expert opinion: CLREQ §7.1.1.5, a Note about books]` So Chinese usually sits above Latin's 1.2 to 1.45. Working values: body 1.7 to 1.85, tighter on short phone lines, headings 1.3 to 1.4. `[working default]`
- Set `line-height` on the block. Do not give inline English runs their own value. `[working default]`
- **Why the weight is adjusted.** Han characters pack many strokes into the same square, and CLREQ cites their complex structure as the reason for a minimum body size. `[expert opinion: CLREQ §7.1.3.2]` No authoritative figure exists for how weights should differ on screen. Check by eye that Han body and Latin at the same nominal weight read as the same grey, and adjust by one weight step if the font has one. `[working default]`
- **Body size.** Print body is commonly 10.5pt `[expert opinion: CLREQ §7.1.1.5]`, which does not transfer to screens. Working value: 16 to 18px, metadata not under 14px. `[working default]`
- **Letter spacing.** Han is set solid by default. Leave body at 0; say why if you add tracking to headings. `[working default]` `letter-spacing` and `word-spacing` add on top of `text-autospace`. `[vendor guidance: MDN-AUTOSPACE]`
- **Emphasis.** Many CJK fonts have no bold or italic cuts, and synthesised ones can hurt legibility or meaning, so `font-synthesis: none` under `:lang(zh)` is reasonable `[vendor guidance: MDN-SYNTH]`. Use a real heavier cut `[expert opinion: CLREQ §3.1.1.3]` or emphasis dots (`text-emphasis: filled dot` with `text-emphasis-position: under right`, widely available since March 2022) `[expert opinion: CLREQ §5.3.1; vendor guidance: MDN-EMPH, MDN-EMPHPOS]`. No italics on Han. Note that some families stop short: LXGW WenKai TC ships Light, Regular and Medium only `[vendor guidance: LXGW-REL]`, so with synthesis off, Medium is its heaviest.

## Punctuation

- Use Chinese punctuation in Chinese sentences, even around English words. Technical text with many formulas may use the Western full stop and ellipsis. `[expert opinion: CLREQ §4.1]`
- **Quotes.** Taiwan: 「」 first, 『』 nested; some Taiwanese publications use the other order. Mainland: “” first. `[expert opinion: CLREQ §5.2]` The part read gave no separate rule for Hong Kong, so check a local reference.
- **Ellipsis.** Two U+2026, two characters wide, centred, never split across lines. `[expert opinion: CLREQ §5.4.1]`
- **Dash.** Two em, centred, never split. CLREQ recommends U+2E3A; two U+2014 are also common. `[expert opinion: CLREQ §5.1]` Check the font has what you use.
- `text-spacing-trim` trims adjacent full-width marks, but it is experimental and Chromium only (Chrome and Edge 123; none listed for Firefox or Safari), and it needs `halt` or `chws` in the font. `[vendor guidance: MDN-TRIM, BCD-TRIM]` Treat it as progressive enhancement: the page must read correctly without it. If you use it, keep those features when subsetting.

## Latin in Han text

- **Latin font:** proportional. Numerals proportional or monospaced. `[expert opinion: CLREQ §6.3.3]`
- **Spacing:** no more than 1/4 em between Han and Latin or digits; none at line start or end; none beside Chinese stops, pauses, or inside Chinese brackets. `[expert opinion: CLREQ §6.3.3]` A U+0020 is allowed as an alternative, but its width varies by font. `[expert opinion: CLREQ §6.3.3]`
- **`text-autospace`:** adds this spacing in layout, without changing the text. `[vendor guidance: MDN-AUTOSPACE]` Newly available as Baseline 2025 (Chrome and Edge 140, Firefox 145, Safari 18.4). `[vendor guidance: BCD-AUTOSPACE]`
- **Contradiction, and it changes what you write.** The spec and MDN give the initial value as `normal`, and the CSSWG reaffirmed that on 2025-12-10 `[normative: CSSWG-12386]`. Browser data says shipped browsers still start at `no-autospace` `[vendor guidance: BCD-AUTOSPACE]`. **So set `text-autospace: normal` explicitly.** Do not assume the default gives you spacing.
- **Do not use the finer keywords yet.** `normal` and `no-autospace` work across engines. `ideograph-alpha`, `ideograph-numeric`, `auto` and `insert` are not in Chromium according to the same data. `[vendor guidance: BCD-AUTOSPACE]`
- **No double space.** The default behaves like `insert`, adding nothing where a space already exists `[vendor guidance: MDN-AUTOSPACE]`. So old content with literal spaces should not double up (per MDN; not tested across engines). For new content, do not type literal spaces. Older browsers then show no gap, which is acceptable: CLREQ gives a ceiling, not a minimum. Pick one convention and state it.
- `pre` and `code` already switch it off in the UA stylesheet. `[background: CSSWG-12386, meeting minutes]`
- **Words:** Western words do not split except at hyphenation points. `[expert opinion: CLREQ §6.1.4]` Long identifiers on a phone need `overflow-wrap: anywhere` as a last resort. `[working default]`

## Font stack: the shared code point trap

Browsers pick a font per character, so with a Latin font first, the code points Chinese shares with Latin (U+2014, U+2018 to U+201D, U+2026, U+00B7) come from the Latin font: narrow and on the baseline, not centred and two characters wide. CLREQ notes that Western-style ellipses and stops keep Western positioning `[expert opinion: CLREQ §4.1]`. The recipe below is `[derived, no authoritative source]`, so verify it by rendering a line with 「引號」“引號”……——.

```css
/* Letters and digits only for Chinese runs, so shared punctuation falls through to the Han font.
   "Latin full" is a second @font-face on the same file, with no unicode-range. */
@font-face { font-family: "Latin in zh"; src: url(latin.woff2) format("woff2");
             unicode-range: U+0020-007E, U+00C0-00FF; font-display: optional; }
:root { text-autospace: normal; }
:lang(zh) { font-family: "Latin in zh", "Noto Sans TC", "PingFang TC", "Microsoft JhengHei", sans-serif;
            line-height: 1.75; font-synthesis: none; }
:lang(en) { font-family: "Latin full", system-ui, sans-serif; line-height: 1.5; }
```

The system faces named are general knowledge for macOS and iOS and for Windows, not sourced here, so check them on your targets. For Hong Kong, pick an HK face. Do not list a mainland face first on a Traditional Chinese page.

## Font loading

Full CJK fonts cannot be sent as they are. Sizes read on 2026-11-05: Noto Sans TC Regular OTF 5.68 MB `[vendor guidance: NOTO-DIR]`, LXGW WenKai TC Regular TTF 15.3 MB `[vendor guidance: LXGW-REL]`. CJK fonts can exceed 10,000 glyphs, Latin fonts usually 100 to 1,000 `[vendor guidance: WEBDEV-FONT]`. Chinese webfonts stay rare largely because of size `[background: ALMANAC]`.

The spec must state all four of these.

**1. Subset.** WOFF2 only `[vendor guidance: WEBDEV-FONT]`. Choose by content:

| Text | Approach | Why |
|---|---|---|
| Fixed, known at build: headings, a logo word | Static subset built from the real strings | Smallest result |
| Changes: CMS, posts, schedule edits | `unicode-range` slices, or a system-font body | A static subset leaves new characters to a fallback font, mixing faces in one line |
| Long body in Chinese | System fonts are a real option | Nothing to load; often the honest choice |

```
pyftsubset NotoSansTC-Regular.otf --text-file=chars.txt --flavor=woff2 \
  --layout-features='*' --name-IDs='*'
```

Why those flags `[vendor guidance: FONTTOOLS]`: the default keeps `locl` but does not list `halt`, `chws` or `vert`; `--layout-features='*'` keeps them, or add only what you need. The default keeps only name IDs 0 to 6, which drops licence fields, so `--name-IDs='*'` keeps them. WOFF2 output needs the Brotli module. These flags come from the docs and were not run in this repo.

**2. `font-display`.** `optional` for body avoids layout shift, `swap` for brand or display, and mixing the two works `[vendor guidance: WEBDEV-FONT]`. `size-adjust` on a fallback reduces the shift from `swap` (Chrome 92, Firefox 92, Safari 17) `[vendor guidance: BCD-SIZEADJ]`. Preload ignores `unicode-range`, so preload at most one critical file `[vendor guidance: WEBDEV-FONT]`.

**3. Size budget.** State a number and how you will measure it. **No authoritative budget exists.** Working target: 150 KB or less of font bytes on first view. `[working default]` For scale, the median font file is about 35 KB across all sites and is not CJK-specific `[background: ALMANAC]`. Measure from DevTools Network filtered to Font, or the size of the built files. If nothing is built yet, write "target, not measured".

**4. Licence.** Read the font's licence file before you specify the font. `[vendor guidance: WEBDEV-FONT]`

- OFL fonts may be served with `@font-face`, from your own server or a service. `[vendor guidance: OFL-FAQ Q2.1, Q1.8]`
- **Subsetting counts as modification.** It is allowed, but a modified font may not keep a Reserved Font Name. The Functional Equivalence exception needs the same character coverage, so a subset does not qualify. `[vendor guidance: OFL-FAQ Q2.5 to Q2.8]`
- WOFF2 compression alone is not modification only if the font data is unchanged and metadata is intact, and tools do not automatically ensure that. `[vendor guidance: OFL-FAQ Q2.2.1, Q2.2.2]`
- Keep copyright and licence information in the font metadata, and ship the licence text with the font. `[vendor guidance: OFL-FAQ Q1.10, Q2.4]`
- This is a reading of the FAQ, not legal advice.

| Font | Licence file read 2026-11-05 | Subsetting note |
|---|---|---|
| Noto Sans TC | OFL 1.1; none named in the part read | Check the font's own metadata too |
| LXGW WenKai TC | OFL 1.1; none named | No rename needed on what was read |
| Inter | OFL 1.1; none named in the copyright line | No rename needed on what was read |
| IBM Plex | OFL 1.1, Reserved Font Name "Plex" | Per the FAQ, a subset needs a new name |
| Source Han Sans | OFL 1.1, Reserved Font Name "Source" | Per the FAQ, a subset needs a new name |

For anything else, including paid fonts, read its licence; do not extend this table from memory. Self-hosting is not automatically faster: test it. `[vendor guidance: WEBDEV-FONT]`

Avoid specifying `Inter` across the whole site by reflex. It is a fine font, and a default. If you pick it, say what about this brief calls for it.
