#!/usr/bin/env python3
"""songmap_js.py — merge the bar map and the word map into the film's songmap.js (window.SONGMAP for engine/lib/beat.js).

Usage:
  python3 songmap_js.py [--beatmap songmap/beatmap.json] [--words songmap/words.json] [--beats songmap/beats.json]
                        [--offset 0] [--out songmap.js]

--beatmap  tools/audio/beatmap.py output (beats, downbeats, sections, drop, hits, stops); film seconds
--beats    optional {"beats": [...], "downbeats": [...]} from a stronger tracker (tools/audio/beat_this_track.py);
           replaces beatmap.json's beats and downbeats when given
--words    tools/audio/align_lyrics.py output (words, lines, lyric sections)
--offset   seconds to subtract from every time (when the film starts later in the song than the bar map)
Sections: the lyric sections (from [Verse]/[Chorus] tags) win when present; otherwise the bar map's energy sections.
"""
import argparse, json, os, sys


def shift(v, off):
    if isinstance(v, (int, float)):
        return round(v - off, 4)
    if isinstance(v, list):
        return [shift(x, off) for x in v]
    if isinstance(v, dict):
        return {k: (shift(x, off) if k in ('t', 'end', 'stress') or isinstance(x, (list, dict)) else x) for k, x in v.items()}
    return v


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--beatmap', default='songmap/beatmap.json')
    ap.add_argument('--beats')
    ap.add_argument('--words', default='songmap/words.json')
    ap.add_argument('--offset', type=float, default=0.0)
    ap.add_argument('--out', default='songmap.js')
    a = ap.parse_args()
    m = {}
    if os.path.exists(a.beatmap):
        b = json.load(open(a.beatmap))
        m.update({k: b.get(k) for k in ('bpm', 'beats', 'downbeats', 'drop', 'hits', 'stops') if b.get(k) is not None})
        m['sections'] = [{'name': s.get('name'), 'kind': s.get('kind'), 't': s.get('t'), 'end': s.get('end')} for s in b.get('sections', [])]
        m['duration'] = b.get('duration')
    if a.beats:
        bt = json.load(open(a.beats))
        m['beats'], m['downbeats'] = bt['beats'], bt['downbeats']
    if os.path.exists(a.words):
        w = json.load(open(a.words))
        m['words'], m['lines'] = w['words'], w['lines']
        if w.get('sections'):
            m['sections'] = [{'name': s['name'], 'kind': 'lyric', 't': s['t'], 'end': s['end']} for s in w['sections']]
    if not m:
        sys.exit(f'songmap_js: neither {a.beatmap} nor {a.words} exists')
    if m.get('hits'):
        m['lastHit'] = m['hits'][-1]
    if a.offset:
        m = {k: (v if k in ('bpm', 'duration') else shift(v, a.offset)) for k, v in m.items()}
    for k in ('beats', 'downbeats'):
        if k in m and any(x >= y for x, y in zip(m[k], m[k][1:])):
            sys.exit(f'songmap_js: {k} are not strictly increasing')
    with open(a.out, 'w') as f:
        f.write('// written by tools/audio/songmap_js.py — do not edit by hand; re-run after any change to the song map\n')
        f.write('window.SONGMAP = ' + json.dumps(m, ensure_ascii=False, separators=(',', ':')) + ';\n')
    print(f"{a.out}: {len(m.get('beats', []))} beats, {len(m.get('downbeats', []))} bars, {len(m.get('words', []))} words, "
          f"{len(m.get('sections', []))} sections{', drop ' + str(m['drop']) if m.get('drop') is not None else ''}")


if __name__ == '__main__':
    main()
