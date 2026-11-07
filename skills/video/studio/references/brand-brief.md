# Brand brief + brand guidelines (required whenever a product or brand is in the video)

The user's rule after the app-builder music video: every product or brand video starts with a brief and brand guidelines, like the research pack another AI tool made for that brand. That pack is why the film looked 1:1 like the brand's own marketing video: design, colors, even the font. No build starts without it.

## Two ways to get it (in stages, ask the user which; on a run, audit the site yourself and say so)

1. **The user's own research agent (for example ChatGPT).** Give the user the prompt below to paste, with the brand, the product URL and the reference video attached. It returns a pack (brief, audit, storyboard, moodboard). Read all of it before pitching.
2. **Claude does it.** Drive the live site in Chrome: computed styles, `@font-face` rules, the logo's DOM SVG, the product UI, the brand's official YouTube or campaign pages. Write the same sections into `BRAND-BRIEF.md` in the project folder.

Either way, then close the gaps with real assets (`references/brand.md`): font files, exact logo paths, a faithful UI rebuild.

## What the pack must contain

1. **Brand audit, observed vs. chosen.** A table of what was measured on the live site (each color with its hex and where it was read, e.g. logo fill, primary button, ink, backgrounds, CTA; each font with its job and weight) kept separate from creative choices. Two close values stay two values.
2. **Voice and lines.** The brand's real taglines, CTA wording and product phrases, quoted exactly.
3. **Motifs.** Recurring visual devices (headline casing, punctuation, grids, labels, framing of product shots, photography style).
4. **Official campaigns.** What the brand's own videos do (people, type, product proof), from its channel; what to keep, what to avoid.
5. **Asset register.** Logo master, font files, product screens, photos: each with source, status (have / need / stand-in) and who supplies it.
6. **The idea.** One takeaway, audience, hero, problem, payoff, and how the reference's craft translates to this brand (the reference gives the look and energy; the brand gives the facts).
7. **Claims check.** No invented metrics, testimonials or features; product proof only from real behavior.

## Research prompt (the user pastes it)

```
Prepare a brand brief and brand guidelines pack for a short video about <BRAND / PRODUCT> (<URL>).
1. Brand audit from the live site: measure every brand color (hex + where you read it: logo fill, primary action, ink, backgrounds, CTA, accents), every font with its job and weight, and save any font files you can. Keep observed facts separate from your creative suggestions.
2. The brand's exact taglines, CTA wording and product phrases.
3. Recurring visual motifs (headline style, punctuation, grids, labels, photography, how the product is framed).
4. Review the brand's official videos/campaigns: what they do, what to keep, what to avoid.
5. Asset register: logo master, fonts, product screens, photos, with source and status.
6. Attached is my style reference video: break down its craft (framing, type roles, overlays, transitions, pacing) and translate it to this brand without copying its subject.
7. One idea: takeaway, audience, hero, problem, payoff, a timed storyboard, and a claims check (no invented metrics or features).
Deliver it as markdown files plus a PDF.
```
