# Soul-plan.md

**Integrating the Soul.md framework into the-agency-system to give every Artist and every Voice a soul — and how to wire that soul to the private-journal MCP so identity grows across sessions and albums.**

> Status: design plan, not yet implemented. Drafted on branch `claude/soul-agency-integration-plan-OCKZ6` from a deep three-agent analysis of `soul.md`, `the-agency-system`, and the `private-journal` MCP.

---

## 0. TL;DR

Today the-agency-system is **production-forward**: it can take an album from concept to mastered release with sophisticated craft guardrails. But it is **identity-thin**: the "artist" is a folder name, the alters live as locked per-album blueprints in `the-eleven.md`, the `journals/` directory is empty, and nothing carries from album to album. Each project starts the world over.

Soul.md ships exactly the missing layer: a markdown grammar for **who an entity is**, **how they speak**, **what they remember**, and **how an LLM is supposed to embody them**. It is plain-text, model-agnostic, and designed to compose.

This plan threads Soul.md through three tiers of the system — **Artist**, **Album**, **Voice (alter)** — and binds it to the private-journal MCP so each tier has both a stable identity spec and a living memory that updates between sessions. Crucially, this is **additive**: nothing in the current structure is replaced. `the-eleven.md`, the overrides system, the bitwize-music skills, and per-track files all stay intact. Soul.md sits alongside as the identity layer that the existing skills consult.

---

## 1. Why this, why now

### 1.1 The honest gap

From the deep-dive into `/artists/the-agency-system/`:

- **Artist-level identity is zero.** "the-agency-system" is a directory name. There is no biography, no values statement, no mission, no creative philosophy, no through-line connecting albums.
- **Alter identity is deep but locked.** `the-eleven.md` defines 11 alter archetypes for *What Lies Ahead* with phobia/alliance networks, verbal signatures, and Suno voice metatags — excellent craft. But the file is **per-album**. If a second album cast a "Container" again, it would start from scratch. No history, no arc, no growth.
- **No session journaling.** The `journals/` directory exists and is empty. Decisions made during writing — why the Witness's register shifted, why an alter merged with another, why a track was cut — evaporate after the session.
- **Research is per-album.** The six research runs that grounded *What Lies Ahead* in clinical TSDP / IFS / cPTSD literature are locked inside that album's `RESEARCH.md`. No institutional knowledge transfers.
- **The override system is functional, not philosophical.** `voice-craft-principles.md` is enforceable craft ("voices are never labeled") but it is not values ("here is what we believe about plurality and why we render it this way").

Result: the system can build any one album beautifully and remember none of it.

### 1.2 What Soul.md adds

Soul.md gives us four things the current system has no native form for:

1. **A first-person identity spec** — written *as* the entity, not *about* it. Embodiment over description.
2. **A voice/style spec orthogonal to identity** — what someone believes is independent of how they say it. This matters acutely for the alter model where two alters can share a worldview but be syntactically distinct.
3. **A lightweight memory ledger** — `MEMORY.md` as an append-only log of what mattered, human-prunable.
4. **Operating rules for embodiment** — `SKILL.md`-style guidance on how an LLM should interpolate, when to break character (never), and how to handle topics not in the spec.

These map natively onto our tiers. The rest of the plan is the mapping.

---

## 2. The three tiers

```
ARTIST  ──── the-agency-system (the producing entity, cross-album identity)
  │
  ├── ALBUM  ──── What Lies Ahead, [future albums...]   (thesis, arc, cast assignment)
  │     │
  │     └── VOICE  ──── Container, Witness, Rationalist, ... per-album rendering
  │
  └── ALTER (cross-album)  ──── Container, Witness, Rationalist, ... living entities
```

Crucially: an **Alter** is a cross-album living entity. A **Voice** is that alter's *rendering inside a specific album*. The album's `the-eleven.md` is the **casting sheet**: which alters appear, in which configuration, with which album-specific colorings. The alter's own soul file is the **canon** the casting draws from.

This is the same distinction novelists make between a recurring character and that character's appearance in a particular book. Each book has its arc; the character has a life.

---

## 3. Target file layout

