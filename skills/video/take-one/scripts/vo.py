#!/usr/bin/env python3
# scripts/vo.py : lay a recorded narration on the film, and prove that every cut line says what the script says.
# Usage (from the film folder): python3 <skill>/scripts/vo.py vo.json      (VO_FORCE=1 writes the track even when a line is cut wrong)
#   vo.json: {"seconds": 45, "takes": [{"file": "audio/vo/narrator.mp3", "lines": [{"id": "hook", "text": "The line as spoken.", "at": 0.4}, ...]}]}
#     one entry in "takes" per recorded file (a second voice is a second take). "lines" lists every line in the take, in the order spoken.
#     line fields: id; text; at = when it starts in the film, in seconds (leave out a line that is in the take but not used);
#                  chain + gap = start no earlier than the end of the line before plus gap; marks = {"name": word index} for a sentence that starts inside the line.
#     optional: "wav" (default audio/vo.wav), "js" (default assets/vo.js)
#   How a take is cut:
#   1. it is split into islands of speech by its own silences;
#   2. whisper gives rough word times, used only to say which silence sits between two lines (the longest one there);
#   3. each line is cut silence to silence, so a cut can never land inside a word;
#   4. every cut line is transcribed ON ITS OWN and compared with its text. A line with extra or lost words stops the build.
#   out: the voice track (film length, 48 kHz mono) and a small file of when each line starts, so the words on screen can follow the voice.
#   needs: ffmpeg, numpy, whisper-cli with a model (VO_MODEL=<path>, default ./ggml-large-v3-turbo.bin). VO_LANG sets the language (default en).
import sys, subprocess, json, re, os, hashlib, difflib, struct, numpy as np
if len(sys.argv) < 2: sys.exit('usage (from the film folder): python3 vo.py vo.json   (the format is at the top of this file)')
CFG = json.load(open(sys.argv[1])); SR = 48000; DUR = float(CFG['seconds'])
MODEL = os.path.expanduser(os.environ.get('VO_MODEL', './ggml-large-v3-turbo.bin')); LANG = os.environ.get('VO_LANG', 'en')
if not os.path.exists(MODEL): sys.exit(f'no whisper model at {MODEL}: set VO_MODEL to a ggml model file')
NUM = {'40': 'forty', '4': 'four', '1': 'one'}
def norm(w):
    w = re.sub(r"[^a-z0-9']", '', w.lower().replace('’', "'")); return NUM.get(w, w)
def words_of(s): return [w for w in (norm(x) for x in s.split()) if w]
def whisper_words(take):
    base = os.path.splitext(take)[0]; wav16 = base + '-16k.wav'; out = base + '-words.json'
    if not os.path.exists(out) or os.path.getmtime(out) < os.path.getmtime(take):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', take, '-ar', '16000', '-ac', '1', wav16], check=True)
        subprocess.run(['whisper-cli', '-m', MODEL, '-f', wav16, '-l', LANG, '-ml', '1', '-sow', '-oj', '-of', base + '-words', '-np'], capture_output=True, check=True)
    ws = [(norm(s['text']), s['offsets']['from'] / 1000, s['offsets']['to'] / 1000) for s in json.load(open(out))['transcription']]
    return [w for w in ws if w[0] and not w[0].startswith('[')]
def islands(y):
    hop = int(0.005 * SR); n = len(y) // hop; edb = 20 * np.log10(np.sqrt(np.mean(y[:n * hop].reshape(n, hop) ** 2, axis=1)) + 1e-9)
    ref = float(np.percentile(edb[edb > -60], 95)); loud = edb > ref - 34; runs = []; s = None
    for i in range(n + 1):
        v = i < n and loud[i]
        if v and s is None: s = i
        if not v and s is not None: runs.append([s, i]); s = None
    merged = []
    for r in runs:                                          # a stop consonant is not a pause: close gaps under 70 ms
        if merged and r[0] - merged[-1][1] < 14: merged[-1][1] = r[1]
        else: merged.append(r)
    return [(a * hop / SR, b * hop / SR) for a, b in merged if b - a >= 6], ref
def hear(clips):                                            # transcribe each clip on its own; cached by its samples
    d = 'audio/vo/.check'; os.makedirs(d, exist_ok=True); cf = d + '/cache.json'; cache = json.load(open(cf)) if os.path.exists(cf) else {}; need = []
    keys = []
    for c in clips:
        m = len(c) // 3 * 3; x = np.concatenate([np.zeros(6400), c[:m].reshape(-1, 3).mean(axis=1), np.zeros(6400)]); pcm = (np.clip(x * 3, -1, 1) * 32767).astype('<i2').tobytes()
        k = hashlib.sha1(pcm).hexdigest()[:16]; keys.append(k)
        if k not in cache:
            p = f'{d}/{k}.wav'; open(p, 'wb').write(b'RIFF' + struct.pack('<I', 36 + len(pcm)) + b'WAVEfmt ' + struct.pack('<IHHIIHH', 16, 1, 1, 16000, 32000, 2, 16) + b'data' + struct.pack('<I', len(pcm)) + pcm); need.append((k, p))
    if need:
        subprocess.run(['whisper-cli', '-m', MODEL, '-l', LANG, '-np', '-nt', '-otxt', *[p for _, p in need]], capture_output=True, check=True)
        for k, p in need:
            cache[k] = open(p + '.txt').read().strip() if os.path.exists(p + '.txt') else ''
            for f in (p, p + '.txt'):
                if os.path.exists(f): os.remove(f)
        json.dump(cache, open(cf, 'w'), indent=0)
    return [cache[k] for k in keys]
