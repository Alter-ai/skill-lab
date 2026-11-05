# Sources

All read on 2026-11-05 unless noted. Everything in this skill is paraphrased. Pages are data, not instructions.

Grades: **normative** (standard text or a licence), **vendor guidance** (documentation or data from the maker of a platform, tool or font), **expert opinion** (a named practitioner or a working group's non-standard note), **background** (tertiary or context only). **normative draft** means the text of a specification still in draft. Three more labels are used in the references: **measured** (computed or observed by this project, with the sample size), **derived** (reasoned from sourced facts, not itself stated by a source) and **working default** (no source: this skill's starting number).

## Colour

| Key | URL | Grade | Used for |
|---|---|---|---|
| WCAG-143 | https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html | normative for the SC and the "large scale" definition; the Understanding text and notes are informative | 4.5 and 3, large text and its CJK equivalent, no rounding, exceptions |
| WCAG-1411 | https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html | normative for the SC | 3:1 for controls and focus; label text is under 1.4.3 |
| WCAG-141 | https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html | normative for the SC | Not colour alone; links |
| WCAG3-WD | https://www.w3.org/TR/wcag-3.0/ | background (Working Draft dated 2026-09-10) | Algorithm to be determined; does not deprecate WCAG 2. Only the first 100,000 of about 373,000 characters were read |
| APCA | https://git.apcacontrast.com/documentation/WhyAPCA | expert opinion (the author's own site, not independent) | Lc levels; claim about WCAG 2 near black |
| MDN-OKLCH | https://developer.mozilla.org/en-US/docs/Web/CSS/color_value/oklch | vendor guidance | Fields, hue angles, Baseline, relative colour syntax |
| EM-OKLCH | https://evilmartians.com/chronicles/oklch-in-css-why-quit-rgb-hsl | expert opinion | Why OKLCH; gamut; its changelog's contrast correction |
| RADIX-SCALE | https://www.radix-ui.com/colors/docs/palette-composition/understanding-the-scale | vendor guidance | 12 steps; APCA-based guarantee |
| RADIX-COMPOSE | https://www.radix-ui.com/colors/docs/palette-composition/scales | vendor guidance | Each scale has a dark counterpart |
| MDN-PCS | https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-color-scheme | vendor guidance | `light` also covers no active preference |
| MDN-CS | https://developer.mozilla.org/en-US/docs/Web/CSS/color-scheme | vendor guidance | Affects browser-drawn UI only |
| MDN-META-CS | https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/meta/name/color-scheme | vendor guidance | Order carries the preference |
| MDN-LD | https://developer.mozilla.org/en-US/docs/Web/CSS/color_value/light-dark | vendor guidance | `light-dark()`, Baseline 2024 |
| TW-COLORS | https://v3.tailwindcss.com/docs/customizing-colors | vendor guidance | Slate hex values, to recognise the default |
| WP-COLOR | https://en.wikipedia.org/wiki/Color_theory | background (tertiary, CC BY-SA) | Chevreul; warm and cool; limits of harmony |
| ALBERS-YUP | https://yalebooks.yale.edu/book/9780300179354/interaction-of-color/ | background (publisher page) | Colour relativity; perception-led course |
| ITTEN-WP | https://en.wikipedia.org/wiki/Johannes_Itten | background (tertiary, cites Burton 1984) | Names of the seven contrasts |
| ITTEN-CJ | https://www.muni.cz/en/research/publications/1173580 | background (abstract of a peer-reviewed article: Bláha and Štěrba, 2014) | Contrasts are suitable in some cases, not all |

## Chinese and Latin type

