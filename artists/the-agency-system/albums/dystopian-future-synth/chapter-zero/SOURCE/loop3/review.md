# Chapter Zero — Review (FEASIBILITY LENS)

> **Agent:** Review Agent (Phase 3), feasibility lens. I am a bitwize-music +
> Suno V5/V5.5 build advocate. I weigh the three concern-pure designs (FID =
> `design-fidelity.md`, FEA = `design-feasibility.md`, ACC = `design-accessibility.md`)
> and the adversarial clash set against ONE question: **will it build cleanly and
> reliably in Suno through the bitwize chain?** I take positions and recommend
> resolutions for the Opus arbiter; I do not edit the designs.
> **Walls honored as fixed:** the two LOCKED decisions (T10 hybrid round→stack;
> T9 tight/airless/mid-volume), source truth, `name_exposure`, and the loop2
> 11-item work-order.
> **Grounding checked against** `overrides/suno-preferences.md` (genre maps L18–28,
> register table L53–64, Avoid list L70–96, parenthesis hazard L119) and
> `overrides/mastering-presets.yaml`.

---

## 0 · Headline

**The reconciled set is buildable in Suno through the bitwize chain — and it is
buildable precisely *because* FEA's "move everything Suno can't do off the
generator" architecture is already the shared spine across all three designs
(adversarial Consensus 5, 11).** Nothing in the reconciled album asks Suno to do
a thing Suno does badly *as a prompt* — every fragile gesture (continuous KOH
curve, ritard-reboot, datamosh, KOH cliff, shatter, collapse crush, accel feel)
is an owned-stem or post move. The two genuinely build-relevant fights are
**Clash 5 (polyphony)** and **Clash 4 (T9 numbers)**; the three BREACH clashes
(1/2/3) are essentially build-neutral, so feasibility has no veto there and I
defer to the source/aesthetic walls. **I veto nothing as unbuildable.** The one
thing I insist on as a build prerequisite is FEA's discipline being adopted
wholesale, not partially.

---

## 1 · Per-clash table (feasibility lens)

