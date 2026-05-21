# Chapter Zero — Suno-Feasibility Critique (Round 2)

**Reviewer role:** bitwize-music + Suno V5/V5.5 feasibility.
**Under review:** `DESIGN.md` **v2** (Round-1 critiques claimed closed).
**Verdict scale:** GO / NEEDS-CHANGE / WON'T-WORK
**Grounding:** suno-engineer / lyric-writer / lyric-reviewer / pronunciation-specialist / mix-engineer / mastering-engineer SKILLs; `overrides/suno-preferences.md` (vocals-first, max-2-genre, Exclude 2–4, descriptive-only metatags, parenthesized=backing); `reference/suno/v5-best-practices.md` (Personas, Custom Models, Pitch Transpose, token-bias list — cited from Round 1).

> **Bottom line up front.** v2 did the work. The §0 revision log is not vapor —
> I verified every CONCERN against §4/§8 and the recipes are actually specified
> with execution-grade detail, not just adjectives. The 5-layer KOH recipe, the
> Track 13 *harmonic* anti-heal, the Track 10 multi-pass comp, the post shot
> list, and the number/bracket/token-bias plan are all in the body, not just the
> log. **Track 10 is now genuinely GO. Track 13's anti-heal is harmonic, not
> cosmetic.** One Round-1 prerequisite remains physically unmet (the bucket-level
> genre README still does not exist on disk), and v2 introduced a couple of small
> recipe ambiguities worth tightening — none are blockers. Verdict: **GO** with a
> short NEEDS-CHANGE punch list for the next pass.

---

## 1 · Round-1 verification table

Status legend: **CLOSED** = recipe specified in §4/§8 with execution detail ·
**PARTIAL** = addressed but under-specified or a real-world prerequisite still
unmet · **NOT-ADDRESSED** = absent.

### Major concerns (C1–C5)

