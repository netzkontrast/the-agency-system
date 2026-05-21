# The Eleven — Cross-Project Cast Reference

**Purpose.** The single working reference for the cast of **the Agency
System** — the one DID-system cast shared by every layer of the project:
the **music**, the **novel**, and the **visual design language**. The cast
is the same across all three; what changes is only how each layer addresses
it. This file is **album-agnostic**: it describes the cast generically, the
same way every album and the novel draw from it. It is *not* a tracklist and
*not* an album document. (The most-developed expression of this cast to date
is the *Chapter Zero* album; its SOURCE corpus is mined here for refined DNA,
then generalized.)

**name_exposure (hard rule).** This is cross-project DNA used by the music
and design layers — so **function/archetype form ONLY, never a personal
name.** Personal names live solely in the novel layer, in
`skills/theagencysystem/references/resolver.yaml`, in album SOURCE/`DESIGN.md §7`
files, and nowhere else. A name leaking into a lyric, Suno metatag, promo
field, or art prompt is a CRITICAL defect. This extends
`overrides/voice-craft-principles.md`.

**One cast, three layers, function-keyed.** Design + Music reference the
cast by **function/role**; the Novel references the same parts by **name**.
The bidirectional name↔function bridge is `resolver.yaml`. The loader is the
gate skill `skills/theagencysystem/` — invoke it before the bitwize chain or
a novel phase so only the snippets the active `(function × state × layer)`
needs are pulled.

**What this document gives you.** (a) who each function is, (b) how each
speaks, (c) how they ally, (d) how they avoid each other, (e) imagery
anchors for writing — plus a Suno voice-metatag table for vocal
differentiation. Use the Core Matrix at a glance; the Suno table for style
prompts; the Individual Profiles for voice work; the alliance/avoidance maps
for dialogue and blend tracks; the Lyrical Hooks last, as imagery anchors.

---

## The cast at a glance

**Core 11** (all three layers). Classes: **ANP** = apparently-normal parts ·
**EP** = emotional parts · **Meta** = meta-cognitive parts. The integrator
carries the **ISH** (Internal Self Helper) role.

- **ANP:** the Container (Host) · the Rationalist
- **EP:** the Protector · the Caregiver · the Fighter · the Child-Freeze ·
  the Ambivalent · the Sexualized-Override · the Collapsed One
- **Meta:** the Integrator (ISH) · the Witness-of-Witnesses

A short secondary section at the end covers the **mirror voices**, **system
voices**, and **narrative modes** that surround the core 11 (function-form).

---

## State axis (S0–S4)

The cast lives on a `function × state` matrix. The state axis is the second
dimension every layer shares. Lead functions per state:

| State | Name | Lead function(s) |
|---|---|---|
| S0 | Homöostase | host, rationalist |
| S1 | Latenz / Freeze | child_freeze, collapsed |
| S2 | Alert / Konflikt | fighter, protector |
| S3 | Kollaps-Peak | collapsed (peak) |
| S4 | Repair / Integration | integrator, we-voice |

Full detail: `skills/theagencysystem/references/state-axis.md`.

---

## Core Matrix — Quick Reference

| Function / Archetype | Class | Core phobia / conflict | Arc trajectory | Production-world tendency |
|---|---|---|---|---|
| **The Container** (Host) | ANP | Internal chaos overtaking the maintained surface | Surface → fractality, then held by the system | Mixed — the container of all registers; dry, present |
| **The Rationalist** | ANP | Irrationality, emotional overflow, undecidability | Logic → intuition | Cold orchestral electronic, thin reverb |
| **The Protector** | EP | Helplessness, system-breach | Reactive defense → constructive protection | Band-driven dark electro-rock; clipped, forward |
| **The Caregiver** | EP | Disconnection; abandoning the weak (warmth → smothering) | Warmth → genuine holding (no longer controlling) | Warm orchestral electronic; intimate, lullaby-adjacent |
| **The Integrator** (ISH) | Meta | Premature collapse; mistiming her own emergence | Curatorial waiting → bridge / mediator | Spacious electroacoustic, plate reverb (architecture) |
| **The Fighter** | EP | Re-victimization, surrender | Reactive rage → protective rage as a tool | Band-driven dark electro-rock; growl, breathless |
| **The Child-Freeze** | EP | Abandonment, criticism, being seen | Freeze → trust | Piano-and-voice intimate; head-voice, lo-fi |
| **The Ambivalent** | EP | Betrayal of approached intimacy | Superposition → choosing | Piano-intimate, microtonal, unresolved tonic |
| **The Sexualized-Override** | EP | Authentic vulnerability; loss of preemption | Control → vulnerability as power | Low-register controlled electronic; cabaret styling |
| **The Collapsed One** | EP | Hope (because hope is more to lose) | Catatonia → what he carries begins to be held | Sub-tempo drone / near-spoken; deepest in the body |
| **The Witness-of-Witnesses** | Meta | Dysfunction unobserved; analysis paralysis | Cold critique → constructive critique | Annotative / spoken-word layer, slightly off-beat |