| # | Clash | Buildable? | Suno/bitwize reason | Can I compromise? | Recommended resolution (feasibility) |
|---|---|---|---|---|---|
| **1** | Founding-axiom wording: "prevents" vs "keeps" | **Both buildable — build-NEUTRAL** | Suno sings either string identically; both are clean monosyllable-led hooks under `Do not change any words. Sing exactly as written.`. No token-bias collision on either. Front-stressed /k/ ("keeps") is *marginally* more reliably enunciated than the consonant cluster "prevents" (V5 occasionally softens "pr-" attack), but the delta is sub-threshold and a Persona + the guard line erase it. | n/a — I have no build stake | **Source wins: verbatim "prevents."** It is a verbatim-locked-axiom BREACH, not a tradeoff, and feasibility gives ACC nothing to trade for — the singability gain is negligible. Recommend the arbiter rule the reword out and accept the locked line as the hook. If V5 ever drops the "pr-" attack on a roll, fix with a `[clear attack]` inline tag, not a reword. |
| **2** | T13 warm melodic ghost under the coda | **Trivially buildable — and that is the danger** | The ghost is a 1–2 s owned stem (the T3 warm fragment) laid under a generation in the mix — zero Suno risk, it never touches a prompt. So feasibility *cannot* veto it on build grounds; it is the cheapest gesture on the album. **But** building it cleanly means it WILL be audible and WILL read as the production narrating grief — the build does not protect the aesthetic. It also lightly fights `suno-preferences` Avoid (warmth/comfort) only if it ever leaked into a *prompt*; as a post stem it doesn't. | Yes — I can build it OR omit it with equal ease | **Omit the ghost (defer to the no-Kintsugi wall).** Buildability is not the deciding axis here; the wall is. Since removing it is *also* the cheaper build (one fewer owned stem, one fewer mix dependency that ACC itself flags as "a hard continuity dependency"), feasibility *agrees* with FID. If the arbiter wants a cold-listener safety net, build it as a **non-melodic** sub-stem artifact (a single detuned partial of the drone, not the recognizable T3 tune) — that is buildable, orientation-giving, and doesn't narrate. |
| **3** | T3 deliberate prettiness | **Buildable — but the costliest build to the album's coherence** | A genuinely consonant, "pretty" melodic phrase IS generatable (warm soprano, vowel-forward legato — `suno-preferences` L58). The cost is downstream: it forces a **mastering exception**. Every other track masters cold/dark in one pass per genre cluster; a track carrying real consonant beauty wants a different tonal-balance target or it either (a) gets crushed cold and loses the prettiness anyway, or (b) the cluster pass softens to accommodate it and the *neighbors* warm up. Either way it breaks the "one pass per cluster" economy and risks the album's tonal coherence. | Yes — partially | **Render T3 warm but NOT "pretty/consonant" (lean FID, with a feasibility nuance).** The buildable-and-coherent version is FID's "trügerische Atempause": warm *timbre*, flat *affect*, modal-not-consonant melody. That builds in the same electroacoustic cluster pass as T1/T2/T7, needs no mastering exception, and still gives the warm-voice register a distinct seed to reuse. ACC's claim that a stranger needs ONE consonant anchor is real but is better served by the *register contrast* (soprano vs the cold monotone everywhere else) than by tonal consonance. Resolves Clash 2's root too (no pretty T3 ⇒ no pretty ghost to callback). |
| **4** | T9 paradox numbers: sung vs stripped | **Both buildable — STRIP is the cleaner gen** | This is the one number call with a real build delta. T9 is the album's hardest gen: compressed, airless, mid-volume, mirror-echo doubled-and-phase-offset lead, dense industrial bed. Reciting "zero point eight four → zero point nine nine" inside that bed is exactly where V5 mangles diction — decimals are multi-token, unstressed, and compete with the self-attack texture for the same midrange. Spelled-out long decimals also burn rolls (Suno re-orders or drops digits ~1 in 3 on dense industrial). Stripping removes the single most roll-burning element from the least-reliable track. | Yes — the routing's middle option is the compromise | **Strip from sung lyric (FEA+ACC, 2-vs-1), BUT take the unclaimed middle option as a feasibility hedge:** render 0.84/0.99 as **owned-stem texture** — a thin rising spoken-low artifact buried in the post layer / the KOH cliff automation, NOT a sung vocal line. This keeps the audible counter-motion FID wants (paradox rising while the drone crashes to 0.21) WITHOUT putting decimals in the fragile generated vocal. FID's fidelity claim is satisfied by *audibility*, not by *Suno singing it*. Best of both; cleanest possible T9 gen. Numbers stay sung only where uncrowded: T8, T11, T13, and T7's single 0.41 (Consensus 10). |
| **5** | Polyphony default (T3/T5/T12): one-mind-fracturing vs sequential | **Simultaneous distinct voices = UNBUILDABLE as a prompt; sequential = buildable; comp+stems = buildable** | **Hard build fact: V5 collapses simultaneous distinct lead voices into one smeared timbre or picks one and drops the other.** You cannot prompt "two different registers singing different words at the same time" and get two legible voices — it is the single most reliable Suno failure mode. So *prompted* simultaneity is genuinely unbuildable. BUT the "one mind fracturing" image does NOT require prompted simultaneity — it requires **comp + stem layering** (generate each register as its own short solo gen, 12-stem extract, layer in the mix), which is exactly the T10 LOCKED recipe. | Yes — strongly | **Reject FEA's *blanket* sequential default; adopt a per-track call (the adversarial's "tips into breach" warning is correct).** Buildability does not force sequential everywhere — it only forbids *prompted* simultaneity. The reconciliation: (a) **T5** is genuinely sequential by source (kinetic lead + logic denial *refrain* — they take turns; one gen, register-alternation — cheap, build it sequential, no loss). (b) **T3** warm-voice + reaching-voice: build sequential *for the gen*, but the proto-host bed underneath both means the "one mind" reading is carried by the shared HOST timbre, not by overlap — acceptable, low cost. (c) **T12** sweep/refusal/shatter genuinely take turns in the source (log → refusal → shatter) — sequential is faithful AND buildable, no comp needed. **The only place the source demands true simultaneity is T10's climactic stack — which is LOCKED and already a comp.** So: sequential where the source is sequential (T5/T12), shared-timbre-bed where it's "one mind" (T3), and comp-stack ONLY at T10's peak. This avoids the "crew menu" breach (the roster reading comes from *distinct characters taking turns as the whole event*; here the shared HOST timbre + the T10 stack keep it "one mind") and stays 100% buildable. |
| **6** | False-calm resets (T7/T8) density | **Trivially buildable — pure mix move** | Confirmed: the 0.61-dip→0.998 reset and the 0.991 hold are **owned-drone automation**, not generations (Consensus 5). "How clean" = how few partials/how little detune/saturation in the owned stem under those two tracks. That is a fader/automation decision in the DAW, costs nothing, and is fully reversible. FID's "full clean" and ACC's "ear-reset" point at *different automation values on the same one file* — there is no build fork at all. | n/a | **Build the drone to FULL CLEAN 0.998 at T7 and 0.991 at T8 (FID's structural reading).** Feasibility is indifferent to the value, so defer to source: the meter must lie. The gens themselves (clean sine pad T7, rising-tension detuned shimmer T8) already encode ACC's "too calm / loaded spring" feel in the *Suno bed* — so ACC's engagement goal is met by the generation while the owned drone stays honestly clean. Both served, one build. |
| **7** | T13 flatness depth (harmonic anti-heal) | **Buildable — the highest-iteration gen on the album, manage with the MIDI fallback** | The anti-heal (stay minor, refuse the tonic, open-interval end, no major third, Phrygian/Locrian colour, dry no-reverb) fights Suno's strong bias toward resolution — V5 *wants* to land on a consonant cadence, especially on a sparse sterile arp where it has room to "pretty up." Expect 2–3+ rolls. This is buildable but it is the track most likely to "heal" against intent. | n/a (build-method only) | **Adopt FEA's owned-MIDI minor-arp fallback as the PRIMARY plan, not the fallback.** Don't burn rolls fighting Suno's resolution bias on the most important ending of the album — author the sterile detuned arp as an **owned MIDI figure on an open interval (b6 or 2nd, never root C)** and let Suno carry only the vocal counting over it. The vocal is flat/affectless/dry (HOST Persona, A11) — that generates reliably. The harmonic anti-heal then lives in the owned stem where it is *guaranteed*, not gambled. Exclude budget exactly 4: `no warmth, no major key, no reverb bloom, no uplifting resolution`. Flatness-depth (the FID-vs-ACC tone question) is satisfied at full strength because the open interval is authored, not generated. |

---

## 2 · Most / least buildable design — what to borrow

**Most buildable: FEA**, by construction — it is the only design organized
around the platform's actual failure modes (Suno makes clips not albums; it
can't run a shared oscillator; it collapses simultaneous voices; it mangles
dense decimals; it normalizes broken phrasing). Its architecture — **2 Personas,
one owned C-drone master stem carrying the entire numeric curve, flat-BPM gens
(T6 flat-80, T9 flat-116) with accel/ritard moved to post, the Gen/Own/Post
column on every track, the bucket-README density-ceiling prerequisite, and the
"phonetic substitution BEFORE token-bias guard" ordering** — is the ship vehicle
and is already the shared spine (Consensus 5, 6, 9, 11). **Borrow FEA wholesale
as the production layer.** Its self-named sacrifices are mostly correct calls
(S2 T9 mastering, off-generator accel/ritard, lean densities). Its ONE
over-reach is the *blanket* sequential-polyphony default (Clash 5) — correct as
a build instinct, wrong as a universal rule; scope it per-track as in §1.5.

