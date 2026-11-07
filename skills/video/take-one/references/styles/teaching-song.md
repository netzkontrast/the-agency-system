# Style: 3D teaching song

A song that teaches a technical idea, with each lyric line visualized in a 3D world of the subject itself. Reference: "Chasing the Roofline" (Sep 2026, 3:10, 60 fps), a song about CUDA from the book "CUDA for Deep Learning", set inside a GPU chip.

## The use case

Turn a book, a course, a paper or a product into a catchy song (Suno) plus a clip that explains it. The song carries memory; the visuals carry understanding. Great for authors, educators, dev tools, and "explain my product" pieces that people actually rewatch.

1. Write the lyrics with the user from the source material: one concept per line, concrete numbers in the lyrics ("Thirty-two threads in a warp, in line"), a chorus that states the core idea ("Memory's the slope and the math's the line"). Give the user a Suno prompt with the lyrics.
2. Map the song (see music-video.md) at word level.
3. Storyboard: each line = one visual demonstration of exactly that concept.

## Design system

- **One 3D world = the subject itself** (for a GPU: the chip die, SMs as blocks, memory lanes, tensor cores as cubes). Dark graphite materials, soft studio light, shallow depth of field, slow camera moves across it.
- **One accent: glowing orange** for the thing being explained (active threads, the data path, the current value). Everything else is neutral grey. A second accent (acid green) only for a contrast concept (the divergent branch).
- **A recurring chart as the story spine:** the roofline plot returns throughout, with "your kernel" as a glowing ball climbing toward the ceiling (0.01 → 0.26 → 0.70 → 0.78 of peak). Progress the viewer can feel.
- **Karaoke lyrics as the caption:** a clean bold sans, top-left, white; **the word being sung lights up orange**, the rest dim. Plus small mono callout labels pinned to 3D objects ("32 threads · 1 warp").
- Big numbers and units appear as 3D digits or counters (1,700 GPU, 8192 × 8192 × 4 B = 268 MB).
- Title and end cards: the song name in heavy type on the chip; the book title in a serif at the end.

## Engine

Three.js (from a CDN, e.g. `https://cdn.jsdelivr.net/npm/three@0.170/build/three.module.js`) for the 3D world; a 2D canvas overlay for karaoke and labels. Every frame a pure function of t: camera, animation and highlights driven by the lyric timeline. Serve over http (the scripts do). Keep geometry instanced (thousands of cells as InstancedMesh) for speed.
