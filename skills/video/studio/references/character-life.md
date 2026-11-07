# Character life (code-drawn characters)

Read this when a drawn character moves on screen. It is what made the same figure, with the same poses and timing, read as more alive in three blind tests (wide shot, close-up, medium shot). The helpers are in `engine/lib/life.js` (copied to `engine/life.js` in every project by `new-project.sh`).

1. **Blink on the head turns, never on a timer.** Close fast, open slower (`blinkLid`: 110 ms, 40 ms, 190 ms). One blink as each head turn starts, and one in a long hold. In the close-up test this was the difference the viewer named.
2. **The eyes get there first.** Read the head's keys about 0.1 s ahead for the gaze (`eyesLead`).
3. **Limbs settle, they do not wobble.** Chain a character's poses with `flow` (it keeps moving through a pose and never overshoots), and let child parts trail their parent with `settle` (forearm after upper arm, back hair after the head). Springs stay right for objects and interface; on a body they bounce like rubber. In the wide-shot test, the arm coming down was what the viewer called more real.
4. **Hands stay on what they hold.** Draw a held object from the hand's position every frame, never on its own path.

Breathing and slow sway were in the tests too, and nobody noticed them; add them only if a long hold looks frozen. Left and right never move as mirror images.

## The character department (any film with a character who moves)

Before any scene is animated, build the character properly and get approval on motion, not stills: a real skeleton
(fixed bone lengths, joint limits, 2-bone IK for arms and legs, foot planting), drawn head views and hand shapes
(never procedurally bent faces or fingers), a pose library of the poses the film needs, and short motion tests (walk
cycle, sit/stand, reach and grip, the film's key actions; `styles/pencil-test.md` is their on-screen form). Animators
then use only approved poses and motions. Lesson from a song clip: stills approved, film failed, because animators
improvised limbs on a loose figure and joints twisted in motion. Keep code characters stylized. In the paint medium the
drawn key views, emotions and moves of `paint-medium.md` are this department's kit; whatever performs (a character, an
object, a light) gets its own model sheet the same way.