**Least buildable as written: ACC** — not because its musical instincts are
wrong (they're often the most listenable) but because three of its signature
moves each carry a hidden build cost: the **pretty/consonant T3** forces a
mastering exception that breaks the one-pass-per-cluster economy (Clash 3); the
**T13 warm ghost** adds an owned stem + a hard T1→T13 Persona continuity
dependency it self-flags (its §5.7); and its **reworded axiom** is a wall breach
(Clash 1) that buys a sub-threshold singability gain. **Borrow from ACC: its
voice-distinction-by-(timbre+register+syntax-tic) table (§2 L239–252) is a
build asset** — it is exactly how you make voices legible *without* prompted
simultaneity, and it should be lifted directly into DESIGN.md §5 as the Persona
+ metatag spec. Also borrow ACC's **anchor-phrase repetition discipline** (the
returning child-refrain, ghost-line, counting-coda) — repetition is free in
Suno and is the cheapest legibility win available (lyric-writer's job, no build
cost).

**FID** is the source-truth backstop, build-neutral on most clashes. Its
production stance (§4) is functionally identical to FEA's owned-spine
architecture — the two converge on the build layer, which is why the reconciled
album is feasible. Borrow FID's **exact per-track verbatim/value anchors and the
§A name-quarantine appendix** as the content spec; they impose no build cost
(spelled-out numbers + the guard line handle them) except where they crowd a
dense gen (only T9 — handled by Clash 4's strip-to-texture).

---

## 3 · Consensus confirm / contest (feasibility lens)

All 12 confirmed buildable. Detail where feasibility adds a build note:

1. **T9 masters S2** — **CONFIRM, strongly.** S2 (not S3) is the correct *build*
   call independent of fidelity: it preserves limiter headroom so T10 can be the
   genuine loudness peak. Mastering T9 at S3 would force a fight-the-limiter
   plateau across the loud back-half (`mastering-presets.yaml` S3 = loudest/most
   compressed, true_peak ceiling −1.0). One-line note for release-director:
   **T9 loudness tier (S2) ≠ T9 visual palette (T3-energy)** — track separately.
2. **T9 tight/airless/mid-volume (LOCKED)** — CONFIRM. Builds as flat-116 gen +
   post accel; the contained dynamic is a mastering/arrangement fact, reliable.
3. **T10 hybrid round→stack (LOCKED), B3 mirror-echo panned/timed distinct** —
   CONFIRM. This is the album's labor peak (1 HOST bed gen + 4 short solo echo
   gens + 12-stem extract each + comp). Build note: the mirror-echo is
   **HOST-Persona-doubled, phase-offset, panned hard L vs proto-host center** —
   that pairing is buildable in the comp and is the *only* way "one consciousness
   fracturing" survives (you cannot prompt it). Reserve the most mix-engineer
   time here.
