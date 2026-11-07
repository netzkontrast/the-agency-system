# Real product route (show, don't tell)

For any video about a product, the most convincing frame is the real product doing the thing. Code-drawn UI copies read as mockups; the real UI reads as proof. Use the real product for every beat that shows the product, and code for everything around it.

## The content inside the product is the story

The product being real is not enough; what's *in* it must show the story. A whiteboard-product film's first versions showed a real board full of text stickies, and the user's verdict was that nothing in it was visual: the hook asked "what if our plants could text us?", and a viewer would want to see an app being planned around that question, in pictures. That product's own marketing shots are full of faces, photos, video thumbnails, emoji, personas and journeys.
- **Study the brand's own product imagery first** (their homepage and feature-page screenshots): what kind of content fills their product, how their cursors and name tags look (a whiteboard product: big pastel pill tags with an outlined arrow), how dense and colorful it is. Match that, not the bare default UI.
- **Answer the hook visually within seconds.** If the hook is "plants that text you", the first reveal shows plants and a phone with a plant's text, not words about it.
- **Plan an image pack at the pitch:** moodboard and inspiration photos, a persona with a face, the product shot, app screens, packaging or launch visuals, anything a real team would pin while building the thing. Generate them (Nano Banana in the Higgsfield web UI with Unlimited on, or the user's ChatGPT) and place them in the product; if the product's own AI can generate images, prefer that, since it's more show-don't-tell.
- **Every layer of the story should be visually different** (photos, then clusters, then a flow, then screens, then a launch shot), so the eye gets something new at each beat.

## Steps

1. **Access.** The user signs up (free plan is fine) or logs in, in their own Chrome. Claude never creates accounts with the user's email or handles verification codes on its own. Ask what plan limits apply (AI credits, board count, export).
2. **Story first, then build it for real.** From the approved storyboard, list each beat as a product state ("30 messy stickies", "AI clusters them", "flow generated"). Drive the product with Claude in Chrome to create exactly those states. Use the product's own AI/automation for the "magic" beats where the plan allows, so the claim is literally true.
3. **Capture.**
   - Screenshots of each state at a fixed window size, at the zoom levels the film needs (resize the window large, hide sidebars/toolbars when the product lets you, keep the product's chrome when it helps recognition).
   - Short screen recordings of the moving moments (AI sorting, generation, collaboration). GIF/record tools in Chrome MCP, or a sequence of screenshots at fixed intervals.
   - Save to the project's `assets/real/` with the beat name.
4. **Composite in code.** The captures are plates. Code adds camera moves (zoom, push, nested zooms between states), cursor characters, highlight rings, type, sound hits and the payoff. Never repaint over the product's own UI to change what it says.
5. **Honesty.** Caption states it: "every frame is the real product; the camera, cursors and sound are code." Don't show features the plan or product doesn't have. Blur or avoid personal data (emails, avatars, other boards) in every capture. Any illustrative figure (sample revenue, a demo balance, a made-up chart) carries a visible **"Example data"** label on screen. Show only real integrations: every partner logo, connector and "works with" chip must exist in the product today.
6. **Clean up.** Tell the user what was created in their account (boards, files) so they can keep or delete it.

## The component macro (launch-video grammar)

The move that makes a UI launch feel premium: lift **one real control** out of the product and make it the whole frame for a beat.
1. **Capture it big.** Screenshot the control at `deviceScaleFactor: 3` (Playwright or the Chrome tool with the window zoomed), cropped tight: a toggle, the prompt box, a pricing switch, the send button.
2. **Lift it onto a clean field** (the brand's background colour, nothing else) at **3-5x** its in-product size. At 3x capture it stays native up to about 3x on a 1080p frame.
3. **Perform the interaction** on the lifted control: type into it one character per frame-tick, flip the toggle, press the button (a 0.95 scale dip on `snappy`, then release).
4. **Show the result state** there, still big: the answer appearing, the toggle's effect, the confirmation.
5. **Return to the full UI**: the control springs back to its real rect in the product screenshot (a shared element across the handoff, `motion-kit.md`), and the full interface is revealed around it.
The viewer learns one interaction perfectly instead of scanning a whole screen. Use it for the 2-3 interactions the story turns on, not every beat.

## Why

Proposed for an infinite-zoom video of a whiteboard product (Sep 2026): the first pitch redrew the product in code. The user's direction: show, don't tell, with the real product; it's what makes product videos amazing.

## Proven technique: capture the product's own canvas (whiteboard product, Sep 2026)

- **Look for an in-page SDK first.** That product's board page exposed a global board object (create stickies/frames, set the viewport), so the board was built and the camera driven by script from the Chrome tool.
- **Grab the render surface, not screenshots.** That product's main canvas element was WebGL with `preserveDrawingBuffer: true`, so `canvas.toBlob()` gives native 2x frames (3840x1688) with no UI chrome. Check `getContextAttributes()` on any canvas-rendered product.
- **Getting frames to disk:** a localhost upload was blocked (Chrome local-network permission) and macOS `screencapture` only saw the wallpaper (no Screen Recording grant). What worked: pack PNGs + viewport JSON into one binary bundle per ~40 frames (records of: 4-byte big-endian name length, name, 4-byte big-endian data length, data; each PNG followed by its viewport JSON) and download it from the page with a blob link (user approves downloads once, and "allow multiple downloads" once), then unpack locally with `scripts/unbundle.py`.
- **The tab must stay visible.** A covered or minimized window reports `visibilityState: hidden`, rAF stops and the product stops rendering; ask the user to keep it in front during capture.
- **Zoom ladder for an infinite zoom:** capture frames log-spaced along the camera path (2% zoom steps, ~250 frames), each about 1.3x wider than the film's view (just enough for 16:9 inside the capture's aspect), and keep them at full resolution. The film draws the smallest plate that covers the camera. Real pixels at every zoom, smooth motion from code.
- **Lock the camera path before capturing, and recapture after any reframe.** v4 of the whiteboard-product film re-framed three shots after capture, so those moments borrowed wider plates and enlarged them; the user saw it at once ("why is user flow out of focus and pixelated"). Also don't downscale plates to save memory.
- **Never blend plates that contain fixed-size UI.** Product chrome drawn at constant screen size (a diagram label chip) sits at a different place and size in every plate, so a crossfade prints a ghost copy. A dense ladder needs no blending.
- **Let the product's AI make the content.** The clusters, flow, roadmap and wireframes were real output of the product's own AI from real prompts; the film shows those prompts verbatim (prefixes). Free plans can refuse a feature (wireframes): take the AI's offered fallback and say so.
- **Mind stray keystrokes.** Typing into the canvas instead of the prompt fires the product's shortcuts; click the input and verify focus with a zoom before typing.
- **Async plates:** `renderFrame` can return a promise (the export/frames scripts await it), and the page's own autoplay preview must not run under automation (`navigator.webdriver`), or it paints over exported frames.
- **Canvas-only fonts** must be requested with `document.fonts.load(...)` before READY; `document.fonts.ready` alone lets them fall back to Times.

## Getting generated images into the product (whiteboard product, Sep 2026)
- Generate in the Higgsfield web UI (Nano Banana Pro, Unlimited on), read the results with the free MCP `show_generations`, and pass their public CloudFront `rawUrl` straight to the product: the product's SDK image call (`createImage({url, x, y, width})` in that case). No downloads or uploads needed.
- Keep a local copy (`imgpack/`) for the record and for previews.

## Keeping the capture session alive
- **One tab.** Opening another tab in the same Chrome window (Higgsfield) makes the product tab `hidden`: it stops rendering and SDK calls that wait on a frame hang. Close the other tab before capturing.
- A "Reconnecting…" reload of the product tab wipes every helper you injected. Keep them in a local file and paste them back in one call.
- After capturing, check every plate against its neighbour with the known viewports (predict, compare, flag spikes) before building on them; contact-sheet tiling can fake a glitch, so confirm on the full frame.

## Headless capture of a public product demo (kids' learning app, Sep 2026)
When the product has a public demo (no login), skip the user's Chrome and drive it with Playwright headless, which is faster, repeatable and sharper:
- **Phone plates at 3x:** `viewport 430x900, deviceScaleFactor 3, isMobile, hasTouch` gives 1290x2700 screenshots of the real UI. A phone in a 1080p frame shows them at about 0.33x, so push-ins up to about 2.5x stay native.
- **Read the product's own data first.** The demo's lesson JSON listed every step, question and answer. A scripted playthrough solved each question from the on-screen caption ("5 groups of 4 = ?"), not a hardcoded answer list, because the product adapts its question order.
- **Miss on purpose** to capture the product's help moment (the coach's "Off the rim!" plus a number-line hint), then answer correctly. Take burst screenshots (12-24 frames at 100-150 ms) around each state change; they play back as real motion.
- **Harvest the product's own media from its network and source:** recorded voice lines (that product stored each sentence at `audio/<FNV-1a hash of the text>.mp3`, so any line could be fetched by computing its hash), SFX (crowd, swish, buzzer), and short character videos with their own audio. That gave real motion and a real voice with zero credits.
- **Forms:** reveal a hidden form step via the DOM and fill it for the story's persona, but never enter an email or submit (abort `/api/` routes to be safe).
- **Honesty line:** every product frame, voice and sound came from the product. Code added the camera, phone frame, taps, type and confetti.

## Gotchas from the same run
- Suno's CDN `.m4a` is encrypted and the API returns `audio_url: forbidden`. Download goes through the UI and **costs one of the plan's monthly download unlocks**. Ask before spending one, like credits.
- Don't `pkill -f export.mjs` in the same command line that starts a new export: the pattern matches your own shell.
- `frames.mjs` doesn't clear `review/`, so the sheet mixes old and new frames. `rm -rf review/square` before a fresh sheet.
