#!/usr/bin/env python3
"""estimate.py — a PROVISIONAL song map for track 13 (no audio file available yet).

Known from Suno's clip metadata: duration 138.08 s, 60 BPM. Everything else is planned: the lyric lines are placed on
a bar grid (1 bar = 4 s) and the words inside a line are spread by length. Replace it with the measured map as soon as
the audio exists:  bin/studio songmap audio/<file>.mp3 --lyrics songmap/lyrics.txt --dir .   (then every scene retimes).
Writes songmap/words.json and songmap/beatmap.json; then run tools/audio/songmap_js.py.
"""
import json, re

DUR = 138.08
# (section, line text, key word, start s, slot s) — streaming lyrics, never the Suno box
LINES = [
    ("Intro",    "Der Puls ist langsam. Der Puls ist meiner.",              "meiner",   2.0,  8.0),
    ("Verse 1",  "Das Gelb hängt in den Vorhängen. Es ist nur Licht.",      "Licht",   12.0,  8.0),
    ("Verse 1",  "Kein Faden auf dem Mund. Kein Druck, der mich erstickt.", "Druck",   20.0,  8.0),
    ("Verse 1",  "Ich atme ein. Ich atme aus. Niemand verhandelt mit.",     "aus",     28.0,  8.0),
    ("Verse 1",  "Der Raum ist still. Und ich bin hier.",                   "hier",    36.0,  8.0),
    ("Refrain",  "Ich bin hier.",                                           "hier",    44.0,  4.0),
    ("Refrain",  "Das war.",                                                "war",     48.0,  4.0),
    ("Refrain",  "Kein Sieg. Kein Ende. Nur das hier und das, was war.",    "war",     52.0,  8.0),
    ("Refrain",  "Ich bin hier.",                                           "hier",    60.0,  4.0),
    ("Verse 2",  "Ich hab nach Luft gefragt. Ich hab es laut verlangt.",    "verlangt",68.0,  8.0),
    ("Verse 2",  "Jetzt frag ich nicht mehr. Die Luft ist einfach da.",     "da",      76.0,  8.0),
    ("Verse 2",  "Das, was war, bleibt wahr. Und es bleibt hinter mir.",    "mir",     84.0,  8.0),
    ("Verse 2",  "Ich dreh mich nicht mehr um. Ich bin hier.",              "hier",    92.0,  8.0),
    ("Refrain 2","Ich bin hier.",                                           "hier",   100.0,  4.0),
    ("Refrain 2","Das war.",                                                "war",    104.0,  4.0),
    ("Refrain 2","Kein Sieg. Kein Ende. Nur das hier und das, was war.",    "war",    108.0,  8.0),
    ("Refrain 2","Ich bin hier.",                                           "hier",   116.0,  4.0),
    ("Bridge",   "Ich bin auch hier.",                                      "auch",   122.0,  4.0),
    ("Outro",    "Ich bin hier. Das war.",                                  "war",    128.0,  4.0),
]
SECTIONS = [("Intro", 0.0, 12.0), ("Verse 1", 12.0, 44.0), ("Refrain", 44.0, 68.0), ("Verse 2", 68.0, 100.0),
            ("Refrain 2", 100.0, 120.0), ("Bridge", 120.0, 128.0), ("Outro", 128.0, 134.0), ("Stille", 134.0, DUR)]

words, lines = [], []
for i, (sec, text, key, t0, slot) in enumerate(LINES):
    toks = text.split()                            # keep the punctuation: the subtitles use these tokens
    win = slot * 0.7                               # speech fills 70 % of the slot; the rest is breath
    wts = [len(re.sub(r'\W', '', w)) + 1.5 for w in toks]
    tot, t = sum(wts), t0 + 0.4
    first = len(words)
    for w, wt in zip(toks, wts):
        d = win * wt / tot
        words.append({"w": w, "t": round(t, 3), "end": round(t + d * 0.86, 3), "line": i, "stress": round(t + d * 0.35, 3)})
        t += d
    kw = [x for x in words[first:] if re.sub(r'\W', '', x["w"]).lower() == key.lower()][-1]
    lines.append({"i": i, "text": text, "section": sec, "t": words[first]["t"], "end": words[-1]["end"],
                  "key": {"w": kw["w"], "t": kw["t"], "stress": kw["stress"]}})
json.dump({"source": "ESTIMATED (no audio yet)", "language": "de", "estimated": True, "words": words, "lines": lines,
           "sections": [{"name": n, "t": a, "end": b} for n, a, b in SECTIONS]},
          open("songmap/words.json", "w"), ensure_ascii=False, indent=1)
beats = [round(k * 1.0, 3) for k in range(int(DUR) + 1)]
downs = [round(k * 4.0, 3) for k in range(int(DUR // 4) + 1)]
json.dump({"source": "ESTIMATED: 60 bpm grid, offset 0", "bpm": 60, "duration": DUR, "beats": beats, "downbeats": downs,
           "hits": [], "stops": [], "drop": None, "sections": [{"name": n, "kind": "lyric", "t": a, "end": b} for n, a, b in SECTIONS]},
          open("songmap/beatmap.json", "w"), indent=1)
print(f"{len(words)} words, {len(lines)} lines, {len(beats)} beats, {len(downs)} bars")