4. **Back-half contour build→peak→void** — CONFIRM. Pure mastering/arrangement,
   reliable.
5. **KOH spine = one owned C-drone, automated, Layer-B anchor verbatim on all 13
   boxes, locked C minor, all detune in the owned stem** — CONFIRM, this is THE
   load-bearing feasibility decision. Off-key gens fixed by Suno Studio Pitch
   Transpose, not a re-roll burn. Without this the album is unbuildable; with it,
   it ships.
6. **2 Personas, HOST reused T1→T13, per-section Persona on T6/T11/T12 (A6)** —
   CONFIRM. Build HOST Persona FIRST (before T1) since T13's payoff and 8 tracks
   depend on it. When a Persona carries register, DROP those words from the box
   (no double-spec) — confirmed correct per V5 behavior.
7. **"Klick" untranslated, bare-syllable** — CONFIRM. Builds as a percussive
   consonant-event; keep it OUT of `[...]` brackets in the lyric body (it's
   content, not a tag) and ensure it is not parenthesized (Suno *sings*
   parenthesized words, `suno-preferences` L119).
8. **Axiom as repeated melodic hook 3×/rising** — CONFIRM the hook-ness is
   buildable (repetition is reliable). Wording = Clash 1 (use "prevents").
9. **No brackets in lyric bodies; logs as plain text; numbers spelled; "Sing
   exactly as written" atop every box** — CONFIRM, and this is non-negotiable for
   THIS album: the phonetic spellings (K-O-H), the cold/dry diction, and the
   bias-list collisions (echo/noise/shadow/mirror/whisper) all depend on the
   guard line. **Contest nothing — but ADD:** verify the witness/annotating
   parenthetical layer (FID/FEA T4, T6) is delivered as a low backing *gen layer*,
   NOT as literal `( )` in the lyric body, or Suno will sing the parentheses.
