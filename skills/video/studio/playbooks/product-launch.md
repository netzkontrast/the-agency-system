# Playbook: Product launch

**Use when** a film launches a product, an app or a feature, on brand, with the real product shown working:
30–60 s for a feed, plus cut-downs. **Not when** there is nothing to show yet and the film is a statement
(`explainer.md` with `references/styles/manifesto.md`), only a logo sting is wanted (`brand-title.md`), or a finished
launch film needs a shorter cut (`teaser-cutdown.md`).

## Inputs to collect

- Product name, the one line only this product can say, the action and **the real link** (none given → end on the
  name and say the link is missing).
- Access to the product: the person logs in in their own browser (never create accounts or handle codes), or a public
  demo; plan limits (AI credits, export).
- Brand pack (`references/brand-pass.md`, `references/brand-brief.md`): real font files, computed colours, logo
  vector paths, tokens file.
- Hero example: one product state, one set of people, used in every shot.
- Competitors (the strategist's study, `references/launch-film.md`), audience, platforms, ratios, voice or not.
- What spend is allowed for pictures, moving shots, voice, music (`references/services.md`).

## Defaults

| Item | Default |
|---|---|
| Length | 30–60 s feed; product and its result fill at least half |
| Aspect / size | 16:9 1920×1080 master; 9:16 and 4:5 recomposes planned at the pitch (`references/vertical.md`) |
| fps | 60, master `SUB=8`; 30 fps copy for Instagram |
| Medium | canvas around real captures: `bash <studio>/tools/new-project.sh <dir> --medium canvas --duration 45` |
| Style candidates | the brand's own look first; then `references/styles/explainer.md`, `monochrome-launch.md`, `chrome-showreel.md`, `dark-premium.md`, `editorial-hud.md` (with real footage) |

## Phase deltas

| # | Phase | What changes |
|---|---|---|
| 1 | Brief | strategist: audience, takeaway, claims check, brand pack, `COMPETITORS.md` (contact sheets via `bash <studio>/tools/contact-sheet.sh <video>`), and the two lines "what this category always does / where we differ". |
| 2 | Route | real product route (`references/real-product.md`) for every product beat; code for everything around it. Pick the way to explain from `references/directed-look.md` and name it. |
| 3 | Pitch | concept check in full (`references/concept-check.md`), page-or-picture counts, the order from `references/launch-film.md` (hook 3–5 s → name ~1 s full frame → working on one example → features on that example → at scale → end card 4–5 s), services and price. |
| A | Capture | after pitch approval: drive the product into each storyboard state, capture at fixed window size (phone plates at deviceScaleFactor 3), save to `assets/real/<beat>`; component macros at 3× for the 2–3 key interactions. Lock the camera path before capturing; recapture after any reframe. |
| 4 | Map | VO script (`python3 <studio>/tools/vo.py vo.json`) or the music's measured structure (`bash <studio>/bin/studio songmap track.wav`): drop on the reveal, last hit on the end card. |
| 6 | Test section | three moments, not the opening only: the name reveal, the strongest pair of features, the turn (`references/directed-look.md` §7). |
| 11 | Deliver | + brand posts per platform (`references/captions.md`, "The brand's own launch posts"), + 15–30 s cut, + vertical. |

## Team & fan-out

Producer, **strategist** (always), director, critic, art-director (brand tokens owner), 1–2 animators (chapters:
hook+name · working · features · scale+end), integrator, qa-operator, reviewer (with the agency-bar paragraph),
sound, copywriter, vertical-editor.

## Craft rules specific to this type

1. **One hero example for the whole film**; the people come back near the end if it opens on them.
2. **Show the real thing very close:** one control, one row, one typed line fills the frame with a large cursor;
   never a whole screen (that is a screenshot). Component macro: lift at 3–5×, perform, show the result, spring
   back to its real rect (`references/real-product.md`).
3. **The content inside the product is the story:** fill it with the brand's kind of content (faces, photos), not
   bare default UI. Let the product's own AI make the "magic" beats so the claim is literally true.
4. **Nothing on screen the product does not do;** only real integrations; personal data blurred; illustrative
   figures labelled "Example data".
5. Never repaint over the product's UI to change what it says; never let an image model draw a logo or UI.
6. **No layout more than ten seconds**; no layout back more than twice in a row; each repeat of a pattern gets its
   own treatment (`references/launch-film.md`).
7. **First frame carries the first words and really moves;** the big word lands on the music's downbeat.
8. End card: mark, name, one line, the given link from its first second; held ≥ 3 s.
9. Nothing inside a frame cut by the frame: measure crops with `python3 <studio>/tools/content-box.py`.
10. Captures shown at ≤ native pixels (`plate-audit` UPSCALE ≥ 1.2× is a FAIL).

## Gates & bar

- Battery + `text-audit`, `edge-audit`, `plate-audit`, `audit-faces.mjs` (each delivered aspect), `audio-check`.
- Brand pass check: tokens file used everywhere; fonts are the real files; colours computed.
- Honesty list in the delivery note: every illustrated screen, every rebuilt (not captured) UI.
- **Reviewer brief includes the agency-bar paragraph** (`references/reviewer-brief.md`). Locked: brand look, product
  line, link, the real captures.
- **8/10 here** (`references/quality-checklist.md`, agency bar): the real thing on screen in the explaining part, no
  list as matching frames, two tones and one accent, the best picture at full frame, words read at 360 px, proof
  before 50 % of the runtime.

## Pitfalls

- The explaining part in the default look (cards, pills, one panel per job); two restyles of the same skeleton.
- Opening on the finished result when the film's turn is its reveal.
- Dropping the narrator in the short cut without asking.
- Capture tab hidden (rendering stops); stray keystrokes firing product shortcuts; plates blended with fixed-size UI.
- A link, price or date nobody gave.

## Deliverables

Master `out/<product>-launch.mp4`, `-9x16`, `-4x5`, 15–30 s cut, 30 fps Instagram copy, `.srt`, brand posts
(`POSTS.md`), `COMPETITORS.md`, tokens file, list of what was created in the person's account, honesty list, gate
and review reports, review room.

## Checklist

- [ ] Brand pack + tokens; competitors studied
- [ ] Hero example fixed; storyboard as product states
- [ ] Captures at native size, camera path locked first
- [ ] Ban list + way-to-explain named
- [ ] Faces/text/edge/plate audits clean in every aspect
- [ ] Agency bar met; honesty list written; real link on end card
- [ ] Account cleanup told to the person
