# Genre-Konzeption: Systemischer Kollaps

**Provenance:** Vom User in Session vom 2026-05-20 bereitgestellt.
**Verwendung:** Sonic-Direction Input für Album-Conceptualizer Phase 3.2 und
Per-Track-Sound-Brief für Phase 3.5.

---

**Obergenre:** Post-Grunge meets Dark Shoegaze & Industrial Ambient

**Sound-DNA:**
Eine Verschmelzung aus der rohen, ungeschönten Laut-Leise-Dynamik der 90er
(Nirvana, Pixies) und erdrückenden, dichten Soundwänden (My Bloody Valentine,
Deftones). Das Klangbild nutzt Störgeräusche, unvorhersehbare Rhythmuswechsel
und vielschichtige Vocal-Texturen, um das Verlassen des emotionalen
Toleranzfensters und den ständigen Kampf um innere Kohärenz physisch spürbar
zu machen.

---

## Klangliche Schwerpunkte der 7 Tracks

### Track 1 — Deceptive Soft-Grunge
Beginnt trügerisch aufgeräumt und klanglich zugänglich, wird aber durch stetig
ansteigendes, unterschwelliges Rauschen (Static) und subtile Dissonanzen
destabilisiert. Die akustische Fassade bröckelt.

### Track 2 — Classic 90s Grunge / Noise-Rock
Der Riss im System. Stoisch pumpender Bass in den Strophen trifft auf eine
aggressive, mehrstimmige Wall-of-Sound im Refrain. Fremde, destruktive Stimmen
übernehmen die klangliche Führung.

### Track 3 — Heavy Doomgaze / Sludge
Klaustrophobisch und schleppend. Ein massiver, tiefer Sound, der an
Unterwasser-Druck erinnert. Das Tempo drosselt sich drastisch, dröhnende
Gitarrenwände erdrücken die Lead-Vocals, um den kompletten Kontrollverlust und
die Panik zu vertonen.

### Track 4 — Dark Ambient / Spoken Word
Der absolute Nullpunkt. Minimalistisch, kühl und beinahe völlig befreit von
Rhythmus. Isoliert stehende, intime und trockene Vocals schweben über leeren,
dunklen Bass-Drones. Ein akustisches Vakuum der Erschöpfung.

### Track 5 — Melancholic Dream-Pop / Shoegaze
Ätherisch und harmonisch tröstlich, aber tief in Reverb und Delay getaucht.
Der Sound simuliert eine betäubende Flucht in eine künstliche, weiche Realität
— ein bittersüßes, trügerisches Paradies.

### Track 6 — Driving Post-Punk / Industrial Rock
Mechanisch treibend, aggressiv und zwingend. Harte, synthetische Beats mischen
sich mit stark verzerrten Gitarren. Der klangliche Ausdruck eines
verzweifelten Kraftaufwands und des Aufbäumens gegen die innere Lethargie.

### Track 7 — Epic Post-Rock / Noise-Loop
Ein ausufernder, sich stetig verdichtender Aufbau, der in einem chaotischen
instrumentalen Höhepunkt kollabiert. Das Outro verfällt in ein präzises,
loopartiges Störgeräusch, das exakt in den Anfang des ersten Tracks
überleitet — die musikalische Manifestation der endlosen Dauerschleife.

---

## Cross-Track-Dependencies

- **Track 1 ↔ Track 7:** müssen als Paar geplant werden. Track 7 Outro
  (Noise-Loop) MUSS exakt in Track 1 Intro überleiten. Gemeinsamer Noise-Layer
  als Anker.
- **Mastering:** Crossfade-Spec dokumentieren. Gapless-Playback im
  Distributor-Metadata erzwingen.
- **Mix-Engineer:** Track 7 Outro und Track 1 Intro zusammen designen.

## Genre-Coverage in `overrides/mastering-presets.yaml`

Bestehende Presets (per Pre-Conceptualizer-Audit 2026-05-20):
- `dark-ambient` (passt für Track 4)

Fehlende Presets (mastering-engineer Phase muss albumspezifisch erstellen,
NICHT in overrides):
- `post-grunge` / `soft-grunge` (Track 1)
- `noise-rock` (Track 2)
- `doomgaze` / `sludge` (Track 3)
- `dream-pop` / `shoegaze` (Track 5)
- `industrial-rock` / `post-punk` (Track 6)
- `post-rock` / `noise-loop` (Track 7)

Closest existing analogs als Startpunkt: `dark-electro-rock`, `gothic-rock`,
`alternative-rock` (-12 bis -13 LUFS), `dark-ambient`/`drone`.
