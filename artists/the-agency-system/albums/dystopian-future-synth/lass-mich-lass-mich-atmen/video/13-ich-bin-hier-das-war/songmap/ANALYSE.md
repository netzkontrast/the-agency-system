# Analyse — „Ich bin hier / Das war“ (Track 13)

Quelle: `audio/13-ich-bin-hier-das-war.mp3` (aus Google Drive), Suno-Clip `7863da98-…`, Modell v5.5. Gemessen mit ffmpeg
(ebur128, silencedetect), librosa (Onsets, Chroma, pyin, STFT) und faster-whisper (Wortzeiten). Alle Zeiten in Sekunden.

## 1. Eckdaten
| | |
|---|---|
| Länge | 138,12 s (2:18), Stereo 48 kHz, MP3 ~177 kbit/s |
| Tempo | **60 BPM** (librosa 60,09), Herzschlag-Raster, Phase 0,45 s |
| Tonart | **g-Moll** (Korrelation 0,86; relatives B-Dur 0,82). Wichtige Töne: B♭, G, D♯, D |
| Lautheit | **−13,3 LUFS** integriert, LRA 7,2 LU, True Peak **−1,0 dBFS** (an der Grenze, kein Spielraum) |
| Stereo | L/R-Korrelation 0,78, Seitensignal −9 dB zum Mittelsignal: breit, aber mono-kompatibel |
| Stille am Anfang | 0 bis 2,35 s unter −45 dB; der erste Herzschlag kommt bei ca. 2,4 s |

## 2. Aufbau (gemessen)
| Zeit | Teil | Pegel (RMS) | Inhalt |
|---|---|---|---|
| 0–2,4 | Stille | | nichts, dann der erste Puls |
| 1,7–8,0 | Intro | −25 dB | „Der Puls ist langsam. Der Puls ist meiner.“ (Stimme ab 1,7) |
| 8,6–21,5 | Instrumental 1 (13 s) | −17 dB | Pads, sehr dunkel (Spektralschwerpunkt 321 Hz) |
| 21,9–44,6 | Strophe 1 | −17,6 dB | vier Zeilen, je etwa 5 s |
| 44,6–58,7 | Refrain 1 | −15,3 dB | „Ich bin hier.“ / „Das war.“ / „Kein Sieg…“ / „Ich bin hier.“ |
| 61,5–78,6 | Strophe 2 | −16 dB | vier Zeilen, kürzer und dichter (4–5 s) |
| 78,6–92,8 | Refrain 2 | −15,4 dB | identische Wörter |
| 92,8–95,0 | Bridge | −22 dB | „Ich bin auch hier.“ (Kinderstimme, f0 ≈ 251 Hz) |
| 95,0–102,3 | Instrumental 2 (7 s) | **−12,9 dB** | fast nur Sub-Bass (89 % der Energie unter 120 Hz) |
| 102,3–108,4 | Outro 1 | −13 dB | „Ich bin hier. Das war.“ |
| 108,4–125,1 | Instrumental 3 (17 s) | **−12,3 dB** | der lauteste Teil des Songs |
| 125,1–132,5 | Outro 2 | −21,6 dB | „Ich bin hier.“ (125,1), „Das war.“ (130,7), Wiederholung, nicht im Lyric-Blatt |
| 133–138 | Ausklang | | Sub-Drone bei 55 Hz schwillt 134–136 an (−13 dB), dann Fade, letzte Sekunde −37 dB |

Auffällig: Die Dynamik-Spitze liegt **nicht** in der Stimme, sondern in den Instrumentalteilen nach der Bridge (95–125 s).
Die Stille nach der Bridge ist also kein Abfall, sondern ein Anschwellen.

## 3. Klang
- Sehr dunkel: 59–89 % der Energie unter 120 Hz, über 5 kHz fast nichts. Das Mittenband (300–3000 Hz) trägt die Stimme.
- Der Herzschlag steckt im Sub-Bereich (35–130 Hz); seine Abstände schwanken um 0,7–1,0 s, ein klares „Verlangsamen“
  ist nicht zu messen. Das Schlussbild des Songs ist statt dessen die 55-Hz-Drohne (A1) 133–137 s.
- Spektralschwerpunkt: Instrumental 1 und 2 um 320–370 Hz (dunkelster Klang), Refrains und Strophe 2 um 1000–1100 Hz.

## 4. Stimmen
- **Bariton, Sprechgesang**: f0 im Median 70–117 Hz; Strophe 1 höher (88–117 Hz), die Refrains liegen mit 70–78 Hz an
  der Messgrenze von 70 Hz, also vermutlich noch tiefer (nicht gesichert, pyin-Untergrenze).
- **Kinderstimme in der Bridge**: f0 251 Hz, 92,8–95,0 s. Das passt zur Vorgabe („einmal, Präsens, „Ich bin auch hier.“).
- **Zweiter hoher Einsatz (zu prüfen):** das letzte „Das war.“ bei 130,7 s misst f0 ≈ 311 Hz, deutlich höher als der Bariton
  (97 Hz bei „Ich bin hier.“ 125,1). Das kann eine zweite Kinderstimme sein, auch ein Messfehler. Bitte einmal nach Gehör prüfen.

## 5. Text gegen Audio
- 131 von 136 Textwörtern wurden vom Erkenner gefunden. Der Erkenner hörte u. a. „Kann sie kein Ende“ statt „Kein Sieg. Kein Ende“
  und „drehe“ statt „dreh“; die Streaming-Lyrics gelten (Zeiten sind interpoliert, wo der Erkenner abwich).
- **Abweichungen vom Lyric-Blatt:** Das Lied wiederholt „Ich bin hier. Das war.“ zweimal am Ende (102–108 und 125–132); im Blatt steht es einmal.
  Suno hat die Zeile im Instrumental-Outro erneut gesungen.
- **Länge:** Die Track-Datei verlangt 2:30–4:00, das Lied ist 2:18 lang und liegt darunter.
- Der Refrain ist doppelt so schnell gesungen wie geplant: Strophe 2 und Refrain 2 folgen fast ohne Pause (78,6 s direkt nach 78,1 s).

## 6. Folgen für das Video
- Das Lampenpuls-Raster beginnt erst beim ersten gehörten Herzschlag (2,4 s); davor ist Papier und Stille.
- Der lauteste Moment (108–125 s) braucht das größte Licht des Films (Licht über Wand und Boden, warm, ohne Blitz).
- Die Bridge (92,8–95 s) und die letzte „Das war.“ (130,7 s) sind Licht-Ereignisse der Kinderstimme: ein Lichtpunkt, nie eine Figur.
- Das Ende: die Drohne 134–136 s trägt den letzten Atemnebel; ab 137 s Papier.
- Die True-Peak-Reserve ist null: beim Mastern auf −14 LUFS (Dateiformat Plattform) bleibt der Pegel, beim Muxen nicht anheben.