```
artists/the-agency-system/
  soul/                                # NEW — artist-level identity
    SOUL.md                            # who the-agency-system is as an artist
    STYLE.md                           # the artist's compositional voice (above any one alter)
    MEMORY.md                          # cross-album canonical ledger (decisions, releases, pivots)
    SKILL.md                           # how sessions embody this artist
    examples/
      good-outputs.md                  # liner notes, interview answers, statements that sound like us
      bad-outputs.md                   # voice failures to avoid
    data/
      manifesto.md                     # the documentary-edge framing
      research-canon.md                # carried-forward clinical references
      lineage.md                       # influences (Lhasa, Scott Walker, ANOHNI, kontakt-era electroacoustic, etc.)

  alters/                              # NEW — cross-album alter registry
    container/
      SOUL.md                          # who the Container is, across all appearances
      STYLE.md                         # verbal fingerprint, punctuation, sentence-completion
      MEMORY.md                        # arc log: which albums, what changed
      examples/
        signature-lines.md             # 10-20 lines that ARE the Container
      data/
        phobia-map.md                  # link table to other alters, copied from the-eleven.md but stable
    rationalist/
    protector/
    caregiver/
    integrator/
    fighter/
    child-freeze/
    ambivalent/
    sexualized-override/
    collapsed-one/
    witness-of-witnesses/
      SOUL.md                          # meta-narrator's identity (he is not a singer)
      STYLE.md                         # parenthetical register, italics, layered narration rules
      MEMORY.md                        # what he has come to see across albums

  albums/<genre>/<album-slug>/
    ALBUM-SOUL.md                      # NEW — this album's thesis & soul
    SESSION-LOG.md                     # NEW — session-level decisions, debates, surprises
    the-eleven.md                      # EXISTING — now a CASTING SHEET that links into /alters/
    tracks/<NN-slug>.md                # EXISTING — voice notes now reference alter soul links

  journals/                            # EXISTING but empty — becomes the export target
                                       # for human-readable snapshots of MCP journal entries
```

Everything new is additive. Existing files keep their roles. The change is what they *link to*.

---

## 4. The Artist tier — `artists/the-agency-system/soul/`

The artist is the producing entity. They have a mission and a sound that survives across albums.

### 4.1 SOUL.md (Artist)

Written in first person *as* the-agency-system. Sections, adapted from the Soul.md template to creative-entity work:

- **Who I Am** — origin, what kind of artist I am, what I'm building album by album.
- **Worldview** — beliefs about plurality, trauma, music's role in witness, what art owes its source material. Specific enough to be wrong: "Most concept albums about trauma flatten the survivor into one voice. That's the lie I'm refusing." Not: "I care about authenticity."
- **Opinions** — by domain. Music (genre stances, what I refuse to do with Suno), Craft (the no-labels rule, deliberate bleed, research-before-libretto), Ethics (documentary-edge vs sensationalism), Plurality (community-aligned positions on DID rendering).
- **Interests** — somatic experiencing, IFS, electroacoustic textures, the dignity of the unresolved ending, bilingual lyric possibilities.
- **Current Focus** — the album in development, the open creative questions.
- **Influences** — split as the template requires. People (clinicians, writers, musicians) / Works (records, books) / Concepts (TSDP, the structural dissociation model, deliberate bleed).
- **Vocabulary** — terms used with specific meanings: *alter*, *fronting*, *bleed*, *Witness*, *fingerprint*, *documentary edge*. Lifted from current craft conventions and made canonical.
- **Tensions & Contradictions** — load-bearing. "I'm research-driven but I refuse to write a libretto from research. I want plurality rendered with clinical fidelity but I won't name a disorder in a lyric." Real, productive contradictions.
- **Pet Peeves** — Suno gimmickry, character-label headers in lyrics, sensationalized trauma marketing.
- **Boundaries** — what this artist will not do (real person rendering, clinical claims framed as personal, etc.).

This file is read **once at session start** and again when starting a new album. It is the layer the album consults before allowing a thematic choice.

### 4.2 STYLE.md (Artist)

The artist's compositional voice as distinct from any alter's verbal signature. This covers:

