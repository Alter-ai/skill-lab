# Layout and hierarchy

Read this before writing a layout spec or reviewing a page's structure. Tags give the evidence grade and a source key from `sources.md`.

## Where hierarchy comes from

Three things, in practice `[expert opinion: NNG-HIER]`:

- **Value and saturation contrast** against the surroundings. Hue alone does little.
- **Scale.** Larger reads as more important.
- **Grouping.** Proximity and white space show what belongs together; borders and containers are for when spacing is not enough.

## Count it

These are rules of thumb from one practitioner source, stated as guidelines to adapt, not laws. `[expert opinion: NNG-HIER]`

| Item | Rule of thumb |
|---|---|
| Type sizes | No more than 3 (small, medium, large). Examples: body 14 to 16px, subhead 18 to 22px, heading up to 32px |
| Large elements on a screen | At most 2 |
| Contrast treatments | No more than 3 in a complex design |
| Colours | About 2 primary, 2 secondary |

Contradiction: many real type scales have five or six steps, and a display treatment often goes well past 32px. This skill's rule is to **state the count and defend anything past 3**: 3 working sizes, plus at most one for the memorable element, plus at most one for metadata. `[working default]` A ratio-based scale produces sizes; it does not justify using them all. In the no-skill baseline, specs listed five to seven sizes, and none stated a limit on the count. `[measured: BASELINE, n=3]`

Write it like this, with your numbers:

> 3 sizes + 1 display. 28 heading, 18 sub, 16 body; 56 only for the page title. 2 weights. Nothing else appears.

**Spacing is a rule, not a list.** Name the base step, the number of steps in use, and how they map to grouping. Inside a group must be clearly tighter than between groups: tighten heading to content, and give important elements more room `[expert opinion: NNG-HIER]`. Use about a 2:1 or stronger jump between levels. `[working default]`

> Base 8. 4 steps: 8 inside a row, 16 inside a group, 32 between groups, 64 between sections. Each level at least doubles.

## Reading column

- Narrow column, loose leading: Latin benchmark columns are 644 and 607px wide, and line-heights are about 1.65 and 1.75 `[measured: D7, n=2 each, not a law]`. Chinese numbers are in `references/typography-zh-en.md`.
- State widths in `em` for Chinese and `ch` for Latin.
- For code and tables, say how they break out of the column; a table in a text column is the usual failure.

## Squint test

Blur the page and see which shapes and groups remain, without reading. NN/g applies blur radii of 5, 10 and 20px: the first two show the intended structure, and at 20px one strongly coloured item emerged as an unintended focal point. `[expert opinion: NNG-HIER]`

**With a rendered page:** in the browser console run `document.documentElement.style.filter = "blur(10px)"`, repeat at 5 and 20, and write down what you see. Tools like `webapp-testing` can screenshot this.

**With a spec only, nothing rendered:** write the prediction and label it `predicted, not rendered`. Do not write "passes the squint test" when nothing was rendered.

Required form:

> Squint (predicted, not rendered): at 10px you see (1) the dark title block top left, (2) one accent bar, (3) two grey columns. The accent is the only saturated shape. At 20px, nothing else should compete; the risk is the sticky button, so it stays neutral until the hero scrolls away.

If the first thing you see is not the first thing the page is for, change the value or size of that element, not its hue.

## One memorable element

Spend boldness once. In the owner's benchmarks, three sites each rely on one element visible at a glance, with everything else restrained. `[measured: D7, n=3, a small hand-picked sample]` `frontend-design` gives the same direction. Here it has to be stated in a checkable form:

> Memorable element: X. It appears in N places and takes Y (the accent, the display size). Held back so it can stand out: A, B, C.

Check: take it away. If the page could be anyone's, you have the right element. If nothing changes, it was not doing the job. Tie it to the subject. A generic flourish, such as a gradient or a large statistic, does not count.

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

Design rules drawn from them, all from this small sample:

1. One memorable element for the whole site.
2. Narrow column and loose leading; looser for Chinese, and test with real text.
3. Avoid common defaults: Tailwind's default dark blue, Inter everywhere, glow backgrounds, hero photo with stock images.
4. Free-licence fonts only when there is no font budget.

## Attractive is not usable

Attractive products are rated easier to use than they are, and people forgive small problems in them. Kurosu and Kashimura (1995, 252 participants) found appeal correlated more with perceived than with measured ease of use. `[expert opinion: NNG-AUE, summarising the study]` It masks small problems in testing, and it does not rescue large ones.

So passing this skill's checks shows that the listed conditions are met. It does not show that the design is good or that the page works. Run real tasks and watch what people do, not what they say about the look. A person still makes the final call on taste; say so rather than certifying quality.
