#!/usr/bin/env python3
"""align_lyrics.py — word-level times for KNOWN lyrics on a sung track, plus the stressed moment of every word.

Usage (run with python -I on downloaded media):
  python -I align_lyrics.py <song.wav|mp3> --lyrics lyrics.txt --out songmap/words.json [--lang de] [--model large-v3-turbo]
         [--stems auto|demucs|none] [--vocals vocals.wav] [--from-words raw.json]

Lyrics file: one sung line per line, exactly the real / streaming lyrics (never a phonetic generation prompt).
  [Verse 1] / [Chorus] tags start a section; blank lines are ignored; mark the key word of a line with *stars*
  ("lass *mich*, lass mich atmen"); without a mark the loudest word of the line is the key.

Pipeline:
  1. vocals: --vocals given → used; --stems demucs (or auto when demucs is installed) → htdemucs two-stem vocals;
     none → the full mix.
  2. alignment: stable-ts `model.align(audio, text, language)` on the vocals (forced alignment of the supplied text,
     not transcription). --from-words raw.json skips this and takes [{word, start, end}, …] from any aligner
     (whisperX, MFA, a hand-fixed file).
  3. stress: the loudness peak of the vocals inside each word (10 ms RMS) — impacts land there, not on the word start.
  4. lines: words are assigned to the lyric lines in order; each line gets t/end, its section and its key word.

Output (songmap/words.json):
  {"source", "language", "words": [{"w","t","end","stress","line"}], "lines": [{"i","text","section","t","end","key":{"w","t","stress"}}],
   "sections": [{"name","t","end"}]}
Needs numpy and ffmpeg; stable-ts (pip install stable-ts) for step 2; demucs for step 1.
"""
import argparse, json, os, re, subprocess, sys, tempfile

SR = 16000


def die(msg):
    sys.exit(f'align_lyrics: {msg}')


def parse_lyrics(path):
    lines, section = [], None
    for raw in open(path, encoding='utf-8'):
        s = raw.strip()
        if not s:
            continue
        m = re.fullmatch(r'\[(.+?)\]', s)
        if m:
            section = m.group(1).strip()
            continue
        words = s.split()
        key = next((i for i, w in enumerate(words) if w.startswith('*') and w.rstrip('.,;:!?…"\')').endswith('*')), None)
        clean = [w.replace('*', '') for w in words]
        lines.append({'text': ' '.join(clean), 'words': clean, 'key': key, 'section': section})
    if not lines:
        die(f'{path} holds no lyric lines')
    return lines


def norm(w):
    return re.sub(r"[^\w']+", '', w.lower())