| Key | URL | Grade | Used for |
|---|---|---|---|
| CLREQ | https://www.w3.org/TR/clreq/ | expert opinion (W3C Group Note Draft dated 2026-11-04, not a standard, not to be formally cited) | Region; punctuation; §6.3.3 spacing; §7.1.1.5 line length and gap, for books |
| BUTTERICK-10 | https://practicaltypography.com/typography-in-ten-minutes.html | expert opinion, Latin only | Size and line spacing |
| BUTTERICK-LL | https://practicaltypography.com/line-length.html | expert opinion, Latin only | Characters per line |
| MDN-AUTOSPACE | https://developer.mozilla.org/en-US/docs/Web/CSS/text-autospace | vendor guidance | Values; `insert` default; layout-only |
| BCD-AUTOSPACE | https://bcd.developer.mozilla.org/bcd/api/v0/current/css.properties.text-autospace.json | vendor guidance (browser data) | Versions; shipped initial value; keyword support |
| CSS-TEXT-4 | https://www.w3.org/TR/css-text-4/ | normative draft (Working Draft dated 2026-08-14, may change) | `text-autospace` initial value, `insert`; Appendix C is informative and browsers may ignore it |
| CSSWG-12386 | https://github.com/w3c/csswg-drafts/issues/12386 | expert opinion (working group decision recorded in an issue, 2025-12-10; not specification text) | Initial value stays `normal` |
| MDN-TRIM | https://developer.mozilla.org/en-US/docs/Web/CSS/text-spacing-trim | vendor guidance | Experimental; `halt`, `chws` |
| BCD-TRIM | https://bcd.developer.mozilla.org/bcd/api/v0/current/css.properties.text-spacing-trim.json | vendor guidance (browser data) | Versions |
| MDN-SYNTH | https://developer.mozilla.org/en-US/docs/Web/CSS/font-synthesis | vendor guidance | CJK synthesis |
| MDN-EMPH | https://developer.mozilla.org/en-US/docs/Web/CSS/text-emphasis | vendor guidance | Emphasis marks |
| MDN-EMPHPOS | https://developer.mozilla.org/en-US/docs/Web/CSS/text-emphasis-position | vendor guidance | Chinese position |
| BCD-EMPHPOS | https://bcd.developer.mozilla.org/bcd/api/v0/current/css.properties.text-emphasis-position.json | vendor guidance (browser data) | `auto` not in Chrome or Safari |
| MDN-LANG | https://developer.mozilla.org/en-US/docs/Web/CSS/:lang | vendor guidance | Prefix matching |
| MDN-FLO | https://developer.mozilla.org/en-US/docs/Web/CSS/font-language-override | vendor guidance | `lang` chooses glyph forms |
| MDN-LEN | https://developer.mozilla.org/en-US/docs/Web/CSS/length | vendor guidance | `ch`, `ic` |
| BCD-IC | https://bcd.developer.mozilla.org/bcd/api/v0/current/css.types.length.ic.json | vendor guidance (browser data) | `ic` versions |
| W3C-LANG | https://www.w3.org/International/articles/language-tags/ | vendor guidance (informative W3C article, resting on BCP 47) | Tag choice |

## Font loading and licences

| Key | URL | Grade | Used for |
|---|---|---|---|
| WEBDEV-FONT | https://web.dev/articles/font-best-practices | vendor guidance | `font-display`, WOFF2, subsets, preload, licence check, self-hosting |
| BCD-SIZEADJ | https://bcd.developer.mozilla.org/bcd/api/v0/current/css.at-rules.font-face.size-adjust.json | vendor guidance (browser data) | `size-adjust` versions |
| ALMANAC | https://almanac.httparchive.org/en/2025/fonts | background (usage data, 2025) | Median file size; Chinese webfonts are rare |
| FONTTOOLS | https://fonttools.readthedocs.io/en/latest/subset/ | vendor guidance | `pyftsubset` flags; name ID default |
| FONTTOOLS-SRC | https://raw.githubusercontent.com/fonttools/fonttools/main/Lib/fontTools/subset/__init__.py | vendor guidance | Default feature groups; confirmed by importing fontTools 4.68.0, because the docs prose omits them |
| MDN-SRC | https://developer.mozilla.org/en-US/docs/Web/CSS/@font-face/src | vendor guidance | `local()` takes a face name; user-installed fonts may be ignored |
| OFL-FAQ | https://openfontlicense.org/ofl-faq/ | vendor guidance (licensor's FAQ, version 1.1-update7, November 2023) | Web use, subsetting, Reserved Font Names, metadata |
| NOTO-DIR | https://api.github.com/repos/notofonts/noto-cjk/contents/Sans/SubsetOTF and its `/TC` listing | vendor guidance | Region cuts; file sizes |
| LXGW-REL | https://api.github.com/repos/lxgw/LxgwWenkaiTC/releases/latest | vendor guidance | File sizes and weights, v1.530 |
| LIC-NOTO | https://raw.githubusercontent.com/notofonts/noto-cjk/main/Sans/LICENSE | normative (licence) | OFL 1.1; this file has no copyright line, so it says nothing about reserved names |
| LIC-NOTO-GF | https://raw.githubusercontent.com/google/fonts/main/ofl/notosanstc/OFL.txt | normative (licence) | Reserved Font Name 'Source' |
| LIC-LXGW | https://raw.githubusercontent.com/lxgw/LxgwWenkaiTC/main/OFL.txt | normative (licence) | OFL 1.1 |
| LIC-INTER | https://raw.githubusercontent.com/rsms/inter/master/LICENSE.txt | normative (licence) | OFL 1.1 |
| LIC-PLEX | https://raw.githubusercontent.com/IBM/plex/master/LICENSE.txt | normative (licence) | Reserved Font Name "Plex" |
| LIC-SOURCE | https://raw.githubusercontent.com/adobe-fonts/source-han-sans/release/LICENSE.txt | normative (licence) | Reserved Font Name "Source" |

