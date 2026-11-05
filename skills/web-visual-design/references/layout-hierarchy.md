# Layout and hierarchy

Read this before writing a layout spec or reviewing a page's structure. Tags give the evidence grade and a source key from `sources.md`.

## Where hierarchy comes from

Three things, in practice `[expert opinion: NNG-HIER]`:

- **Value and saturation contrast** against the surroundings. Hue alone does little.
- **Scale.** Larger reads as more important.
- **Grouping.** Proximity and white space show what belongs together; borders and containers are for when spacing is not enough.

## Count it

Rules of thumb from one practitioner source, stated as guidelines to adapt, not laws. `[expert opinion: NNG-HIER]`

| Item | Rule of thumb |
|---|---|
| Type sizes | No more than 3 (small, medium, large). Examples: body 14 to 16px, subhead 18 to 22px, heading up to 32px |
| Large elements on a screen | At most 2 |
| Contrast treatments | No more than 3 in a complex design |
| Colours | About 2 primary, 2 secondary |

Contradiction: many real type scales have five or six steps, and a display treatment often goes well past 32px. This skill's rule is to **state the count and defend anything past 3**. `[working default]` A ratio-based scale produces sizes; it does not justify using them all. `[derived]` In the no-skill baseline, specs listed five to seven sizes, and none stated a limit on the count. `[measured: BASELINE, n=3]`

**Choose scale and spacing from the content.** Say how many steps, what each is for, and why this content wants that. `[working default]` These differ on purpose:

- Dense tables read at a glance: small size range, tight rows, and group separation doing the work.
- Long reading: spacing tied to the body line height, so vertical rhythm comes from the text.
- Phone lists with tap targets: row height set by the target, then spacing fitted around it.

Inside a group must be clearly tighter than between groups. Tighten heading to content, and give important elements more room `[expert opinion: NNG-HIER]`. How large the jump is depends on density. `[working default]`

Do not default to doubling from 8. Every run of an earlier version of this skill copied the same 8/16/32/64 from its example, on unrelated briefs. `[measured: EVAL-R1, n=3]`

## Reading column

- Latin benchmark columns are 644 and 607px wide, with line-heights of about 1.65 and 1.75. `[measured: D7, n=2 each, not a law]` Chinese figures are in `references/typography-zh-en.md`.
- State widths in `em` for Chinese and `ch` for Latin. `[derived from MDN-LEN]`

## Objects on the page

List the objects this brief actually has and give each a type, colour and spacing rule. Without this, a spec describes a page's look but not how to build its contents; no-skill runs had these rules more often than runs of an earlier version of this skill `[measured: EVAL-R1, n=3]`. Skip what the brief does not have. Prompts for common ones, all `[working default]` unless tagged:

- **Tables.** Which size, how figures align, how rows separate, what happens below the column width. Tabular figures need `tnum` kept when subsetting `[measured: BROWSER]`.
- **Code blocks.** Size, background, colour count, overflow. **A width claim must fit the stated column:** N `ch` at the code size plus padding must not exceed the column. Monospace faces are often near 0.6em per character, so 100ch at 14px needs about 840px; measure your font `[derived from MDN-LEN]`.
- **Syntax colours.** Do not use the signals links use, such as underline or the link colour, for non-links `[derived]`. Check them in a second tokens file.
- **Schedules and timelines.** Time column width, long title wrapping, how the current or next item is marked without colour alone `[normative: WCAG-141]`.
- **Portraits and images.** Crop ratio, size, the fallback when one is missing, treatment in dark mode.
- **Badges and tags.** One meaning each, when one does not appear, and text or an icon beside the colour `[normative: WCAG-141]`.
- **Buttons.** How many fill styles, label pair as `body` `[normative: WCAG-1411]`, target size for the stated device.

## Squint test

Blur the page and see which shapes and groups remain, without reading. NN/g applies blur radii of 5, 10 and 20px: the first two show the intended structure, and at 20px one strongly coloured item emerged as an unintended focal point. `[expert opinion: NNG-HIER]`

- **With a rendered page:** run `document.documentElement.style.filter = "blur(10px)"` in the console, repeat at 5 and 20, and write down what you see. `[derived from NNG-HIER]`
- **With a spec only:** give your prediction, labelled `predicted, not rendered`. Do not claim a pass when nothing was rendered. `[working default]`

Say what shows first, second and third for this page, and what might compete. Use your own words about your own shapes. If the first thing you see is not what the page is for, change that element's value or size, not its hue. `[derived from NNG-HIER]`

## One memorable element

Spend boldness once. In the owner's benchmarks, three sites each rely on one element visible at a glance, with everything else restrained. `[measured: D7, n=3, a small hand-picked sample]` `frontend-design` gives the same direction.

Say what it is, where it appears, what it uses up (the accent, the display size) and what is held back for it. Check by removing it: if the page could then be anyone's, it was doing its job. Tie it to the subject. A generic flourish, such as a gradient or a large statistic, does not count. `[working default]`

## Benchmark observations

First screen, desktop only, 2026-11-05, hand-picked sample of 9, phones and scrolled views not yet seen. Directional only. `[measured: D7]`

| Site | One memorable thing | Values read | Takeaway |
|---|---|---|---|
| Rauno Freiberg | Big stepped type with one flat yellow circle | Light grey `#EDEDED` | One bold gesture for the site |
| Filippo Valsorda | One print-style illustration as signature | Raleway, Bitter, Source Code Pro | A security expert can show personality with one image |
| Josh W. Comeau | Illustrated rainbow | Dark ground, pink category labels | Illustration builds recognition |
| Emil Kowalski | Extremely restrained plain text | `#FDFDFC`, `#21201C`; 14/23px; 644px column | Space and slight colour tuning can be enough |
| Paco Coursey | Screenshot did not capture it | `#1A1A1A`; 16/28px | Loose leading; loads a paid font, out of budget |
| Brittany Chiang | Dark blue with glow | `#0F172A`, Inter, heading 48/700, 607px | Do not copy: this exact mix is the default to avoid |
| Anthony Fu | Dotted black background | Inter 36/800 | Information architecture for open source maintainers |
| Scott Helme | Hero photo, image cards | Dark ground | Visually plain in this sample, a hypothesis only |
| Simon Willison | Content density, not visuals | Dark purple bar, two dense columns | Wins by publishing frequency and content |

Design rules drawn from them, all from this small sample `[measured: D7]`:

1. One memorable element for the whole site.
2. Narrow column and loose leading; looser for Chinese, and test with real text.
3. Avoid common defaults: Tailwind's default dark blue, Inter everywhere, glow backgrounds, hero photo with stock images.
4. Free-licence fonts only when there is no font budget.

## Attractive is not usable

Attractive products are rated easier to use than they are, and people forgive small problems in them. Kurosu and Kashimura (1995, 252 participants) found appeal correlated more with perceived than with measured ease of use. It masks small problems in testing, and it does not rescue large ones. `[expert opinion: NNG-AUE, summarising the study]`

So passing this skill's checks shows that the listed conditions are met. It does not show that the design is good or that the page works. Run real tasks and watch what people do, not what they say about the look. A person still makes the final call on taste. `[derived]`