def lay(take, LINES, track, VO):
    words = whisper_words(take); n = len(LINES)
    want = [(w, li) for li, ln in enumerate(LINES) for w in words_of(ln['text'])]
    j = 0; hit = {}
    for i, (w, li) in enumerate(want):
        for k in range(j, min(j + 4, len(words))):
            a = words[k][0]
            if a == w or a.startswith(w) or w.startswith(a) or (len(w) > 3 and a[:4] == w[:4]): hit[i] = k; j = k + 1; break
    miss = [want[i][0] for i in range(len(want)) if i not in hit]
    if len(miss) > max(2, len(want) * 0.15): sys.exit(f'{take} does not match its lines: {len(miss)} of {len(want)} words not found: {miss[:12]}')
    y = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', take, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout, dtype=np.float32).astype(np.float64)
    isl, ref = islands(y); gaps = [(isl[i][1], isl[i + 1][0]) for i in range(len(isl) - 1)]; mid = lambda g: (g[0] + g[1]) / 2
    spans = []
    for li, ln in enumerate(LINES):
        idx = [hit[i] for i, (w, l) in enumerate(want) if l == li and i in hit]
        if not idx: sys.exit(f"line not found in {take}: {ln['text']}")
        spans.append(idx)
    warn = []; B = []                                       # between two lines: the longest silence around the last word of one and the first word of the next
    for a, b in zip(spans, spans[1:]):
        ta, tb = words[a[-1]][1], words[b[0]][2]; am, bm = (ta + words[a[-1]][2]) / 2, (words[b[0]][1] + tb) / 2; floor = (B[-1][1] if B else 0) + 0.08
        cand = [g for g in gaps if g[0] >= ta - 0.05 and g[1] <= tb + 0.05 and g[0] > floor] or [g for g in gaps if g[1] > am - 0.2 and g[0] < bm + 0.4 and g[0] > floor]
        gs = max(floor, (words[a[-1]][2] + words[b[0]][1]) / 2); B.append(max(cand, key=lambda g: g[1] - g[0]) if cand else (gs, gs))
    first = next(i for i in isl if i[1] > words[spans[0][0]][1])
    def span(i, B): return (first[0] if i == 0 else B[i - 1][1]), (isl[-1][1] if i == n - 1 else B[i][0])
    def cut(i, B):
        on, off = span(i, B); nxt = B[i][1] if i < n - 1 else off + 1; c = y[max(0, int((on - 0.03) * SR)):int(max(on + 0.1, min(off + 0.12, max(off, nxt - 0.01))) * SR)].copy()
        f1, f2 = int(0.006 * SR), int(0.06 * SR); c[:f1] *= np.linspace(0, 1, f1); c[-f2:] *= np.linspace(1, 0, f2); return c
    def sim(i, h):
        W, Hh = words_of(LINES[i]['text']), words_of(h); return 1.0 if W == Hh else 0.98 * difflib.SequenceMatcher(None, W, Hh).ratio()
    def wrong(i, h):                                        # extra or lost words. One word spelled another way is not a wrong cut, but the first and last sounds must be there.
        W, Hh = words_of(LINES[i]['text']), words_of(h); a, b = ''.join(W), ''.join(Hh); r = lambda x, z: difflib.SequenceMatcher(None, x, z).ratio()
        if a == b or (len(W) == 1 and len(Hh) <= 1): return False
        return not (r(a, b) >= 0.85 and r(a[:5], b[:5]) >= 0.6 and r(a[-5:], b[-5:]) >= 0.6)
    heard = hear([cut(i, B) for i in range(n)]); moved = 0
    for _ in range(3):                                      # a wrong cut is repaired by trying the silences next to it and keeping the one both lines are heard right with
        fixed = False
        for b in range(n - 1):
            guess = B[b][1] - B[b][0] < 0.03
            if not (guess or wrong(b, heard[b]) or wrong(b + 1, heard[b + 1])): continue
            lo, hi = span(b, B)[0], span(b + 1, B)[1]; cands = [g for g in gaps if g[0] > lo + 0.1 and g[1] < hi - 0.1 and abs(mid(g) - mid(B[b])) < 2.0 and g != B[b]]
            if not cands: continue
            best, pick, ph = sim(b, heard[b]) + sim(b + 1, heard[b + 1]) - (1e-3 if guess else -1e-6), None, None      # a real silence beats a guess when both are heard the same
            hs = hear([c for g in cands for c in (cut(b, B[:b] + [g] + B[b + 1:]), cut(b + 1, B[:b] + [g] + B[b + 1:]))])
            for k, g in sorted(enumerate(cands), key=lambda kg: kg[1][0] - kg[1][1]):                                  # longest silence first
                sc = sim(b, hs[2 * k]) + sim(b + 1, hs[2 * k + 1])
                if sc > best: best, pick, ph = sc, g, (hs[2 * k], hs[2 * k + 1])
            if pick: B[b] = pick; heard[b], heard[b + 1] = ph; fixed = True; moved += 1
        if not fixed: break
    for b in range(n - 1):
        if B[b][1] - B[b][0] < 0.03: warn.append(f"  NO PAUSE between '{LINES[b]['text']}' and the next line: cut at the quietest point, check by ear")
    clips = []; bad = 0; soft = []
    for i, ln in enumerate(LINES):
        on, off = span(i, B); c = cut(i, B); act = np.abs(c) > 10 ** ((ref - 30) / 20); clips.append((ln, on, off, c, spans[i], 20 * np.log10(np.sqrt(np.mean(c[act] ** 2)))))
        if wrong(i, heard[i]): bad += 1; warn.append(f"  WRONG CUT: '{ln['text']}' was heard alone as '{heard[i]}'")
        elif words_of(ln['text']) != words_of(heard[i]): soft.append(f"  one word heard differently (check by ear): '{ln['text']}' -> '{heard[i]}'")
    med = float(np.median([c[5] for c in clips])); prev_end = 0; rows = []
    for ln, on, off, c, sp, r in clips:
        if ln['at'] is None: continue
        g = float(np.clip(med - r, -4, 5)); t0 = ln['at']
        if ln.get('chain'): t0 = max(t0, prev_end + ln.get('gap', 0.25))
        if t0 < prev_end + 0.05: warn.append(f"  TIGHT: '{ln['text']}' starts {t0:.2f} but the line before ends {prev_end:.2f}")
        s = int((t0 - 0.03) * SR); c = c[:max(0, len(track) - s)]; track[s:s + len(c)] += c * 10 ** (g / 20); prev_end = t0 + (off - on)
        if prev_end > DUR - 0.15: warn.append(f"  LATE: '{ln['text']}' ends {prev_end:.2f}, the film ends {DUR:.2f}")
        VO[ln['id']] = round(t0, 3)
        for name, wi in (ln.get('marks') or {}).items():      # a sentence that starts inside the line: the longest silence near where its first word should fall (by share of letters); whisper's word times are too loose for this
            cw = [len(w) for w in words_of(ln['text'])]; exp = on + sum(cw[:wi]) / sum(cw) * (off - on); inner = [g for g in gaps if g[0] > on and g[1] < off and abs(g[1] - exp) < 0.7]
            VO[name] = round(t0 + (max(inner, key=lambda g: g[1] - g[0])[1] if inner else exp) - on, 3)
        rows.append(f"{t0:6.2f} {off - on:5.2f} {g:+5.1f}  {ln['text']}")
    print(os.path.basename(take)); print('\n'.join(rows))
    print(f"  CHECKED: {len(clips) - bad} of {len(clips)} lines, each heard alone, match their text" + (f' ({moved} cut(s) moved to the right silence)' if moved else '') + ('' if not soft else '\n' + '\n'.join(soft)))
    print('\n'.join(warn) if warn else '  no line runs into the next')
    if miss: print('  words the transcript did not give back (check by ear):', miss)
    return bad
track = np.zeros(int(DUR * SR) + SR); VO = {}; bad = 0
for take in CFG['takes']:
    bad += lay(take['file'], [dict(at=None, **l) if 'at' not in l else l for l in take['lines']], track, VO)
if bad and not os.environ.get('VO_FORCE'): sys.exit(f'{bad} line(s) are cut wrong: not writing the voice track')
WAV, JS = CFG.get('wav', 'audio/vo.wav'), CFG.get('js', 'assets/vo.js')
for p in (WAV, JS): os.makedirs(os.path.dirname(p) or '.', exist_ok=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f64le', '-ar', str(SR), '-ac', '1', '-i', '-', '-af',
                'highpass=f=85,equalizer=f=3200:t=q:w=1.1:g=2,equalizer=f=230:t=q:w=1.0:g=-1.5,acompressor=threshold=-24dB:ratio=3:attack=6:release=110:makeup=2',
                '-c:a', 'pcm_s24le', WAV], input=track[:int(DUR * SR)].tobytes(), check=True)
open(JS, 'w').write('// written by scripts/vo.py: when each spoken line starts (seconds)\nwindow.VO=' + json.dumps(VO) + ';\n')
print('wrote', WAV, 'and', JS)