def decode(path):
    import numpy as np
    r = subprocess.run(['ffmpeg', '-v', 'error', '-nostdin', '-i', path, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True)
    if r.returncode or not r.stdout:
        die(f'ffmpeg could not decode {path}: {r.stderr.decode(errors="replace")[:300]}')
    return np.frombuffer(r.stdout, '<f4').astype('float64')


def separate(audio, how, tmp):
    if how == 'none':
        return audio
    if how == 'auto':
        try:
            import demucs  # noqa: F401
        except ImportError:
            print('align_lyrics: demucs not installed, aligning on the full mix (pip install demucs for a vocal stem)', file=sys.stderr)
            return audio
    r = subprocess.run([sys.executable, '-m', 'demucs', '--two-stems=vocals', '-o', tmp, audio], capture_output=True, text=True)
    if r.returncode:
        die(f'demucs failed: {r.stderr[-400:]}')
    base = os.path.splitext(os.path.basename(audio))[0]
    for root, _, files in os.walk(tmp):
        if 'vocals.wav' in files and base in root:
            return os.path.join(root, 'vocals.wav')
    die('demucs ran but no vocals.wav was found')


def align(vocals, lines, lang, model_name):
    try:
        import stable_whisper
    except ImportError:
        die('stable-ts is not installed (pip install stable-ts), or pass --from-words with times from another aligner')
    model = stable_whisper.load_model(model_name)
    text = '\n'.join(l['text'] for l in lines)
    res = model.align(vocals, text, language=lang)
    out = []
    for seg in res.segments:
        for w in seg.words:
            out.append({'word': w.word.strip(), 'start': float(w.start), 'end': float(w.end)})
    return out


def stress_times(vocals_path, words):
    import numpy as np
    x = decode(vocals_path)
    hop = SR // 100  # 10 ms
    n = len(x) // hop
    rms = np.sqrt(np.mean(x[: n * hop].reshape(n, hop) ** 2, axis=1) + 1e-12)
    for w in words:
        a, b = int(w['t'] * 100), max(int(w['t'] * 100) + 1, int(w['end'] * 100))
        seg = rms[a:b]
        w['stress'] = round((a + int(np.argmax(seg))) / 100, 3) if len(seg) else w['t']
        w['_peak'] = float(seg.max()) if len(seg) else 0.0


def assign(raw, lines):
    """Walk the aligner's words against the lyric words in order; tolerate small spelling differences."""
    words, k = [], 0
    for li, line in enumerate(lines):
        for lw in line['words']:
            if k >= len(raw):
                die(f'aligner returned fewer words than the lyrics (stopped at line {li + 1}: "{line["text"]}")')
            r = raw[k]
            # skip aligner fragments that are not in the lyrics (breaths, ad-libs) when the next one matches
            if norm(r['word']) != norm(lw) and k + 1 < len(raw) and norm(raw[k + 1]['word']) == norm(lw):
                k += 1
                r = raw[k]
            words.append({'w': lw, 't': round(r['start'], 3), 'end': round(max(r['end'], r['start'] + 0.02), 3), 'line': li})
            k += 1
    return words


def build(lines, words, source, lang):
    out_lines, sections = [], []
    for li, line in enumerate(lines):
        ws = [w for w in words if w['line'] == li]
        key = ws[line['key']] if line['key'] is not None else max(ws, key=lambda w: w.get('_peak', 0))
        out_lines.append({'i': li, 'text': line['text'], 'section': line['section'], 't': ws[0]['t'], 'end': ws[-1]['end'],
                          'key': {'w': key['w'], 't': key['t'], 'stress': key.get('stress', key['t'])}})
        if line['section'] and (not sections or sections[-1]['name'] != line['section']):
            sections.append({'name': line['section'], 't': ws[0]['t']})
    for i, s in enumerate(sections):
        s['end'] = sections[i + 1]['t'] if i + 1 < len(sections) else out_lines[-1]['end']
    for w in words:
        w.pop('_peak', None)
    return {'source': os.path.basename(source), 'language': lang, 'words': words, 'lines': out_lines, 'sections': sections}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('audio')
    ap.add_argument('--lyrics', required=True)
    ap.add_argument('--out', default='songmap/words.json')
    ap.add_argument('--lang', default=None)
    ap.add_argument('--model', default='large-v3-turbo')
    ap.add_argument('--stems', default='auto', choices=['auto', 'demucs', 'none'])
    ap.add_argument('--vocals')
    ap.add_argument('--from-words', help='JSON list of {word,start,end} from another aligner')
    a = ap.parse_args()
    lines = parse_lyrics(a.lyrics)
    with tempfile.TemporaryDirectory() as tmp:
        vocals = a.vocals or separate(a.audio, a.stems, tmp)
        raw = json.load(open(a.from_words)) if a.from_words else align(vocals, lines, a.lang, a.model)
        words = assign(raw, lines)
        stress_times(vocals, words)
        data = build(lines, words, a.audio, a.lang)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    json.dump(data, open(a.out, 'w'), ensure_ascii=False, indent=1)
    print(f'{a.out}: {len(data["words"])} words, {len(data["lines"])} lines, {len(data["sections"])} sections')


if __name__ == '__main__':
    main()