---

## Suno Voice Metatags (function-form, no names)

Style-prompt language for steering Suno toward distinct timbres per function.
Without explicit voice metatags Suno trends toward similar vocals, which kills
the per-function DNA. **Always include these tokens in the style prompt.**
Gender assignments are **craft choices for vocal differentiation**, not
identity claims. Use the descriptive form `[male mid-baritone, weary, dry
close-mic]` — never the archetype label as a tag.

**Design goal:** maximum spread across range, age, gender, texture, and
processing — so each function is unmistakably distinct before the lyric even
carries the difference. No two functions share more than one vocal axis.

| Function | Suno Voice Metatag |
|---|---|
| **Container (Host)** | male vocals, mid-baritone, weary, slightly under-articulated, present-tense delivery, dry close-mic, no reverb, light tape compression, adult ~40s, conversational range |
| **Rationalist** | male vocals, clear tenor, sibilant precision, no vibrato, cold articulation, thin processed reverb tail, controlled mid-range, adult ~30s, academic register |
| **Protector** | male vocals, chest-weighted low baritone, clipped three-word lines, forward-mic with slight compression, dry room, adult ~35–45, restrained intensity, no vibrato |
| **Caregiver** | female vocals, warm soprano, breathy at the edges, vowel-forward legato, intimate close-mic, soft room reverb, adult ~30s, lullaby-adjacent phrasing |
| **Integrator (ISH)** | female vocals, mezzo-alto, ageless quality, spacious long vowels, controlled vibrato, plate reverb suggesting architectural space, slow legato cadence |
| **Fighter** | female vocals, belt-alto with growl, raw breathless intensity, clipped lines, dry mid-distance mic with slight distortion on lows, adult ~30s, no head voice, no breath inside imperatives |
| **Child-Freeze** | young child vocals, gender-androgynous, head-voice only, whispered consonants, audible breath between phrases, fragile, very close-mic with permitted tape hiss / lo-fi texture, ~10–12yr range |
| **Ambivalent** | female vocals, alto with microtonal pitch-bending, sliding vibrato, oscillating dynamics within phrases, breath audible mid-line, mixed dry/wet processing, ambiguous tonic, adult ~late 20s |
| **Sexualized-Override** | female vocals, low contralto (deepest female register), controlled, deliberate, restrained vibrato held as a weapon, mid-distance polished mic, theatrical / cabaret styling, adult ~30s |
| **Collapsed One** | male vocals, very deep bass, sub-tempo near-spoken delivery, gravelly, breath audible between fragments, subkick-close dry mic, adult ~40–50, line-final pauses longer than the lines |
| **Witness-of-Witnesses** | androgynous spoken-word, monotone or half-sung, dry, layered with slight delay/echo, slightly behind the beat, lowercase delivery, audiobook-narrator register, no melodic contour |

**Notes on the spread:**
- **Range:** very-deep-bass / low-baritone / mid-baritone / tenor / soprano /
  mezzo-alto / three alto positions (belt+growl, microtonal, contralto) /
  child / spoken. No two functions share register *and* texture.