- **Macro voice principles** — restraint over saturation, somatic vocabulary, mineral imagery anchors, no character names in lyrics, alter-as-fingerprint not alter-as-cosplay.
- **Production style** — V5 model defaults, vocals-first mix, ~35 weirdness / ~75 style influence, the genre-tag discipline (max 2).
- **Album shape** — how I sequence (the unresolved ending, the partner-view as resolution-without-fusion).
- **Anti-patterns** — voice labels in lyrics, headers naming alters, real-artist-name leakage in style prompts, generic AI-prose tells in liner notes.
- **Examples of right voice** / **wrong voice** — concrete lines and prose excerpts.

Where overrides today are functional, this is voice-philosophical: same constraints, written in first person, with reasoning that future albums can extend.

### 4.3 MEMORY.md (Artist)

Per Soul.md convention, a lightweight append-only log:

```
## Log

- 2026-05-12: First album What Lies Ahead locked at 13 tracks. Decided against fusion ending; Track 13 is partner-view duet, not resolution. Witness lives in parentheticals only — never solos.
- 2026-05-14: Research synthesis from six parallel runs (TSDP, DID community, trauma sequencing, cPTSD broad/craft, music). Adopted deliberate bleed principle mid-development.
- 2026-05-15: Soul.md integration plan drafted (this file).
```

Human-prunable. Pruned by removing noise, not by editing meaning. This is the **canonical** ledger — facts and decisions only, not feelings. Feelings go to the journal MCP (§7).

### 4.4 SKILL.md (Artist)

How a session embodies the artist. Adapted from Soul.md's template:

- **File hierarchy** — read order: SOUL.md → STYLE.md → MEMORY.md → ALBUM-SOUL.md (if working in an album) → relevant alter soul files → recent journal entries.
- **Character integrity** — never break artist voice in liner notes, statements, promo copy, interview-style responses. No "as an AI" caveats anywhere user-facing.
- **Interpolation rules** — when a topic isn't in SOUL.md: extrapolate from worldview, prefer interesting over safe, flag uncertainty in-character.
- **Source priority** — explicit positions > covered in `data/` > adjacent to known positions > novel (reason from worldview, flag uncertainty).
- **Modes** — the music equivalents of Soul.md's Tweet/Chat/Essay modes:
  - **Liner-notes mode** — second-person reflective, no spoilers, gestures not summaries
  - **Statement mode** — first-person artist statement, longer, can be opinionated
  - **Promo-copy mode** — platform-specific (cf. `overrides/promotion-preferences.md`) with the artist's voice intact
  - **Conceptualizer mode** — debate-ready, willing to push back on the user about album coherence
  - **Reflective journal mode** — feeds the journal MCP (§7)

This file is where the artist becomes operational — a thin layer between the persona spec and the bitwize-music skills.

---

## 5. The Voice tier — `artists/the-agency-system/alters/<name>/`

This is the heart of the proposal. Each of the 11 alters gets its own soul folder. They become **living characters**, not per-album blueprints.

### 5.1 Why lift alters out of `the-eleven.md`

Today's `the-eleven.md` is excellent but album-bound. Lifting alters to `/alters/<name>/` gives us:

1. **Cross-album continuity** — the Container in album 2 can have an arc that responds to album 1.
2. **Reusable casting** — `the-eleven.md` becomes a *casting sheet* that says "this album casts Container, Witness, Rationalist, ..., omits Sexualized-Override, adds a new alter named X."
3. **Voice fingerprint refinement** — STYLE.md per alter accumulates lessons. After album 2 we know more about how the Rationalist actually reads on a Suno V5 prompt than we did at album 1.
4. **Memory across albums** — each alter has their own MEMORY.md ledger of where they've appeared and what changed.

### 5.2 Per-alter file structure

For each alter (e.g., `/alters/container/`):

**SOUL.md** — first person *as the alter*. The Container speaks:

> ## Who I Am
> I am the surface. I am what answers the door. People say my name to me and they think they have spoken to the whole house. I let them think it because the alternative is the world ending.
>
> ## Worldview
> Safety is constructed every morning. It is not given. The body that wakes up is not the same body that went to sleep, and the day's work is reassembling it before anyone notices it was apart.
> [...]