| Concern | Status | Evidence (v2 §/line) |
|---|---|---|
| **C1 — 5-layer manufactured KOH spine** | **CLOSED** | §4 "MANUFACTURED 5-layer mix asset" header L202; **Layer A** owned single-C-drone master stem + edits-to-one-file automation + lay-under-each-track L208–215; **Layer B** verbatim anchor `sustained low C drone underpinning, sub-bass continuo, cold, no key change` on all 13 L216–219; **Layer C** host Persona on T1/2/3/6/10/11/12/13 + optional watch Persona + "DROP gender/register from box when Persona carries them" L220–227; **Layer D** lock C minor globally, detune in owned stem not via Suno, Pitch Transpose for off-key L228–231; **Layer E** state-biased mastering per state-axis L232–239. Density ladder literal-to-number L241–260. |
| **C2 — Track 13 anti-heal (harmonic, not adjectival)** | **CLOSED** | §8 "anti-heal plan" L559–575 + §4 S4 row L275. Harmonic refusal is explicit: "stay **minor**, **refuse the tonic resolution**, end on an **open interval (2nd or b6, never the root C)**, **no major third**; consider **Phrygian/Locrian**" L563–566 and "Write the *melody/lyric* to stop off the tonic, not just the prompt" L566. 4-item Exclude budget `no warmth, no major key, no reverb bloom, no uplifting resolution` L567–568. Dry/no-reverb L569. Owned-MIDI-arp fallback L572–573. "Plan **2–3 rolls**" (= flagged highest-iteration) L575 + §3 T13 "highest-iteration track" §8 L546. |
| **C3 — Two narrator intros as separate clips, 2–4 lines** | **CLOSED** | §8 "Narrator intros" L577–582: "Generate the two narrator intros (Tracks 1, 7) as **separate short clips**… keep direct-address to **2–4 lines**, then hard-cut to `[Verse 1]`." Mirrored §3 T1 L168 / T7 L174 and §4 narrator-mode fingerprint L336–338. "echo" token-bias watch carried L582. |
| **C4 — Per-track style boxes + NEEDS-CHANGE flags + T10 → GO** | **CLOSED** | §8 style-box rules L529–531: "vocals FIRST; max 2 genre tags / 4–7 total descriptors; descriptive vocal metatag only at each voice change (never a function name, never a personal name); include Layer B anchor verbatim." Per-track flags L533–546 (T1/3/6/9/10/11/12/13). **T10 multi-pass comp** L548–557 (host-Persona bed + per-echo-voice generations + 12-stem extraction + phase-offset comp). Naming gate L390–393. |
| **C5 — Post shot list + numbers/brackets + token-bias + bucket README** | **PARTIAL** | Shot list present §8 L584–594 (boot, ritard-reboot, KOH cliff, datamosh, shatter, collapse-crush, sterile arp). No-brackets-in-lyric-bodies L602–603. Numbers-spelled-as-words (Suno box only, standard in streaming) with a full per-value list L606–612. Token-bias house default `Do not change any words. Sing exactly as written.` L613–617. Per-track Pronunciation Notes plan L598–600. **BUT** the bucket-level genre README is listed as a *prerequisite* (§8 L514–518) yet **still does not exist on disk** — `artists/the-agency-system/albums/dystopian-future-synth/` contains only `chapter-zero/` and `lass-mich-lass-mich-atmen/`, no bucket-level `.md`. Plan is correct; the artifact is not yet created. Acceptable for concept stage (it's a pre-generation prerequisite, not a design defect), hence PARTIAL not CLOSED. |

### Quick-wins (10)

| # | Quick-win | Status | Evidence |
|---|---|---|---|
| 1 | Build host Persona before Track 1 | **CLOSED** | §8 prereq #2 L520–523; §4 Layer C L220–223. |
| 2 | Own the KOH drone as a separate automated stem | **CLOSED** | §8 prereq #3 L524–525; §4 Layer A L208–215. |
| 3 | Generate narrator intros (1, 7) as separate short clips | **CLOSED** | §8 L577–582. |
| 4 | `Do not change any words…` token-bias default on every box | **CLOSED** | §8 L613–617. |
| 5 | Spell every number, strip every bracket; log in Pronunciation Notes | **CLOSED** | §8 L602–612 + L598–600. |
| 6 | Track 10 as multi-pass comp, budget the labor | **CLOSED** | §8 L548–557 ("Budget this as the album's most labour-intensive track"). |
| 7 | Reserve T13 exclude budget + write melody to refuse tonic, expect 2–3 rolls | **CLOSED** | §8 L563–575. |
| 8 | Create the missing bucket-level genre README | **PARTIAL** | Documented as prereq §8 L514–518 with concrete word-count ceilings; **file not yet created on disk** (see C5). |
| 9 | Per-track genre mastering overrides + state-axis LUFS/LRA bias | **CLOSED** | §4 Layer E L232–239 (one pass per genre cluster + per-track overrides, mastering SKILL Step 1.5). |
| 10 | Boot/ritard-reboot/glitch/shatter/KOH-cliff as a post shot list | **CLOSED** | §8 L584–594. |

**Tally: 15 items tracked (C1–C5 + 10 quick-wins). CLOSED = 13. PARTIAL = 2
(C5 and QW8 — the same root cause: the bucket README is planned but not yet a
file). NOT-ADDRESSED = 0.**

---

## 2 · Fresh pass — new findings (v2-introduced)

I checked the recipes for *correct specification* against the SKILL rules, and
probed for problems v2 created while closing Round 1.

### Recipe-correctness spot checks (all PASS)

- **Persona rule (drop gender/register from box when Persona carries them):**
  correctly stated §4 L226–227 and §8 L523. **PASS.**
- **Exclude Styles ≤ 4:** T13 spends exactly 4, explicitly "(the max)" §8 L567.
  Matches `suno-preferences.md` L167 (2–4). **PASS.**
- **Vocals-first / max-2-genre / 4–7 descriptors:** stated as the universal
  style-box rule §8 L529–531; matches `suno-preferences.md` L39–40. **PASS.**
- **Numbers spelled in Suno box only, standard in streaming:** §8 L606 says
  exactly that ("streaming lyrics keep standard form"). **PASS.**
- **No square brackets in lyric bodies:** §8 L602–603 converts the two log
  lines to plain spoken text; brackets reserved for section/voice tags. **PASS.**
- **Descriptive vocal metatag, never a name:** §5 L357–369 + naming gate
  L390–393 + §4 voice fingerprints are all function/descriptor form. **PASS.**
- **Track 10 genuinely GO:** the comp recipe (separate per-voice generations →
  12-stem extraction → phase-offset comp) is the correct platform-true method
  for >2 simultaneous distinct registers. **Confirmed GO**, no longer WON'T-WORK.
- **Track 13 anti-heal is harmonic, not just adjectives:** confirmed — refuse
  tonic / open-interval landing / no major third / modal colour, with the lever
  written into the *melody*, not only the prompt. **Confirmed.**

### NEW-1 — `[Verse 1]` after a separate narrator clip is a no-op (NEEDS-CHANGE, minor)

§8 L581 says keep the narrator intro to 2–4 lines "then hard-cut to `[Verse 1]`."
But the same paragraph (and C3) generates the intro as its **own separate clip**.
A section tag inside clip A does not bridge to clip B — the "hard-cut to
`[Verse 1]`" happens in the **mix/edit butt-join**, not via a tag. State that the
intro clip ends and the sung body is a *separate generation* whose own lyrics
begin at `[Verse 1]`/`[Intro]`. Cosmetic wording fix; no feasibility risk.

### NEW-2 — "K-O-H" spell-out vs. token-bias guard interaction (NEEDS-CHANGE, minor)

§8 L603 renders the protocol line as "protocol K-O-H one point zero, initiated."
Spelling the acronym letter-by-letter is the right call (Suno would otherwise say
"koh"/"co"). But verify the lyric-writer doesn't also leave a literal `KOH` token
elsewhere — and note that the album-wide `Do not change any words` guard L613–617
can *fight* deliberate phonetic spellings if the box also contains the standard
form. Resolution: the **Suno box carries only the spelled form**; the guard then
protects it. Make that ordering explicit so pronunciation-specialist and the
token-bias guard don't contradict (the guard says "sing exactly as written" —
so "as written" must already be the phonetic form). One sentence in §8.

