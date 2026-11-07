# On brand, 100% (the app-builder film method)

The user's favorite thing about an app-builder music video: it looked 1:1 like that brand's own marketing video, in design, brand colors, even the font. Two things made that happen:
- **A brand audit before the build (a research pack from another AI tool).** It read the live site and wrote down the palette (logo orange #FF6A00, action orange #FF773C, ink, warm white, cobalt, charcoal CTA), the fonts and their jobs (a custom display face at weight 600 for headings, Geist for UI), the site's lines (its tagline and its "Start building" CTA) and its motifs (sentence-case headlines, dot grid, bracketed labels, white prompt field). Ask the user for such an audit, or do one yourself, as step 0. Use a brief's brand facts; take the look and energy from the user's reference.
- **Real assets for everything the audit could only name.** The steps below closed its gaps (the font files it couldn't download, the logo, the product UI).

For any video about a brand or product:

1. **Fonts: the real files.** Read the site's `@font-face` rules in the browser (`document.styleSheets`, `document.fonts`) and download the actual woff2 files (the brand's display face came from the app domain's static folder; the marketing domain returned empty files, so try the app domain too). Also note the UI font of the product itself (that product's prompt field used Wix Madefor Text, not the heading font).
2. **Colors: computed, not eyeballed.** Read computed styles from the live page: logo fill, primary action button, ink, backgrounds, secondary accents, idle/active states (app-builder brand: logo #FF6A00, action #FF773C, idle send #FFE8DB, ink #0F0E0E). Keep distinct values distinct; don't merge two oranges into one.
3. **Logo: exact vector paths.** Take the SVG paths from the site's header logo in the DOM and draw them in code. Never let an image model draw a logo. If the full wordmark can't be extracted, set it in the brand font as a clearly labeled stand-in and ask the user for the official file.
4. **The brand's own devices.** Look for small signatures and reuse them: that brand's headings end in an orange full stop ("Hi there."), so every slam in the film ended with one. Use their real product lines ("What will you build next?" and its tagline).
5. **Product UI rebuilt faithfully.** Screenshot the real product surface and rebuild it in code at a legible scale (same layout, controls, fonts, colors, states). Label it a rebuild, not a capture, and never let an image model invent the interface.
6. **Keep a tokens file** (colors, fonts, lines, logo paths, source URL and date) as the single source every shot reads from.
7. **Honesty:** for a spec piece, say "spec piece, not affiliated" in the post, and swap stand-ins (wordmark, fonts license) for official masters before wide release.

## When the owner doubts the typeface: a font test, not an argument

On the Take One launch film the owner said the type "gives the AI look away" and asked to "do some tests and select the best font". What worked:

1. Put the type behind one switch in the page (a table of candidates: family, weight, size factor, letter-spacing factor) chosen by a URL parameter, so every candidate renders the real frames, not a specimen. Keep the logo and the wordmark out of the switch: they are the brand, not the film's text.
2. Pick six to nine candidates in clearly different directions (the current face, a serif, a typewriter, a poster face, a pixel face that matches the icons, wider and narrower cuts of the current family), not six near neighbours.
3. Size every candidate so the film's longest headline is the same width in each. Otherwise wide faces look weak and narrow ones look loud.
4. Render the same three frames in each (the first frame, a busy middle frame, the end card), label the rows with one big letter and a two-word description, and send ONE image. Ask for a letter.
5. Expect the first choice to survive: on ours the owner called the original "still the best by far" after the first sheet of six, asked for a second sheet that went further, and then asked which face an admired film uses. A test that ends on the first choice is not wasted: the doubt is gone.
6. Free faces with real weights come from Google Fonts (`css2?family=...` with a browser user-agent returns woff2 links); keep the licence file with the film.

### Naming the typeface in a reference film

When the person asks "what font is this?", do not answer from memory: three confident guesses on ours (two paid faces and a popular free one) were all wrong, and the right answer came only from looking.

1. Find the frames where the type is largest (a tile of the first forty frames usually shows a zoom) and crop them at full resolution. Small captions hide the details that decide it.
2. Write down what the letters do: one-storey or two-storey a and g, the tail of y and j (straight, curved, turned with a flat end), the foot and the top of t, round or square dots, how c, e and s are cut, the notch where u and d meet their stems.
3. Render candidates with the same words beside the crops (a page of `@font-face` rows, screenshotted) and compare letter by letter. Free families come from Google Fonts and Fontshare; for a paid family, the designer's own site often has a free weight or trial, or specimen pictures that settle it.
4. Read the licence before proposing it. A weight that is free to use in a film may still not be redistributed, so its file stays in the film's folder and never goes into a shared repository or skill.
5. Then show the person their own frames in that face next to the current one. What made the reference feel hand-made is often how the type is used (small, sparse, tight, moving with the camera), not the face.