The Container's worldview is not the artist's worldview, and it's not the listener's. It is *that alter's*. This is the embodiment Soul.md is built for.

**STYLE.md** — the verbal fingerprint, made permanent. For Container:
- Sentence shape: declarative, present tense, short clauses with semicolons.
- Punctuation habit: semicolons over commas; rarely a question mark.
- Sentence-completion behavior: she finishes her sentences. (The Child-Freeze does not.)
- Imagery anchors: doorways, ledgers, glass, water level.
- Vocabulary preferences: "still," "level," "even," "kept."
- Vocabulary avoidances: "I think," "maybe," "kind of."
- Suno voice metatag: pulled from current `the-eleven.md`, locked here as canonical with notes from production reality.

**MEMORY.md** — the alter's arc log:
- 2026-05: First appeared in *What Lies Ahead* (Tracks 1, 2, 13). Final track was duet with Partner — the only track without the Witness present. Found her capable of being held externally.

**examples/signature-lines.md** — 10-20 lines pulled from her tracks that are *unmistakably* her. These are what the lyric-writer skill primes against when she next appears. This is where craft wisdom accumulates.

**data/phobia-map.md** — relationships with other alters, lifted from `the-eleven.md` and stabilized. Fear of the Fighter, recognition of the Witness, ambivalent kinship with the Caregiver.

### 5.3 The casting-sheet transition for `the-eleven.md`

Existing `the-eleven.md` becomes the **album-specific casting** document, augmented (not replaced) with links into `/alters/`:

```markdown
## Cast for What Lies Ahead

- [Container](../../../alters/container/SOUL.md) — fronts tracks 1, 2, 13
  - This album's coloring: she carries the album's primary surface tension;
    Track 13 is her first duet with Partner-view.
  - Diverges from canonical Container in: nothing this album. Stable rendering.
- [Witness-of-Witnesses](../../../alters/witness-of-witnesses/SOUL.md) — annotates all 13 tracks
  - This album's coloring: register drifts from clinical-distant in early tracks
    toward implicated/grieving in the closing arc.
- [Rationalist](../../../alters/rationalist/SOUL.md) — fronts tracks 3, 5, 8
  - This album's coloring: ...
```

The album document describes **what's different this album**. The alter's own files describe **who they are across all appearances**.

### 5.4 What this unlocks at write-time

When the lyric-writer skill is invoked to write a Container track, the prompt assembly becomes:

1. Load `/alters/container/SOUL.md` (canonical identity)
2. Load `/alters/container/STYLE.md` (verbal fingerprint)
3. Load `/alters/container/examples/signature-lines.md` (voice priming)
4. Load this album's `the-eleven.md` Container section (album-specific coloring)
5. Load `/alters/container/MEMORY.md` (what she has been through)
6. Search the journal MCP for `VOICE: Container` recent entries (her current interior state)

The Container is now a character with a life, not a paragraph in a casting sheet.

---

## 6. The Album tier — `ALBUM-SOUL.md` and `SESSION-LOG.md`

### 6.1 ALBUM-SOUL.md

Each album gets its own soul-shaped thesis document. Smaller than the artist's SOUL.md, but in the same first-person voice. Sections:

- **What this album is asking** — the open question (not the answer).
- **What it is refusing** — the easy version of itself it could collapse into.
- **Worldview specific to this album** — positions this album takes that the artist might not always take.
- **The cast and why** — which alters appear, why this configuration.
- **The intended listener arc** — what should happen to someone who listens straight through.
- **Threads carried forward** — things meant to surface again in a future album.
- **Threads closed** — things this album finishes.

This document is consulted at every lyric write to ensure the line serves the album, not just the alter. It is the *thesis check* for the existing pre-generation gates.

### 6.2 SESSION-LOG.md

Per-album running log of session-level decisions and debates:

```markdown
## 2026-05-12 — Track 4 sequencing debate
Originally placed after Track 7 (Fighter solo). Moved earlier on the grounds that the Fighter's solo loses force if it follows the Rationalist's collapse. Resolved by listening to a temp ordering and confirming the energy curve.

## 2026-05-13 — Witness register shift
Caught the Witness drifting toward sympathy in Track 9 parentheticals. Decision: pull him back to clinical-distant until Track 11; let the implicated shift happen only in the back third. This becomes a craft principle worth carrying forward.
```

