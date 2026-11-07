# Video models: read them live, and what we have seen

`real-shots.md` holds the method for moving shots (where they pay, the prompt, what goes wrong). This page holds the facts about particular models. Those facts go stale in weeks: lengths, inputs, prices and names change. So there are two rules, and then the notes.

## Rule 1. Read the model before the first render
The same way the price is read before every spend, read the model's own limits before the first clip:
- which models the person's service offers today, and which of them accept a start picture;
- the shortest and longest clip, and the sizes it renders at natively;
- what the call needs for a start picture (some models want a named mode or role, and fail validation without it; a failed validation is not charged);
- how many jobs run at once.

Through a connector, ask the catalog (on Higgsfield: the model list and a model's own entry) and price the exact call with the cost flag. In a browser, read the model's panel. Then say in one line what you read. Where this page and the live read disagree, the live read wins, and this page gets a new dated line.

## Rule 2. One clip first when the model is new to you
The first time a model is used on a film, render one clip on the hardest shot (faces, small lettering, hands) and look at it at the size it plays before sending the rest. It is still one render per shot: the test clip is the shot if it holds.

## Notes, dated. Check the date before trusting a line.

### Seedance 2.5 (through Higgsfield), 6 and 7 October 2026
- Clip length 4 to 30 s. A start picture needed the mode `omni_reference`; without it the call failed validation with "mode 't2v' does not accept reference media". The start picture can be a picture already generated on the same service, passed by its id with the role `start_image`.
- Prices read then: about 7 credits a second at 720p and 12 at 1080p. A 480p draft was 3 a second, and finishing it cost the full 1080p price, so draft then finish costs more than rendering directly.
- A first call sometimes came back as a preset suggestion and not a job; declining the preset and sending again gave the literal render.
- A 4 s 1080p clip took about 3 minutes; 720p took 6 to 8. Four jobs ran at once; a fifth was refused and not charged.
- It started on the exact framing of the still. Most of the motion happened in the first two seconds, and the camera drifted more than asked later on, so shots were taken from frame 0.
- 720p read as soft on an opening, and an upscale did not fully fix it for the owner.

### Kling 3.0 Pro (through Higgsfield), 7 and 8 October 2026
- Native 1080p. Shortest clip 3 s. Price read on 7 October: 1.5 credits a second; on 8 October a 5 s clip from a start picture priced at 8.75.
- From an approved still it held faces, clothes and a product, with the same prompt wording as above, and took 3 to 6 minutes. Seven jobs were accepted at once.
- On a film of people shots it replaced the dearer model on every shot: sharper at about a sixth of the price a clip. For people from an approved still, price it first.

### Upscalers, 7 October 2026
- A model upscale kept the exact motion and took 12 to 17 minutes a clip. Fine at the size it plays; zoomed two times or more it paints skin. A close-up is its own clip.

## Prompt wording that held, on both models
1. "The camera is held by hand and stays on this exact framing, a faint sway, no push, no pan." (when the film's own camera does the move in code)
2. One small action for each person or object, "in real time, already in motion from the first frame".
3. "Everyone stays exactly as they are: same faces, same clothes, same room." For a product: "it stays perfectly still and unchanged", and any lettering "stays exactly as it is".
4. The bans: "no new objects, no hands entering, no text, no morphing, no flicker".
Two people doing the same gesture in one still read as one copying the other once it moves. Fix the still first; that is free.

## Add to this page
After any film that used a video model, add a dated line: the model, what you read live, what held, what did not, the price. Facts only, no client names.

**Kling 3.0 on the Higgsfield website, 11 Oct 2026 (read on the Generate button, start picture given):** 4K 5 s = 30 credits; 1080p 5 s = 10; 1080p 3 s = 6 with the clip's own sound on, **4.5 with sound off**. The sound switch and the prompt-rewrite switch are two small chips under the prompt; both were on by default. When the film has its own sound, turn the clip's sound off before reading the price, and turn prompt rewriting off so the model gets the prompt as written. A product-only shot (still object, slow camera arc, one light event, the bans) held the product and its embossed lettering on the first render.
