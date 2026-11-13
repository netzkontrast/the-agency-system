#!/usr/bin/env python3
"""srt.py — subtitles from the measured word map: SRT (or WebVTT) cues per lyric line, optional ASS karaoke.

Usage:
  python3 srt.py [--words songmap/words.json] [--out out/film.srt] [--format srt|vtt|ass] [--offset 0]
                 [--max-chars 42] [--min-dur 0.8] [--gap 0.08] [--lead 0.1] [--end <film length s>]

Text comes from words.json, i.e. from the real / streaming lyrics the alignment was given — never from a phonetic
generation prompt. A line longer than --max-chars is split into two rows at the word nearest the middle; a line
longer than two rows becomes two cues split at the word boundary nearest the middle in time.
Cue timing: starts --lead before the first word, holds at least --min-dur, ends --gap before the next cue.
With --end, a line sung in the film's last 0.3 s or later is dropped and the rest are clipped to the end.
ASS output highlights each word on its sung time (\\k tags) for karaoke-style burn-in.
Pure Python; no dependencies.
"""
import argparse, json, os


def ts(t, sep=','):
    t = max(0.0, t)
    h, rem = divmod(int(round(t * 1000)), 3600000)
    m, rem = divmod(rem, 60000)
    s, ms = divmod(rem, 1000)
    return f'{h:02d}:{m:02d}:{s:02d}{sep}{ms:03d}'


def ass_ts(t):
    t = max(0.0, t)
    h, rem = divmod(int(round(t * 100)), 360000)
    m, rem = divmod(rem, 6000)
    s, cs = divmod(rem, 100)
    return f'{h:d}:{m:02d}:{s:02d}.{cs:02d}'


def wrap(words, max_chars):
    text = ' '.join(w['w'] for w in words)
    if len(text) <= max_chars:
        return text
    best, best_d = 1, 1e9
    for i in range(1, len(words)):
        left = len(' '.join(w['w'] for w in words[:i]))
        d = abs(left - len(text) / 2)
        if d < best_d:
            best, best_d = i, d
    return ' '.join(w['w'] for w in words[:best]) + '\n' + ' '.join(w['w'] for w in words[best:])


def cues_from(data, max_chars):
    by_line = {}
    for w in data['words']:
        by_line.setdefault(w['line'], []).append(w)
    cues = []
    for li in sorted(by_line):
        ws = by_line[li]
        if len(' '.join(w['w'] for w in ws)) > 2 * max_chars and len(ws) > 1:
            mid_t = (ws[0]['t'] + ws[-1]['end']) / 2
            k = min(range(1, len(ws)), key=lambda i: abs(ws[i]['t'] - mid_t))
            parts = [ws[:k], ws[k:]]
        else:
            parts = [ws]
        for p in parts:
            cues.append({'t': p[0]['t'], 'end': p[-1]['end'], 'words': p})
    return cues


def time_cues(cues, lead, min_dur, gap, offset):
    for i, c in enumerate(cues):
        c['a'] = c['t'] - lead - offset
        nxt = cues[i + 1]['t'] - lead - offset if i + 1 < len(cues) else None
        end = max(c['end'] - offset, c['a'] + min_dur)
        c['b'] = min(end, nxt - gap) if nxt is not None else end
        if c['b'] <= c['a']:
            c['b'] = c['a'] + 0.3
    return cues


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--words', default='songmap/words.json')
    ap.add_argument('--out', default='out/film.srt')
    ap.add_argument('--format', default=None, choices=['srt', 'vtt', 'ass'])
    ap.add_argument('--offset', type=float, default=0.0)
    ap.add_argument('--max-chars', type=int, default=42)
    ap.add_argument('--min-dur', type=float, default=0.8)
    ap.add_argument('--gap', type=float, default=0.08)
    ap.add_argument('--lead', type=float, default=0.1)
    ap.add_argument('--end', type=float, default=None, help='film length in seconds: drop/clip cues past it')
    a = ap.parse_args()
    fmt = a.format or os.path.splitext(a.out)[1].lstrip('.') or 'srt'
    data = json.load(open(a.words, encoding='utf-8'))
    cues = time_cues(cues_from(data, a.max_chars), a.lead, a.min_dur, a.gap, a.offset)
    if a.end is not None:
        cues = [c for c in cues if c['t'] - a.offset < a.end - 0.3]   # a line sung in the last 0.3 s cannot be read
        for c in cues:
            c['b'] = min(c['b'], a.end)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, 'w', encoding='utf-8') as f:
        if fmt == 'srt':
            for i, c in enumerate(cues, 1):
                f.write(f"{i}\n{ts(c['a'])} --> {ts(c['b'])}\n{wrap(c['words'], a.max_chars)}\n\n")
        elif fmt == 'vtt':
            f.write('WEBVTT\n\n')
            for c in cues:
                f.write(f"{ts(c['a'], '.')} --> {ts(c['b'], '.')}\n{wrap(c['words'], a.max_chars)}\n\n")
        else:
            f.write('[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\n\n[V4+ Styles]\n'
                    'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, '
                    'StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n'
                    'Style: Lyric,Arial,54,&H00FFFFFF,&H0088AAFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,3,0,2,80,80,70,1\n\n'
                    '[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n')
            for c in cues:
                parts, cur = [], c['a']
                for w in c['words']:
                    start = w['t'] - a.offset
                    if start > cur:
                        parts.append(f'{{\\k{int(round((start - cur) * 100))}}}')
                    parts.append(f"{{\\k{max(1, int(round((w['end'] - w['t']) * 100)))}}}{w['w']} ")
                    cur = w['end'] - a.offset
                f.write(f"Dialogue: 0,{ass_ts(c['a'])},{ass_ts(c['b'])},Lyric,,0,0,0,,{''.join(parts).strip()}\n")
    print(f'{a.out}: {len(cues)} cues ({fmt})')


if __name__ == '__main__':
    main()
