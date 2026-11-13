#!/usr/bin/env python3
"""beat_this_track.py — beats and downbeats with beat_this (CPJKU, MIT code and weights), a stronger tracker than the
numpy bar map for songs with soft onsets, swing or tempo ramps.

Usage:  python -I beat_this_track.py <song.wav|mp3> [--out songmap/beats.json] [--device cpu|cuda] [--checkpoint final0]
Then:   python3 songmap_js.py --beatmap songmap/beatmap.json --beats songmap/beats.json --words songmap/words.json
Install: pip install beat-this   (pulls torch; optional — tools/audio/beatmap.py works without it)
"""
import argparse, json, os, sys


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('audio')
    ap.add_argument('--out', default='songmap/beats.json')
    ap.add_argument('--device', default='cpu')
    ap.add_argument('--checkpoint', default='final0')
    a = ap.parse_args()
    try:
        from beat_this.inference import File2Beat
    except ImportError:
        sys.exit('beat_this_track: beat_this is not installed (pip install beat-this); tools/audio/beatmap.py needs only numpy/scipy')
    beats, downbeats = File2Beat(checkpoint_path=a.checkpoint, device=a.device, dbn=False)(a.audio)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    json.dump({'source': os.path.basename(a.audio), 'tracker': 'beat_this', 'beats': [round(float(x), 4) for x in beats],
               'downbeats': [round(float(x), 4) for x in downbeats]}, open(a.out, 'w'), indent=1)
    print(f'{a.out}: {len(beats)} beats, {len(downbeats)} downbeats')


if __name__ == '__main__':
    main()
