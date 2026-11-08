#!/usr/bin/env python3
"""align.py — snap faster-whisper's heard words (songmap/heard.json) to the KNOWN streaming lyrics (songmap/lyrics.txt).

The text is always ours; only the times come from the audio. Heard and lyric words are matched by sequence alignment
(difflib on lowercased letters-only tokens). A lyric word the model missed or misheard gets a time interpolated
between its matched neighbours. The song repeats its last line ("Ich bin hier. Das war.") once more after an
instrumental stretch; that repeat is appended to the lyric as an extra line so every sung word has a place.
Writes songmap/words.json and songmap/beatmap.json (60 bpm heartbeat, phase measured with librosa)."""
import json, re, difflib

norm = lambda w: re.sub(r"[^\wäöüß]", "", w.lower())
LYR = [l.strip() for l in open("songmap/lyrics.txt", encoding="utf-8").read().splitlines() if l.strip()]
SECT = ["Intro", "Verse 1", "Verse 1", "Verse 1", "Verse 1", "Refrain", "Refrain", "Refrain", "Refrain",
        "Verse 2", "Verse 2", "Verse 2", "Verse 2", "Refrain 2", "Refrain 2", "Refrain 2", "Refrain 2", "Bridge", "Outro", "Outro"]
KEY = ["meiner", "Licht", "Druck", "aus", "hier", "hier", "war", "war", "hier", "verlangt", "da", "mir", "hier",
       "hier", "war", "war", "hier", "auch", "hier", "war"]
# the Intro line is one sentence pair on one row of lyrics.txt; the outro "Ich bin hier." / "Das war." are two rows
rows = []
for l in LYR:
    rows.append(l)
# split "Ich bin hier. Das war." (last row) stays one line; add the repeat
assert len(rows) == 20, len(rows)
rows += rows[-2:]; SECT += ["Outro", "Outro"]; KEY += ["hier", "war"]   # the repeat after the instrumental stretch

toks = []                                   # (word, line)
for i, l in enumerate(rows):
    for w in l.split():
        toks.append((w, i))
heard = json.load(open("songmap/heard.json"))["words"]
heard = [h for h in heard if h["t"] < 135.5]                 # drop the model's hallucinated end credit
A = [norm(w) for w, _ in toks]; B = [norm(h["w"]) for h in heard]
sm = difflib.SequenceMatcher(None, A, B, autojunk=False)
tm = [None] * len(toks)
for a, b, n in sm.get_matching_blocks():
    for k in range(n):
        tm[a + k] = heard[b + k]
# interpolate the rest between matched neighbours
idx = [i for i, x in enumerate(tm) if x]
print(f"{len(idx)} of {len(toks)} lyric words matched to heard words")
out = []
for i, (w, ln) in enumerate(toks):
    if tm[i]:
        t, e = tm[i]["t"], tm[i]["end"]
    else:
        lo = max([j for j in idx if j < i], default=None); hi = min([j for j in idx if j > i], default=None)
        if lo is None: lo_t, lo_i = max(0.0, tm[hi]["t"] - 0.5 * (hi - i)), i - 1
        else: lo_t, lo_i = tm[lo]["end"], lo
        if hi is None: hi_t, hi_i = lo_t + 0.5 * (i - lo_i + 1), i + 1
        else: hi_t, hi_i = tm[hi]["t"], hi
        step = (hi_t - lo_t) / (hi_i - lo_i)
        t = lo_t + step * (i - lo_i - 0.5) if lo is not None else lo_t + step * (i - lo_i - 1)
        t = max(t, 0.0); e = t + min(0.5, step * 0.8)
    out.append({"w": w, "t": round(t, 3), "end": round(max(e, t + 0.15), 3), "line": ln, "stress": round(t + 0.3 * (max(e, t + 0.15) - t), 3), "heard": bool(tm[i])})
# monotonic
for a, b in zip(out, out[1:]):
    if b["t"] < a["t"]: b["t"] = a["t"] + 0.05; b["end"] = max(b["end"], b["t"] + 0.15); b["stress"] = round(b["t"] + 0.3 * (b["end"] - b["t"]), 3)
lines = []
for i, l in enumerate(rows):
    ws = [x for x in out if x["line"] == i]
    kw = [x for x in ws if norm(x["w"]) == norm(KEY[i])][-1]
    lines.append({"i": i, "text": l, "section": SECT[i], "t": ws[0]["t"], "end": ws[-1]["end"], "key": {"w": kw["w"], "t": kw["t"], "stress": kw["stress"]}})
secs = []; cur = None
for l in lines:
    if cur and cur["name"] == l["section"]: cur["end"] = l["end"]
    else:
        if cur: secs.append(cur)
        cur = {"name": l["section"], "t": l["t"], "end": l["end"]}
secs.append(cur)
# instrumental stretches in between become sections of their own; the song starts at 0 and ends at the file's end
full = []; t = 0.0
for s in secs:
    if s["t"] - t > 4.0: full.append({"name": "Instrumental", "t": round(t, 2), "end": round(s["t"] - 0.4, 2)})
    full.append({"name": s["name"], "t": round(s["t"] - 0.4, 2), "end": round(s["end"] + 0.6, 2)}); t = s["end"] + 0.6
full.append({"name": "Stille", "t": round(t, 2), "end": 138.08})
json.dump({"source": "audio/13-ich-bin-hier-das-war.mp3 (faster-whisper small, snapped to the streaming lyrics)", "language": "de",
           "words": out, "lines": lines, "sections": full}, open("songmap/words.json", "w"), ensure_ascii=False, indent=1)
PH, DUR = 0.45, 138.08                      # heartbeat phase measured with librosa (60 bpm, stable from 40 s on)
beats = [round(PH + k, 3) for k in range(int(DUR - PH) + 1)]
json.dump({"source": "measured: 60 bpm heartbeat, phase 0.45 s (librosa onset fit); bar 1 assumed on the first beat", "bpm": 60, "duration": DUR,
           "beats": beats, "downbeats": beats[::4], "hits": [], "stops": [], "drop": None,
           "sections": [{"name": s["name"], "kind": "lyric", "t": s["t"], "end": s["end"]} for s in full]}, open("songmap/beatmap.json", "w"), indent=1)
for l in lines: print(l["i"], l["section"], round(l["t"], 1), round(l["end"], 1), l["key"]["w"], l["key"]["stress"], "|", l["text"][:40])
print([(s["name"], s["t"], s["end"]) for s in full])
