# Paint demo: "The fallen star" (11 s)

An 11-second film in the paint medium (p5.js + p5.brush) that exercises the kit: an acted emotion timeline, a drawn
turn through the key views, a trot, a pickup, a throw on an arc, `glow`, a brush wipe and an iris in and out. It stars
the optional sample character Clawd (`engine/paint/clawd.js`). It is one idea, not a template: don't reuse its story,
night sky, hills, star or shot structure (`references/paint-medium.md`, "About the demo", walks through how its ending
is timed).

## Run it

```bash
# 1. a paint project with the sample character loaded, 11 s long
bash <studio>/tools/new-project.sh ~/paint-demo --medium paint --character --duration 11

# 2. the demo becomes the project's only chapter
cp <studio>/examples/paint-demo/demo.js ~/paint-demo/scenes/ch01.js

# 3. look at it: a contact sheet of the whole film, then every frame of the throw
cd ~/paint-demo
node <studio>/tools/render.mjs --sheet=0.5,2,3.5,5,6.5,7.5,8.5,10 --cols=4 --w=480 --out=review/sheet.jpg
node <studio>/tools/render.mjs --strip=6.9:7.9 --cols=6 --w=320 --out=review/throw.jpg

# 4. the film itself (drawn on twos), then the gate on the export
node <studio>/tools/render.mjs --clip --twos --out=out/fallen-star.mp4
node <studio>/tools/gate.mjs film.html --mp4 out/fallen-star.mp4
```

Open the review images with the Read tool (or any image viewer). To scrub it in a browser, serve the folder over
http (for example `python3 -m http.server 8000` in the project folder, then `http://127.0.0.1:8000/film.html`); `?t=2.5` jumps to a time,
`?loop=emotions` shows a model-sheet loop.

Needs: the studio's Node packages and a Chrome/Chromium (`bash <studio>/bin/studio doctor`; without a GPU set
`STUDIO_GL=soft` and expect 20–30 s a frame at 1080p, so render small sheets there).