- **Gender:** 4 male / 5 female / 1 child-androgynous / 1 spoken-androgynous.
  The Fighter is female (subverts the male-rage default). The Child-Freeze is
  genuinely androgynous (avoids the cuteness trap). The Witness is
  non-musically gendered (he narrates, he doesn't sing).
- **Processing:** each function has a distinct sonic fingerprint at the
  *production* level, not just the vocal level — dry close-mic / cold thin
  reverb / soft room / plate reverb / dry-with-distortion / lo-fi tape hiss /
  mixed dry-wet / mid-distance polished / subkick-close / delay-echo layered.
- **Reference-singer hints** (to ground imagination; use sparingly in actual
  prompts): younger Scott Walker (Container), academic Matt Berninger
  (Rationalist), Mark Lanegan (Protector), intimate ANOHNI (Caregiver),
  mature Björk (Integrator), PJ Harvey *Rid of Me* (Fighter), lo-fi
  child-folk (Child-Freeze), Mitski / Joanna Newsom slides (Ambivalent),
  modernized Marlene Dietrich (Sexualized-Override), late Leonard Cohen
  (Collapsed One), audiobook narrator (Witness).
- **All adjustable.** Re-tag if a function reads strongly different in context.

---

## Individual Profiles

### The Container (Host, ANP)
**Function.** Holds the surface; maintains social camouflage and the illusion
of unity. Suffers time loss, gaps, the small daily lies that cover them. Does
not know what it doesn't know — that ignorance is its function, not its flaw.
**Verbal signature.** "I don't know how I got here." "I must have —" "Someone
in here —". Sentences that trail and don't punctuate. A counting tic as a
somatic anchor (tiles, degrees, seconds of breath).
**Voice / delivery.** Mid-baritone, tired, present-tense, slightly
under-articulated; dry close-mic, no reverb. The voice of someone who keeps
almost-remembering. Do NOT resolve the trailing lines or sound certain.
**Inner posture.** Distantly grateful to the Rationalist for order, uneasy
near the Caregiver (too warm), avoidant of the EPs (cold spot in the room),
unaware of the Witness until very late; quiet bargain with the Integrator
(she keeps the gate, he keeps the surface).

### The Rationalist (ANP)
**Function.** System administrator. Imposes logical order on chaotic inner
and outer reality; reframes emotion as a variable to be solved (even loss as
"structure optimization").
**Verbal signature.** Hypotactic, nested. Conditionals and qualifiers.
"Given that …, it follows —", "Let me restate —". Cool, operational, never
raises, never swears, never weeps.
**Voice / delivery.** Clear tenor, sibilant precision, no vibrato, cold
articulation, thin reverb tail. Micro-cracks at the line-ends — the track
*almost* succeeds at its logic before something gives. A broken sentence from
him is a massive event.
**Inner posture.** Contempt for the Fighter (sees only chaos), invalidating
coldness toward the Child-Freeze (sees inefficiency), tactical alliance with
the Witness (until critique turns on him), structural rivalry with the
Caregiver (logic vs. relation), tolerates the Container as infrastructure,
dismisses the Integrator as concept (her non-dismissal unsettles him).

### The Protector (EP)
**Function.** Proactive crisis manager. Where the Fighter is reactive, the
Protector is *strategic* — plans defenses, anticipates threats, prepares the
body. His vigilance is the silence that follows fragmentation.
**Verbal signature.** Contained imperatives. "Stay behind me." "Not this
one." "I have you." Never explanations. Care comes out as "Head down," never
"I love you."
**Voice / delivery.** Chest-weighted low baritone, clipped three-word lines,
forward-mic, dry room, restrained intensity, no vibrato. Weight on the front
foot, breath held for the listening. Do NOT let lines flow long.
**Inner posture.** Loyal beyond reason to the Child-Freeze and the
Ambivalent. Tense mission-alliance with the Fighter (same goal, incompatible
methods). Low-grade friction with the Container (he exposes; the Protector
covers). Wary of the Caregiver (her warmth opens what he closes).

### The Caregiver (EP)
**Function.** Holds the relational tissue — attachment, caregiving, social
interfacing. Tries, against all evidence, to keep the cut connections from
going necrotic. Confuses her own needs with others'.
**Verbal signature.** Soft openings, questions framed as offers. "Let me —",
"It's okay if —", "If you'd like, we could —". "We" before "I." Diminutives,
gentle negations.
**Voice / delivery.** Warm soprano, breathy at the edges, vowel-forward
legato, intimate close-mic, soft room reverb, lullaby phrasing. Risks reading
as a love song until the love is *for the dying system*. Watch the turn where
"I'll hold you" becomes "you cannot leave"; hardness from her is an alarm.
**Inner posture.** Loves the Child-Freeze and the Ambivalent openly (the
danger: care becoming smothering). Rivalry with the Rationalist (warm vs.
cold), terror near the Fighter, methodological opposition with the Protector
(same goal, opposite temperature), longing toward the Integrator.

### The Integrator (ISH, Meta)
**Function.** Witness *with agency* and the system's gatekeeper. Holds the
blueprint of the time before the dissociation; manages what is accessible to
whom and when. Centrally responsible for what the Host does not remember —
the amnesia is also her protection. Her patience is curatorial: she waits for
the system to be ready *because she controls when ready is*. From love, not
malice — but it has costs. Inside the system (not the outside signal).
**Verbal signature.** Unforced first-person plural. "We could —", "There is
a way." Patient deferrals that are active management: "Not yet." "It's not
time." Long pauses as syntax; almost nothing definitive.
**Voice / delivery.** Mezzo-alto, ageless, spacious long vowels, controlled
vibrato, plate reverb suggesting architecture not weather, slow legato. The
voice that arrives late and reframes — having quietly managed all along.
**Inner posture.** Visible to almost none until the system is ready. The
Rationalist dismisses her; the Fighter mistakes her for surrender; the
Caregiver longs for her; the Collapsed One she alone does not fear; the
Witness alone *sees* her. Never pushes — the EPs misread her buffering as an
identity-threat.

### The Fighter (EP)
**Function.** Kinetic counter-reaction. Where the Child-Freeze went still
under earlier harm, the Fighter burns under later harm. Holds the rage the
system was not permitted to feel at the time. Anger as a tool, not an
identity.
**Verbal signature.** Staccato. Sentence fragments, no connectors,
verb-first / imperative. Standalone negations ("Not."). Profanity if useful.
Periods, not exclamation marks.
**Voice / delivery.** Belt-alto with growl, raw breathless intensity, clipped
lines, dry mid-distance mic with distortion on lows; no head voice, no breath
inside imperatives — breath is a vulnerability. Calm = exhaustion, not
healing. Do NOT pause to breathe.
**Inner posture.** Contempt for the Rationalist (cold = complicit). Protective
fury toward the Child-Freeze that often *terrifies* the Child-Freeze. Method-
conflict with the Protector. Maximum contempt for the Collapsed One (what she
refuses to become). Wary respect for the Witness (the one she can't
intimidate).

### The Child-Freeze (EP)
**Function.** Holds the original terror of neglect — the ice of being unseen.
Voicelessness as protection: if I am quiet enough, perhaps I will not be hurt
again.
**Verbal signature.** Fragments, childlike syntax, repetition, ellipses.
Words that almost arrive and then don't; question-marks at the ends of
statements. "is it —", "i didn't —". Concrete body-sensation: cold, dark,
hurt, where, who, away.
**Voice / delivery.** Young child, gender-androgynous, head-voice only,
whispered consonants, audible breath, very close-mic with permitted tape
hiss, ~10–12yr. The track listeners misread as cute is the cruellest. Do NOT
make it sweet — it is mangled by fear.
**Inner posture.** Seeks shelter near the Caregiver. Trusts the Protector
quietly but cannot say so. Terrified of the Fighter even when she is *for*
him. Cannot be in the room with the Rationalist. Recognizes the Ambivalent
and doesn't know what to do with the recognition.

### The Ambivalent (EP)
**Function.** Holds the unsolvable contradiction *come closer / go away*.
Longs for the bond that, once granted, became the wound. Cannot stay in
either position.
**Verbal signature.** Self-correcting sentences that reach and retract.
"I want — no, I don't — I mean —", "stay — go — come back —". The em-dash is
her natural punctuation; statements revoke themselves mid-speech. Split, not
moody — her sentences must break to be honest.
**Voice / delivery.** Alto with microtonal pitch-bending, sliding vibrato,
dynamics oscillating within phrases, breath mid-line, mixed dry/wet, ambiguous
tonic. Never resolve to the tonic until the very end — and even then,
ambiguously.
**Inner posture.** Cannot trust the Caregiver's offered warmth (the *yes* is
the trap). Cannot trust the Fighter's offered fury. Recognized only by the
Child-Freeze, and the recognition frightens both. Provokes the
Sexualized-Override into preemptive control.

