# Page or picture: the check that names "slideshow"

Run it on the storyboard, at the pitch, shot by shot. Run it again on the stills.

**Why it exists.** A 40 second product ad passed every technical gate and three fresh reviewers gave it the same verdict in different words: "a tidy animated slide deck", "a polished slideshow", "a screen recording in the middle". They could feel it and could not say what to change. The cause was in the storyboard from the first day: most shots were pages (a caption band on top, a card under it, things fading in and sitting there). Nothing in the process asked the question below before the build.

Slop is rarely a bad choice. It is the choice nobody made. Each default here is fine when it was chosen for this film and you can say why in one sentence. It fails when you arrived there because it is what a film like this usually looks like.

## The two questions, for every shot

**1. Is this shot a page or a picture?**
A page: a frame laid out like a slide or a web page (a title strip, a body, maybe a footer), where the layout stays put and the content is swapped into it. A picture: one thing fills the frame and the eye knows where to go.
- Cover the words on the still. If what is left is a plain ground with a card or a block on it, it is a page.
- If three shots in a row share one layout, they are one page with three slides.
- A page is allowed when the product is a page and this is the one shot that shows it. Then it gets a camera: crop in until one object fills the frame.

**2. Does something happen, or is something shown?**
Read the shot's line in the storyboard. "A list with eight tasks" is a state. "She gives the task to the agent and it starts" is an event. A film of states is a slideshow however well each one moves in.
- Write every shot as an event: who or what does something, and what that causes.
- A shot that has no event either gets one or loses its time to a neighbour.

## The defaults to catch in a product film
Ask of each: did I choose this for this film?
- **A caption band.** The same strip of headline over every shot. The words then narrate the picture from outside it. Prefer words that live in the picture: on the wall, behind a person, on the object.
- **The name parked in a corner** for the whole film. A viewer does not need a watermark; they need the name once at the start and once at the end.
- **A generic card.** A rounded white card with a dot, a label and a value could be any product. Show the real product's own piece, big.
- **The first idea the name gives you**, or a mark that turns into something (a dot that becomes a person, a tick that becomes a road), used because it is neat and not because the film needs it.
- **Everything, at equal weight.** Each feature of the brief gets a beat and none is the point. Say which features you left out on purpose.
- **A dark, glowing "premium" ground** because dark feels expensive, when the brand is light.
- **Proof made up to look real**: numbers, logos of customers, quotes.
- **An ending that is a web footer.** A film ends on its last beat. The mark, one line and one action are that beat; they still need to arrive as part of the story and not as furniture. How long the action holds is the person's call: an ad that must be acted on holds it longer than a mood film.
- **Stillness as safety.** A lone element on an empty ground and a long hold look restrained and risk nothing.
- **Sound as wallpaper.** One loop at one level from start to end, with no quiet and no hit tied to something seen.

## What to do with the answers
- At the pitch: mark each shot P (picture) or G (page) and E (event) or S (state) in the storyboard table. More than a third pages, or more than a third states, means the storyboard changes before anything is built. Say the count in the pitch.
- At the stills gate: do the cover-the-words test on the sheet. Then run `scripts/text-audit.mjs` (it measures what the words on screen actually do; see `pipeline.md`).
- In the delivery note: one line on any default you kept on purpose, and why.

This check is about how the film is staged. Whether the idea is worth a film is `concept-check.md`; what a still must pass is `before-the-first-cut.md`.