10. **0.67→T8 only; 0.41→T7; paradox ladder 0.84→0.99** — CONFIRM. All spelled,
    all in uncrowded gens (T8/T7), buildable. (T9's 0.84/0.99 → strip-to-texture
    per Clash 4.)
11. **Post shot-list owned/never-prompted** — CONFIRM, this IS feasibility's
    thesis. Every item (boot, ritard→reboot T6, KOH cliff T9, datamosh T9/T10,
    shatter T12, collapse crush T11, sterile arp T13) is a DAW/FX gesture. Build
    note: the **T12 shatter glitch-cut** is the single most important post moment
    — budget edit time; the em-dash gaps in the shatter lyric (FID T12) are
    rendered by the *cut*, not by asking Suno to sing silence.
12. **T1 heavy-voice seed → T10 payoff (A9)** — CONFIRM. Builds as one faint bass
    line in the T1 mix (audible-but-buried) and a full deep-bass gen layer in the
    T10 comp. The callback is a mix/arrangement relationship, reliable.

---

## 4 · Feasibility clashes the adversarial may have under-weighted

1. **Witness / annotating-voice parenthetical layer (T4, T6) — latent
   build/name hazard.** FID and FEA both stage the witness as a "parenthetical
   backing line." If that ever reaches the lyric body as literal `( ... )`, **V5
   sings the parentheses aloud** (`suno-preferences` L119). It must be a separate
   low backing *generation layer* or an inline `[Spoken]`-tagged sotto-voce line,
   never `( )` punctuation. Not in the clash set; flag it for the production
   plan.
2. **HOST Persona is a single point of failure for two payoffs at once.** Both
   the T13 "same timbre now hollow" payoff AND the T10 mirror-echo (HOST-doubled)
   depend on ONE Persona being stable across the whole build. If the HOST Persona
   is re-trained or drifts mid-project, BOTH break. The adversarial flags the
   T1→T13 continuity (via ACC) but not that T10's mirror-echo *also* rides it.
   **Build it once, lock it, never regenerate it.** This is a bigger dependency
   than any single clash.
3. **T2 small-voice / T6 warm-voice register collisions with the HOST Persona in
   one gen.** Where the proto-host (HOST Persona, mid-baritone) and a contrasting
   register (small-voice head-voice T2; warm soprano T6) share a single
   generation, V5 may bleed the Persona timbre onto the contrasting line. Build
   note: these are better as **register-alternating sections within one gen**
   (the contrasting voice gets its own section with its own metatag, HOST drops
   out) rather than overlapped — same per-track-polyphony logic as Clash 5.
   Cheap to do right, ugly if overlapped.
4. **Bucket-README density ceiling is a true prerequisite, not a nicety
   (FEA A8).** Without
   `artists/the-agency-system/albums/dystopian-future-synth/README.md` carrying
   word ceilings + per-track Target Duration, the lyric-writer density gate
   silently no-ops and the dense industrial tracks (T5/T9/T10/T12) will get
   over-written lyrics that V5 then mangles. The adversarial lists it under
   FEA's lyric policy but does not elevate it as a gating prerequisite. **It
   gates the whole chain — create it before lyric-writer runs.**
5. **Modal shift on T3 (Cm→modal) vs the global C-minor lock.** FEA's T3 box says
   `Cm→modal`. Any prompted key/mode change is a Suno reliability risk and
   collides with the "lock C minor in every box, all detune in the owned stem"
   consensus. Build note: keep T3's box in Cm and carry the modal colour in the
   owned pad/drone, OR accept a Pitch-Transpose fix pass. Minor, but it's an
   inconsistency between FEA §2 (T3 modal) and Consensus 5 (global C-minor lock)
   that the adversarial didn't catch.

---

*(km = `SOURCE/kapitel-0.md`; sm = `SOURCE/section-meta.md`; refs grounded in
`overrides/suno-preferences.md` and `overrides/mastering-presets.yaml`.)*