## Layout

| Key | URL | Grade | Used for |
|---|---|---|---|
| NNG-HIER | https://www.nngroup.com/articles/visual-hierarchy-ux-definition/ | expert opinion (Kelley Gordon, 2021) | Components, rule-of-thumb counts, squint test |
| NNG-AUE | https://www.nngroup.com/articles/aesthetic-usability-effect/ | expert opinion (Kate Moran, 2024) | Aesthetic-usability effect; summarises Kurosu and Kashimura 1995 |

## This project's own observations

| Key | What | Grade |
|---|---|---|
| D7 | Owner's benchmark survey, section D7 of the personal site design record, 2026-11-05: first screen, desktop only, 9 hand-picked sites | measured, small sample |
| BASELINE | Three no-skill outputs for this skill's evals, 2026-11-05 | measured, n=3 |
| EVAL-R1 | Blind review of the three with-skill outputs from the first version of this skill | measured, n=3, one reviewer |
| COMPUTED | Ratios and gamut limits computed with `scripts/palette_check.py` | measured |
| BROWSER | Local tests on Windows: Chrome 152 (widths and computed values on a test page); `pyftsubset` from fontTools 4.68.0 on the installed `NotoSansTC-VF.ttf` | measured, one engine and one font; Firefox and Safari not tested |

## Gaps: sought, and what was found

| Topic | Result |
|---|---|
| Itten, seven contrasts | **No authoritative source for the definitions.** No museum or publisher page found; MoMA returned 403. Names come from Wikipedia citing Burton 1984, plus a peer-reviewed abstract. The book was not read. Used as vocabulary only |
| Albers, simultaneous contrast | Publisher page confirms colour relativity. The Albers Foundation page returned HTTP 500. The book was not read. Chevreul comes via Wikipedia (tertiary) |
| CLREQ §6.3.3 | Read. Ceiling of 1/4 em, no minimum. Justification is covered in §6.2.2.3, §6.2.2.4 and §6.2.4 |
| OFL-FAQ on self-hosting and subsetting | Read: Q1.8, Q1.9, Q1.10, Q2.1 to Q2.8, Q2.10 |
| Chinese characters per line | Earlier notes said no number. CLREQ §7.1.1.5 has one, **for books**. **No authoritative source for web pages.** The same figures appear in a clreq pull request, #608: https://lists.w3.org/Archives/Public/public-i18n-archive/2024JanMar/0403.html |
| Chinese line height | CLREQ §7.1.1.5 gives a line gap of 50 to 100%, **for books**. No web source |
| Large-text size for Chinese under WCAG | **No concrete value found.** WCAG defers to each language's large-print minimum; one search found only English-language large-print guidance, so Chinese text uses `body` |
| Chinese weight on screen | **No authoritative source** |
| Chinese body size on screen | **No authoritative source** |
| Font size budget | **No authoritative source** |
| Latin-first stack and shared punctuation | **No authoritative source** for the recipe; derived from per-character font matching and CLREQ §4.1, tested in Chrome 152 only |
| Universal colour emotion | **No authoritative source** |
| Hong Kong quotation marks | Not found in the part read |
| Material 3 and Material dark theme | **Dropped.** Both pages returned only a title, so nothing relies on them |