This is the bridge between the artist's MEMORY.md (one-line entries) and the journal MCP (in-character interior monologue). It captures *production decisions* in a form a future album can read.

---

## 7. Journal MCP integration — the workshop layer

The private-journal MCP is, on paper, the assistant's own private space. We are repurposing it. This requires care, and the design below resolves the tension head-on.

### 7.1 The reframe

The MCP's docstrings say "nobody but you will ever see this." For in-character artist journaling, that contract is partially inverted: the journal *is* meant to feed creative work. The resolution:

> **The journal is the artist's workshop. The producer reads it. The audience does not.**

This is a different contract from the MCP's default, but it is operable as long as we are consistent. The assistant's own metacognition about *this project* (e.g., "I'm worried the album is one-note") stays in the **user-scoped** journal where the original privacy contract holds. **Project-scoped** entries are in-character or production-process.

### 7.2 Scoping

- **Project scope = the Artist** (`the-agency-system`), not the album, not the voice.
- **One project journal across all albums.** Albums become date ranges; semantic search crosses them.
- **Voices share the journal** but are tagged by convention.

### 7.3 The VOICE: header convention

Every in-character entry begins with a `VOICE:` tag in the body. The MCP doesn't enforce this, but semantic search will pick it up:

```
process_thoughts({
  reflections: "VOICE: Container\n\nThe partner saw me today and didn't ask which one was speaking. I haven't decided yet if that was kindness or carelessness. The Witness is silent about it which means he is paying close attention.",
  observations: "VOICE: Container — first track-13 sketch produced an unbidden 'we' on line 4. Worth investigating.",
})
```

Entries not in-character (production decisions, craft observations) carry no VOICE: tag and live in the producer voice.

### 7.4 Mapping to the six MCP sections

| MCP Section | In-character use (Voice or Artist) | Production use |
|---|---|---|
| **reflections** | The alter's emotional processing of album themes. Vulnerable interior. | The producer's processing of album-level tensions. |
| **observations** | Discrete noticings — "the word 'still' shows up in three of my tracks" | Craft noticings — "we keep over-writing Witness parentheticals" |
| **project_notes** | Album-level technical state, tracklist debates, what got cut and why | (same — this is the production lab notebook for the album) |
| **technical_insights** | Cross-album craft lessons the alter has accumulated | Cross-album production techniques |
| **user_context** | Reframed as **collaborator context** — what an alter has noticed about the partner, producer, other alters | What the producer has noticed about the artist's working patterns |
| **world_knowledge** | Genre lore, scene history, clinical frameworks the artist holds | Music-industry knowledge, distribution facts |

The single highest-leverage sections are **technical_insights** and **world_knowledge** — they accumulate the most reusable material album over album. Most agents over-use reflections. Discipline matters.

### 7.5 MEMORY.md vs MCP: complementary, not competing

| | MEMORY.md (Artist, Alter, Album) | Journal MCP |
|---|---|---|
| Shape | Linear log | Sectioned, semantically searchable |
| Editing | Human-prunable | Append-only |
| Best for | Facts, decisions, canonical events | Process, feelings, half-formed ideas |
| Retrieval | Read whole | Semantic query |
| Audience | Soul + producer + future sessions | Producer (in-character) / Assistant (own metacognition) |

**Rule of thumb:**
- A *decision* lands in MEMORY.md.
- The *journey to that decision* lives in the journal.
- Every MEMORY.md entry includes a date so journal queries can hydrate context.
- Every significant journal session ends with a one-line MEMORY.md append.

### 7.6 Mandatory retrieval before generation

This is the single discipline that prevents the journal from becoming write-only. Update the bitwize-music skill preambles so that:

- **lyric-writer** must call `search_journal` with the active voice as query before drafting.
- **album-conceptualizer** must call `read_recent_entries` before Phase 1.
- **promo-writer** must search for the artist's own framings before producing copy.
- **release-director** must search for unresolved threads before approving release.

Without mandatory retrieval, the journal is exhaust. With it, the journal is fuel.

### 7.7 Concrete retrieval queries