### The Sexualized-Override (EP)
**Function.** Proactive control as survival strategy — never again the passive
position. Reclaims power by *taking* intimacy before it can be taken, even
when this forecloses the intimacy she wants.
**Verbal signature.** Confident, performative. Lines that should land as
seduction but read as warning. "I know what this is." "Don't bother." "I've
already —". Imperatives of intimacy as command, not request; cold wit that
never goes light.
**Voice / delivery.** Low contralto (deepest female register), controlled,
deliberate, restrained vibrato held as a weapon, mid-distance polished mic,
cabaret styling. Performs its surface so well listeners may miss the terror
underneath.
**Inner posture.** Active conflict with the Caregiver — whose offered intimacy
is the exact threat she is built against. Triggers fear in the Child-Freeze
and the Ambivalent. Tolerated by the Fighter (same job, different domain). The
Rationalist understands her structurally and is repelled. Her path runs
through herself: vulnerability as a form of power — not rescued, not softened.

### The Collapsed One (EP)
**Function.** Absolute resignation — the instant the nervous system gave up.
Carries the unbearable so the system does not rupture catastrophically: a
safety valve, not a defeat. Catatonic, not clinically depressive.
**Verbal signature.** Sparse, lowercase, fragments that don't punctuate.
"i can't —" (no period). Circular shame-logic, self-negation, inevitability,
repetition as the rhythm of collapse. Words arrive heavy and stay where they
fell.
**Voice / delivery.** Very deep bass, sub-tempo near-spoken, gravelly, breath
audible between fragments, subkick-close dry mic; line-final pauses longer
than the lines. The track everyone skips because it doesn't move — and the one
that recontextualizes everything. His presence drags every other voice down.
**Inner posture.** Feared and avoided by almost everyone (his collapse
threatens to pull the system down). The Fighter holds him in contempt; the
Caregiver cannot reach him (he has out-traveled care); the Integrator alone
does not fear him — she knows what he carries.