### NEW-3 — Track 9 accelerando + mid-track KOH cliff + datamosh in one generation (NEEDS-CHANGE, watch)

v2 correctly moved the datamosh and the 0.991→0.21 cliff to owned-stem/post
(§8 L590–591). Good. Residual risk: the *generated* Track 9 body must still
carry an in-track accelerando (116, accelerating, §3 L176) AND survive having a
collapsing owned-stem laid under it. Suno honors a single accelerando
instruction unreliably across a 3–4 min generation. Recommend: generate Track 9
at a **fixed 116** and impose any accel feel via the post layer / arrangement,
OR split-generate (pre-cliff vs post-cliff) like Track 11 already plans (§8
"open decisions" #2 L643–644). Flag, not a blocker.

### NEW-4 — Two Personas on overlapping tracks (T6, T11, T12) (INFO, verify)

§4 Layer C puts the **host** Persona on T6/11/12 *and* the **watch** Persona on
T6/11/12. Within one generation Suno applies one Persona. Where both the
proto-host and the system speak in the same track (6, 11, 12), each Persona must
drive its **own section/sub-generation** — i.e. these are multi-Persona tracks
that may need the same per-voice-generation discipline as Track 10 (lighter,
since they're sequential not stacked). The design implies this ("voices are
sequential here, manageable" T12 §8 L545) but doesn't say *which Persona owns
which section*. Add a one-line Persona-assignment-per-section note for 6/11/12.
Low risk; sequential voices are well within platform.

### NEW-5 — Bucket README word-count ceiling vs. lyric density (INFO)

§8 L517–518 sets 140–220 words (ambient) / cap ~200–350 (rock). Sound ceilings.
Once the README is actually created (QW8), make sure the per-track Target
Duration is set too, or the lyric-reviewer density gate (item 12) reads a word
ceiling with no duration and can still mis-fire. Bundle duration + density when
creating the file.

**No new WON'T-WORK items. No new blockers.** All five fresh findings are
NEEDS-CHANGE-minor or INFO.

---

## 3 · Overall verdict

v2 is a genuine, verifiable close-out of Round 1, not a log-deep claim. The two
platform-edge items from Round 1 are resolved: **Track 10 is GO** via multi-pass
comp, and **the continuous KOH spine is GO** as an owned-stem mix asset (never a
generation). **Track 13's anti-heal is harmonic** (tonic refusal / open-interval
/ no major third / modal colour written into the melody), which was the load-
bearing requirement. The number/bracket/token-bias hazards are fully planned.

The single real-world gap is that the **bucket-level genre README is specified
but not yet created on disk** — correctly a pre-generation prerequisite, so it
does not block concept-stage sign-off, but it must be the first build action
before lyric-writer runs (else the density/pacing gates silently no-op). The
five fresh findings are wording/assignment tightenings, none feasibility-fatal.

**Per-concern verdict:** C1 GO · C2 GO · C3 GO (NEW-1 wording) · C4 GO · C5
GO-pending-README. **Overall: GO** — buildable in Suno via the bitwize chain as
specified, with a 5-item NEEDS-CHANGE punch list (NEW-1…5) and the README
prerequisite to clear before generation.

VERDICT: GO · BLOCKERS=0 · NEEDS_CHANGE=5 · ROUND1_CLOSED=13/15