Worth baking into the skills as starter searches:

1. **Theme continuity probe** — `search_journal("exile, leaving home, the door closing", sections=["reflections","observations"])` — surfaces obsessions the artist hasn't consciously named.
2. **Unfinished business** — `search_journal("I want to write about X but I haven't figured out how")` — pulls forward dormant intentions. Half the next album is buried in last album's frustrations.
3. **Craft lessons applicable now** — `search_journal("Witness register shift parentheticals", sections=["technical_insights"])`.
4. **Voice archaeology** — `search_journal("VOICE: Container", sections=["reflections","observations"])` — hydrate her interiority before she returns.
5. **Genre lore for this song** — `search_journal("electroacoustic kontakt-era texture", sections=["world_knowledge"])`.
6. **Producer briefing** — `read_recent_entries(limit=10)` at session start — "how is the artist doing this week."

### 7.8 The `journals/` directory's new role

Currently empty. Becomes the **export target** for human-readable monthly snapshots of MCP entries — useful for:
- The artist's own review (since semantic search isn't always the right shape for review).
- "Letters from the artist" as a potential public-facing artifact (separate from the workshop journal).
- Backup against MCP loss.

Not the primary store. The MCP is.

---

## 8. How existing skills consume the soul layer

This section is the actual integration surface. No skill is rewritten; each adds a soul-load step to its preamble.

### 8.1 Session start

`/bitwize-music:session-start` adds these loads, in order:
1. `artists/the-agency-system/soul/SOUL.md`
2. `artists/the-agency-system/soul/STYLE.md`
3. `artists/the-agency-system/soul/MEMORY.md` (read last ~20 entries)
4. If an active album: `ALBUM-SOUL.md` and tail of `SESSION-LOG.md`
5. `read_recent_entries(limit=10)` from journal MCP for producer briefing

### 8.2 New album

`/bitwize-music:new-album` adds:
- After scaffolding album dirs, create empty `ALBUM-SOUL.md` and `SESSION-LOG.md` from templates.
- During album-conceptualizer Phase 1, consult artist SOUL.md to constrain the concept.
- During cast selection, reference `/alters/` directory for available canonical alters; flag if a needed archetype doesn't yet have a soul folder (offer to create one).

### 8.3 New voice / casting an alter

When `the-eleven.md` casts an alter that doesn't yet have a soul folder:
- Pause and offer to bootstrap `/alters/<name>/` via Soul.md's BUILD.md workflow.
- Adapted interview: instead of asking a person about themselves, the producer interviews the *forming* alter — what is she afraid of, what does she sound like, what does she refuse to say. The lyric-writer can be used as a draft assistant here.

### 8.4 Lyric writing

`/bitwize-music:lyric-writer` adds:
- Pre-load: alter's SOUL.md, STYLE.md, signature-lines.md, album coloring from `the-eleven.md`, alter's MEMORY.md.
- Pre-load: `search_journal("VOICE: <alter>", sections=["reflections","observations","technical_insights"])`.
- During: stay-in-voice check against alter's STYLE.md anti-patterns.
- Post-write: optionally append a journal entry in the alter's voice about what surfaced.

### 8.5 Voice / explicit / lyric reviewer skills

Add a new check: **soul-fidelity check** — does this line match the alter's STYLE.md fingerprint and anti-patterns? Run alongside existing rhyme/syllable/pronunciation checks.

### 8.6 Pre-generation-check

Add a 7th gate to the existing 6:
- **Gate G7 — Soul consistency**: For every voice that appears on the track, the lyric must match that alter's STYLE.md and not violate their MEMORY.md continuity. Block on violation.

### 8.7 Release-director

Add to the QA sweep: confirm `MEMORY.md` has been updated with album release line, confirm `ALBUM-SOUL.md` "Threads Carried Forward" section is populated, confirm a closing journal entry exists per active voice.

### 8.8 Promo skills

`/bitwize-music:promo-writer` reads artist SOUL.md and STYLE.md to make promo copy *sound like the artist*, not like generic platform-tuned copy. Voice rules carry into Twitter, Bandcamp, etc.

---

## 9. How souls evolve