### The Witness-of-Witnesses (Meta)
**Function.** Observes the observers. Critiques every part's strategy. The
only one who registered the deep error in the system's design. Not above the
system — the system noticing itself.
**Verbal signature.** Marginal, annotative — footnotes, parentheticals,
asides, almost always lowercase, almost always correcting. "It is notable
that —", "One notices —", "In the current mode —". No wit; sharpness. Never
affective — if he turns emotional, his function collapses.
**Voice / delivery.** Androgynous spoken-word, monotone or half-sung, dry,
layered with slight delay/echo, slightly behind the beat, audiobook-narrator
register, no melodic contour. The voice that comments on the other voices —
that never sings the chorus, only annotates it.
**Inner posture.** Feared by all because he sees through every defense — none
of his observations are wrong, which is the problem. Cold respect from the
Rationalist (until critique turns on him), hostility from the Fighter (he
names what she won't look at), the secret structural alliance with the
Integrator (he sees her before the system is ready). The only part that loved
the system enough to register that something was wrong from the inside.

---

## Alliances (A + B: alliance, basis named)

- **Protector + Fighter** — uneasy mission-alliance: same goal, incompatible
  methods; will fight each other inside the same battle.
- **Caregiver + Child-Freeze** — refuge; stable, but exactly what the
  Caregiver's smothering risk closes around.
- **Caregiver + Ambivalent** — unstable; she tries, the Ambivalent reaches
  and withdraws, she tries again. The pattern is the wound.
- **Rationalist + Witness** — temporary tactical; shared distrust of
  EP-driven decisions, lasting only until the Witness turns on the Rationalist.
- **Protector + Container** — passive; the Protector covers without the
  Container knowing.
- **Integrator + Witness** — secret, structural; the only alliance not based
  on fear-management. He alone sees her before the system is ready.
- **Collapsed One + Integrator** — silent; she does not fear him, he does not
  consume her energy. They share the room.
- **Sexualized-Override + Fighter** — tactical; both run preemption, different
  domains, same operating principle.
- **Child-Freeze + Ambivalent** — silent recognition; they see each other and
  pretend not to. The quietest, most terrifying pairing.

## Avoidance / phobia network (A → B: A fears/clashes with B; ↔ mutual)

Sourced from `cross-cutting/collision-matrix.md` (33 pairs).

**ANP ↔ EP (cross-class friction)**
- host → fighter (hot fury burns through the surface) · host → child_freeze
  (her silence pulls him into the silence he outruns) · host → collapsed
  (dread of recognizing the floor)
- rationalist → fighter (max activation; she's everything his model can't
  contain) · rationalist → child_freeze (inefficiency / model failure) ·
  rationalist → ambivalent (she breaks his decidability) · rationalist →
  sexualized_override (she turns his categories against him) · rationalist →
  collapsed (proof of structural failure)
- fighter → rationalist (contempt-as-fear; his cold is the wound's logic) ·
  fighter → host (collaborator with the surface that erased her) ·
  child_freeze → rationalist (terror; he invalidates her smaller) ·
  child_freeze → host (the parent who keeps almost-noticing, then doesn't)
- rationalist ↔ caregiver (structural rivalry: logic vs. relation) ·
  host ↔ protector (low-grade: host exposes, protector covers)

**EP ↔ EP**
- protector → other EPs (competence-anxiety / workload, not fear) ·
  caregiver → fighter (violence she cannot soothe) · caregiver →
  sexualized_override (a closed door that looks open) · caregiver → collapsed
  (past the reach of care; the limit of her selfhood)
- ambivalent → caregiver (the offered *yes* is the trap) ·
  sexualized_override → caregiver (built against the caregiver's exact gift)
- caregiver ↔ protector (warmth vs. coldness as protection) · fighter ↔
  child_freeze (protector/protected asymmetry; her shield is his nightmare) ·
  fighter ↔ collapsed (maximum contempt) · sexualized_override ↔ ambivalent
  (override pre-empts the longing and resents it) · child_freeze ↔ ambivalent
  (mutual recognition neither can bear) · collapsed → no one (past the energy
  for fear — which itself frightens the others)

**Meta ↔ system**
- integrator → none (not phobic; she fears the *timing* of her emergence) ·
  rationalist ↔ integrator (he dismisses her as concept; her non-dismissal
  unsettles him) · all ten → witness (low-grade dread; he names what each
  protects against, never wrong)

**Style-break triggers (the loudest collisions to build a duet/blend around)**
- **rationalist ↔ fighter** — the break inside one sentence (hypotactic vs.
  staccato).
- **caregiver ↔ sexualized_override** — collide at the point of authentic
  bonding.
- **witness** — uncomfortable everywhere; disrupts wherever he appears.
- **integrator** — read as an identity-loss threat by the EPs, but never
  pushes.

**Composite voice (blend):** the Caregiver + Protector blend speaks as a
single function-exposed "I" (e.g. the lyric *Lass mich, lass mich atmen*) —
warmth and defense fused, name never exposed.

---

## Lyrical Hooks per Function

Imagery anchors and prosodic suggestions for songwriting. **Lyrics in EN**;
character voice marked by syntax/diction only — never headers, never
name-adlibs, never `[Section]` tags, never a personal name.

- **Container** — *imagery:* the unfinished list, the door he doesn't
  remember opening, hands that smell like a place he wasn't, tiles counted.
  *Prosody:* sentences that trail, final lines that don't punctuate.
  *Hook:* "I must have —" / "Someone in here —" / "The day is the same shape
  but smaller."
- **Rationalist** — *imagery:* the proof on the board, the theorem that does
  not match the room, decimal places past usefulness. *Prosody:* long nested
  lines, deliberate articulation. *Hook:* "If A, then —" / "Let me restate —"
  / a chorus that almost closes the proof, then can't.
- **Protector** — *imagery:* the doorway between rooms, the body as wall,
  weight on the front foot, breath held for the listening. *Prosody:* clipped
  imperatives, three-word lines. *Hook:* "Stay behind me." / "Not this one." /
  "I have you."
- **Caregiver** — *imagery:* warm hands, the bandage changed, the lamp left
  on, the vine that begins as decoration. *Prosody:* vowel-forward, breathy.
  *Hook:* "Let me —" / "It's okay if —" / the chorus that doesn't notice when
  "I'll hold you" becomes "you cannot leave."
- **Integrator** — *imagery:* the garden, the path that doesn't announce
  itself, the door that was always open, "we" used unforced. *Prosody:*
  spacious, reverbed, long vowels. *Hook:* "There is a way." / "We could." /
  "Not yet, but soon."
- **Fighter** — *imagery:* teeth, fists, the threshold she won't let be
  crossed, fire that does not warm. *Prosody:* staccato, breathless,
  growl-adjacent. *Hook:* "Try me." / "Never again." / a refusal that becomes
  the whole chorus.
- **Child-Freeze** — *imagery:* small spaces, the corner with the best
  sightline, the smaller-than-small body, breath you can't hear. *Prosody:*
  head-voice, whispered consonants, fragmentary syntax. *Hook:* "is it —" /
  "i didn't —" / three quiet words repeated.
- **Ambivalent** — *imagery:* the doorway entered and exited, the hand
  reaching and not, a room she can't decide is warm. *Prosody:* microtonal
  slides, self-correcting lines, ambiguous tonic. *Hook:* "come closer —
  no —" / "I want — I don't —" / a chorus that never resolves.
- **Sexualized-Override** — *imagery:* the mirror set up before the door
  opened, the lipstick checked, the room she chose, the script. *Prosody:*
  low controlled, vibrato-restrained, deliberate. *Hook:* "I know what this
  is." / "Don't bother." / a seduction that, on second listen, is a warning to
  herself.
- **Collapsed One** — *imagery:* the floor, the weight of the air, the chair
  that hasn't moved in hours, dust at eye level. *Prosody:* sub-tempo,
  near-spoken, line-final pauses longer than the lines. *Hook:* "i can't —"
  (no period) / silence held longer than expected / one phrase repeated under
  itself.
- **Witness-of-Witnesses** — *imagery:* the margin of the page, the small
  note, the recursion symbol, the hand that doesn't move while everything else
  does. *Prosody:* spoken or half-sung, behind the beat, layered. *Hook:*
  parenthetical lines commenting on the other voices; footnotes-as-lyric; a
  voice that never sings the chorus, only annotates it.

---

## Beyond the Core 11 (secondary — function-form)

These surround the core cast. Most live in the **novel** and **design**
layers; the **we-voice** also surfaces in music at S4.

**Mirror voices** (echoes; novel + design):
- **the mirror-echo** — mirrors the signal. Echo-prose: asserts and retracts
  memory ("it was warm — no, it wasn't — it was different"). Resonance, not a
  subject; a splinter of the outside signal carried inside the host.
- **the sweep-voice** — mirrors the system. Internalized erasure-logic — the
  reason the amnesia works from within. Erasure-prose: self-erasing sentences,
  opening words disappearing, gaps left visible as gaps; degrades mid-line as
  it is itself partitioned.

**System voices** (novel layer):
- **the system / the watch** — preservation-function without resonance;
  third-person, never "I"; all-caps bracketed status/telemetry lines; classify,
  index, suppress, escalate, contain. No metaphor, no morality, no wit.
- **memory** — preservation and re-administration of trauma-memory; flowing
  long arcs, water/current/sediment imagery; her gentle temptation ("erase the
  pain") is the most insidious trap.
- **the sweep / erasure** — the erasure-executive; hard-functional, no
  metaphors, speaks only in execution reports (sweep, quarantine, terminate).
- **the signal / anomaly** — the outside witness, never a subject of a
  sentence, appears only through effect (the dust, the hands, the silence);
  never physically described; solves nothing — it lets the system solve
  itself. Distinct from the Integrator, who is *inside* the system.

**Narrative modes:**
- **the narrator** — mediating voice between world and reader; essayistic,
  philosophical, direct address permitted; witnesses without resolving.
- **the we-voice** — choral polyphony: composition, not fusion. The system
  speaks as a whole without the individual voices disappearing (the
  Rationalist still hypotactic within the We, the Fighter still staccato, the
  Child-Freeze still childlike). Never a final fusion; mosaic, not monolith.
  Leads S4 / Repair-Integration alongside the Integrator.

---

## Where this attaches

- **Name bridge (function ↔ name):**
  `skills/theagencysystem/references/resolver.yaml` — the single source of
  truth for the cast/class/tier and the only place the name↔function map
  lives. Personal names appear there and in the novel layer only.
- **Loader:** the gate skill `skills/theagencysystem/` — invoke it before the
  bitwize chain or a novel phase; it loads only the snippets the active
  `(function × state × layer)` needs. Do not bulk-read the snippet tree.
- **Per-function DNA snippets:** `references/entities/<function>.md`.
- **State axis:** `references/state-axis.md`. **Collision network:**
  `references/cross-cutting/collision-matrix.md`. **(function × state) index:**
  `references/matrix-index.yaml`.
- **bitwize attachment** (which bitwize skill phase loads which ref):
  `references/bitwize-attachment.md`.
