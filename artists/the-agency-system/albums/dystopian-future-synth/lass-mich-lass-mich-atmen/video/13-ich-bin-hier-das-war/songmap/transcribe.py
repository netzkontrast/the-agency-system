#!/usr/bin/env python3
"""transcribe.py — word times from the real audio with faster-whisper, snapped to the KNOWN lyrics.

faster-whisper hears the Sprechgesang (German); its words are matched to songmap/lyrics.txt (the streaming lyrics)
by sequence alignment, so the text is always ours and only the times come from the audio. Unmatched lyric words are
interpolated between matched neighbours. Writes songmap/heard.json (what the model heard) and songmap/words.json."""
import json, re, sys, difflib
import soundfile as sf
from faster_whisper import WhisperModel

audio = sys.argv[1]
model = WhisperModel(sys.argv[2] if len(sys.argv) > 2 else "small", device="cpu", compute_type="int8")
samples, sr = sf.read(audio, dtype='float32')   # decode here: the bundled av of some installs cannot open files itself
assert sr == 16000, 'give a 16 kHz mono wav'
segs, info = model.transcribe(samples, language="de", word_timestamps=True, vad_filter=False, beam_size=5, condition_on_previous_text=False)
heard = []
for s in segs:
    for w in s.words:
        heard.append({"w": w.word.strip(), "t": round(w.start, 3), "end": round(w.end, 3), "p": round(w.probability, 2)})
json.dump({"duration": info.duration, "words": heard}, open("songmap/heard.json", "w"), ensure_ascii=False, indent=1)
print(len(heard), "words heard,", info.duration, "s")