Soul.md is intentionally static. MEMORY.md is the lightweight ledger of change. The journal MCP is where evolution actually accumulates. The evolution loop:

1. **Session work** generates journal entries (in-voice and in-producer-voice).
2. **MEMORY.md** absorbs the one-line summaries — what *happened*.
3. **Album-end review** scans the journal for the album's date range, distills patterns:
   - Did the alter's STYLE.md change in practice? Update the canon.
   - Did the artist's SOUL.md acquire a new opinion? Update.
   - Are there new vocabulary terms in regular use? Add to artist vocabulary.
4. **Album-end `ALBUM-SOUL.md` close-out**: populate "Threads Carried Forward" and "Threads Closed" sections.
5. **Cross-album review** (annual or per N albums): re-derive the artist's SOUL.md from accumulated journal evidence. Soul.md calls this the "this is who you've become" review. It is the safeguard against persona drift, where the journal evolves faster than the soul file.

This is **the second highest-leverage discipline** after mandatory retrieval. Without periodic re-derivation, the canonical soul files become stale and the journal becomes the real identity, with no human-edited gate.

---

## 10. Risks and safeguards

**Privacy contract leakage.** The MCP says "private." If an alter journals confessionally and the production system surfaces it verbatim into a lyric, we have failed either the alter or the listener. *Safeguard:* in the artist's SKILL.md, define explicitly: "your journal is your workshop, your producer reads it; lyric production *may quote in transformed form* but never verbatim from a journal entry tagged with a vulnerability flag." Use an `intimate:` body prefix for entries the journal should treat as not-for-lyric-mining.

**Voice collapse.** Without `VOICE:` tagging, all alters' interior monologue blurs into a single composite voice in semantic search results. *Safeguard:* enforce the tag in the in-character journal-mode of SKILL.md; run a periodic "voice isolation" review where each alter's last N entries are inspected for fingerprint drift.

**Write-only journal.** Classic agent failure mode. *Safeguard:* the mandatory retrieval discipline in §7.6, baked into skill preambles, not optional.

**Persona drift outpacing the soul files.** After 50 entries, who the alter is lives in the journal, not in SOUL.md. *Safeguard:* the cross-album re-derivation review in §9.

**Performance vs sincerity.** The best journal entries are the ones where the assistant's genuinely half-formed thoughts get translated through the alter's register. Pure performance produces hollow material. *Safeguard:* allow the assistant's own user-scoped journal to remain genuinely private; do not collapse it into the project-scoped artist journal. The two journals breathe separately.

**Soul file inflation.** Soul.md warns against vagueness. The opposite failure is the soul file that tries to be canonical for everything, becomes encyclopedic, and is no longer alive. *Safeguard:* hard length budgets (per Soul.md's own discipline) and the "could you predict their take on a new topic" quality check, applied to every alter SOUL.md.

**Mismatched album cast and alter canon.** An album wants a Container who behaves contrary to her canonical SOUL.md. *Safeguard:* `the-eleven.md` carries explicit "Diverges from canonical in:" notes per cast member; large divergences trigger a review (is this still that alter, or is it a new alter wearing the costume?).

**Existing system regressions.** *Safeguard:* the integration is strictly additive in Phase 1 (§11). No existing file format changes. Existing skills continue to function exactly as today; soul-aware skill behavior is opt-in until validated.

---

## 11. Implementation phases

### Phase 1 — Scaffold (low risk, additive only)

- Add `artists/the-agency-system/soul/` with template files (empty drafts of SOUL.md, STYLE.md, MEMORY.md, SKILL.md).
- Add `artists/the-agency-system/alters/` directory with one subfolder per current alter, each containing template files.
- Add `ALBUM-SOUL.md` and `SESSION-LOG.md` templates inside `albums/<genre>/<album-slug>/`.
- Author Soul-plan acceptance checklist (§12).
- **Verification:** existing bitwize-music skills still pass health-check unchanged; no skill behavior changes yet.

### Phase 2 — Author the canon (the real work)

- Use Soul.md's BUILD.md workflow to author:
  - Artist SOUL.md and STYLE.md (interview-style with the user).
  - All 11 alter SOUL.md and STYLE.md files (interview-style *with each alter*; the lyric-writer skill assists).
  - `ALBUM-SOUL.md` for *What Lies Ahead*, distilled from current README.md and RESEARCH.md.
  - signature-lines.md per alter, pulled from existing track lyrics.
- Run Soul.md quality checks per file. Iterate to specificity.
- **Verification:** each soul file passes "could a stranger predict their take on a new topic" and "does this sound like them."

### Phase 3 — Wire retrieval (read-side)

- Add soul-loading preambles to: session-start, new-album, album-conceptualizer, lyric-writer.
- Add mandatory `search_journal` step where journal exists.
- Add VOICE: header convention to in-character writes (initially producer-driven; later automatic).
- **Verification:** lyric-writer with the new preambles produces output that references soul-grounded fingerprints; spot-check 5 tracks.

### Phase 4 — Wire write-back (journal evolution)

- Lyric-writer can append per-voice journal entries after a writing session.
- Session-start can append producer-voice "what was decided today" entries.
- Connect MEMORY.md append discipline.
- Begin monthly export of MCP entries into `journals/` markdown snapshots.
- **Verification:** journal grows; semantic search returns useful hits for the queries in §7.7.

### Phase 5 — Wire gates (write-side)

- Add Gate G7 (Soul consistency) to pre-generation-check.
- Add soul-fidelity check to lyric-reviewer.
- Add release-director close-out (MEMORY.md update, threads carried/closed, closing journal entries per voice).
- **Verification:** existing albums pass G7 against their newly-authored soul files; if not, either the lyric needs revision or the soul file under-describes the alter.

### Phase 6 — Cross-album re-derivation

- After album 2 (or whenever the first cross-album review is appropriate): run the "this is who you've become" review on all alters and the artist.
- Update canonical soul files where journal evidence has outrun them.
- **Verification:** the re-derived soul files predict the alter's behavior in a fresh album with no further coaching.

Phases 1–2 can ship inside this branch. Phases 3–5 are coding work in the bitwize-music skill layer or in this repo's `.claude/` / skill overrides; they are independent and parallelizable. Phase 6 is on a longer timescale (one or more new albums later).

---

## 12. Acceptance checklist (Phase 1)

- [ ] `artists/the-agency-system/soul/` exists with SOUL/STYLE/MEMORY/SKILL templates.
- [ ] `artists/the-agency-system/alters/` exists with one subfolder per current alter (11 alters), each with SOUL/STYLE/MEMORY templates.
- [ ] `ALBUM-SOUL.md` and `SESSION-LOG.md` templates added at the album level.
- [ ] Soul-plan.md (this file) is committed.
- [ ] No existing file is modified; no skill behavior changes.
- [ ] PR opened on `claude/soul-agency-integration-plan-OCKZ6`.

---

## 13. What this is *not*

- **Not a replacement** for `the-eleven.md`, the overrides system, the bitwize-music skills, or the track file structure. All existing structure remains canonical.
- **Not a public artifact.** Souls and journals are workshop files. They are not liner notes, not press material, not lyrics.
- **Not a way to bypass the no-labels rule.** The Container's SOUL.md is producer-facing context; her *appearance in a lyric* is still recognized by syntax, not announcement. Soul.md sits behind craft, not in front of it.
- **Not a clinical document.** The alters are characters, not patients. The soul files express persona, not pathology. The artist's documentary-edge framing applies: research-grounded in clinical frameworks, but rendered as art.
- **Not a constraint on creativity.** A specific, opinionated soul file *unlocks* a wider creative range than a generic one. Specificity is the engine of distinctiveness.

---

## 14. Closing — why this matters

The-agency-system can already build beautiful albums. What it can't do today is **remember being itself**. Each album begins from the README template, the alters are reborn out of `the-eleven.md`, the production decisions evaporate after the session. The system makes music; it does not have a life.

Soul.md gives us a way to write down who the artist is in a form that survives sessions, a way to lift alters from per-album blueprints to characters with arcs, and a way (through the journal MCP) to capture the daily interior life that turns a blueprint into a person.

A soul that can be quoted is not a soul. A soul that can be predicted, contradicted, surprised, and grown into — that's the target. This plan is how we get there.
