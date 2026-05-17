<!-- Vendored from agency repo: skills/dramatica-vocabulary/references/dramatica-fundamentals.md @ 867453e49065e16b9298b960a22fd34746985572 -->

# Dramatica Fundamentals — Extended Content

> **⚠ EXTENSION NOTE — Read first.**
>
> This file fills gaps left by the source-PDF extraction (Dramatica Dictionary © Screenplay Systems Inc. 2001) and the resulting per-term reference files. Concepts here that are absent from the term files (`Universe` and `Mind` as Class entries; substantive `Resolve`, `Steadfast`, `Change-as-Resolve-value`, `Linear`, `Holistic` definitions) are reconstructed from:
>
> 1. Cross-references inside the existing Dictionary entries (e.g., "Steadfast" appears in dozens of Element/Variation definitions but has no entry of its own)
> 2. Public Dramatica documentation (storymind.com, dramaticapedia.com, narrativefirst.com)
> 3. Claude's training knowledge of Dramatica theory
>
> Where this file says something the original Dictionary doesn't, that's why. Treat as best-effort reconstruction; verify against authoritative sources (official Dramatica software, *Dramatica: A New Theory of Story* by Phillips & Huntley) for canonical phrasing when stakes are high.

---

## The Four Classes — Complete Set
<!-- nav-ontology (auto-managed; see maintenance/schemas/narrative-ontology/) -->
```yaml
id: class.universe
kind: class
canonical_label: Universe
provenance: extension-derived
aliases_de:
- Universum
aliases_en:
- Situation
scenarios:
- novel.dual-storyform
- novel.act-pivot
- lyric.album-arc-mapping
```


The original term files list only `Physics` and `Psychology` as Class entries, plus `Overall (Objective) Story Domain` (which is a Throughline-perspective wrapper, not a Class proper). **Universe and Mind are missing as Class entries** despite being two of the four Classes. Filled in here.

### Class structure — the 2×2 logic

The four Classes are organized along two axes:

|              | **State** (fixed)            | **Process** (dynamic)         |
|--------------|------------------------------|-------------------------------|
| **External** | **Universe** — situations    | **Physics** — activities      |
| **Internal** | **Mind** — fixed attitudes   | **Psychology** — manipulation |

Diagonals are the **dynamic pairs**: Universe ↔ Mind, Physics ↔ Psychology.

### Universe (Class)

The realm of external situations and circumstances — a fixed external state. A Throughline anchored in Universe asks: *What is the situation, and how does it constrain?* The conflict is anchored in a state of affairs that cannot easily be changed by the characters' actions alone — a place, a status, an arrangement, a configuration.

**Examples**: being trapped in a well, being a slave, being in a war zone, being widowed, being missing a leg, being the king. The problem is *the situation itself*.

**Diametrically opposed Class**: Mind (internal state).

**The four Types under Universe**: Past, Present, Future, Progress.
- Past = Knowledge aspect (what was)
- Present = Thought aspect (what is)
- Progress = Ability aspect (what's changing)
- Future = Desire aspect (what's becoming)

### Mind (Class)

The realm of internal fixed attitudes, biases, and prejudices — a fixed internal state. A Throughline anchored in Mind asks: *What is being held onto internally that resists change?* The conflict is anchored in a fixed mental orientation — a habituated belief, a deep prejudice, an unrelenting emotional fixation.

**Examples**: stubborn pride, deep grief that won't release, an obsession, a phobia, a belief that one is unworthy. The problem is *what the character is fixed on internally*.

**Diametrically opposed Class**: Universe (external state).

**The four Types under Mind**: Memory, Preconscious, Conscious, Subconscious.
- Memory = Knowledge aspect
- Preconscious = Ability aspect (instinctive response)
- Conscious = Thought aspect
- Subconscious = Desire aspect (basic drives)

### Class-Diametricality: the rule for Throughlines

The Main Character and Impact Character **must occupy diametrically opposed Classes**. This is enforced by the Dramatica engine. The two diagonal pairs are:

- Universe ↔ Mind (state-pair: external state ↔ internal state)
- Physics ↔ Psychology (process-pair: external process ↔ internal process)

The Overall Story and Relationship Story Throughlines fill the remaining two Classes (the other diagonal). So a complete Throughline distribution is always one full set of all four Classes.

**Example — Star Wars (1977)** ([Phillips/Huntley analysis][nf]):
- OS = Physics (the rebellion as activity)
- MC (Luke) = Universe (his fixed situation as farm-boy outsider, then orphan)
- IC (Obi-Wan) = Mind (a fixed attitude — the Jedi way of seeing)
- RS = Psychology (the mentorship as manipulation/teaching)

[nf]: https://narrativefirst.com/

---

## Resolve — Substantive Definition
<!-- nav-ontology (auto-managed; see maintenance/schemas/narrative-ontology/) -->
```yaml
id: character-dynamic.resolve
kind: character-dynamic
canonical_label: Resolve
provenance: extension-derived
aliases_de:
- Entschlossenheit
- Wandel-Entscheidung
scenarios:
- novel.character-arc
- novel.crucial-element-audit
- novel.dual-storyform
- novel.diagnose-flat-draft
```


The original term file `## Resolve` is empty (only the header remains). Filled in here.

**Resolve** is one of the four Main Character dynamics. It asks the climax question: *At the moment the MC must commit, do they hold to their original approach (`Steadfast`) or abandon it for the alternative (`Change`)?*

Resolve combined with Outcome (Success/Failure) and Judgment (Good/Bad) determines the moral position the story argues. Crucially, Resolve and Outcome are independent:

| Resolve | Outcome | Judgment | Story type |
|---------|---------|----------|------------|
| Steadfast | Success | Good | "you were right to hold on" — Triumph by perseverance |
| Steadfast | Failure | Bad | "your stubbornness destroyed you" — Tragedy of pride |
| Steadfast | Failure | Good | "you held your principles but lost the fight" — Noble defeat |
| Steadfast | Success | Bad | "you got what you wanted but it cost you yourself" — Pyrrhic |
| Change | Success | Good | "you grew, and that growth let you win" — Transformation triumph |
| Change | Failure | Bad | "you abandoned what worked" — Lost-self tragedy |
| Change | Failure | Good | "you grew, but the world wasn't ready" — Personal triumph in defeat |
| Change | Success | Bad | "you got what you wanted but had to become someone else" — Faustian |

### Steadfast (Resolve value)

The Main Character holds to their fundamental approach, motivation, or worldview despite sustained pressure to change. The Impact Character represents the alternative the MC is *almost* convinced by, but ultimately rejects. Steadfast stories argue: *this approach was correct under these conditions*.

In a Steadfast MC, growth is typically **Stop** (the MC must stop something — a doubt, a temptation, a wavering) — though Stop and Change are not strictly bound.

Cinematic examples: Atticus Finch (*To Kill a Mockingbird*), Sam in the Lord of the Rings ending sequence, Will Kane (*High Noon*).

### Change (Resolve value)

The Main Character abandons their original approach for the alternative offered by the Impact Character. Built-up pressure across the story finally tips them. Change stories argue: *this transformation was necessary*.

In a Change MC, growth is typically **Start** (the MC must start something new) — though again, not strictly bound.

Cinematic examples: Rick (*Casablanca*), Michael Corleone (*The Godfather*), Scrooge (*A Christmas Carol*).

---

## Mental Sex / Problem-Solving Style — `Linear` and `Holistic`

The terms `Linear` and `Holistic` do not appear as standalone entries despite being the operative values of the **Mental Sex** Character Dynamic. Filled in here.

> **Terminology note.** "Mental Sex" is Dramatica's original term; many practitioners now prefer "Mindset" or "Problem-Solving Style" because the original term confused readers (it was never about gender identity, but about cognitive strategy). The underlying concept — Linear vs. Holistic — is unchanged.

### Linear (Mental Sex value)

A problem-solving style emphasizing **cause-and-effect chains**, sequential logic, and discrete-step elimination. The Linear thinker decomposes a problem into pieces and addresses them in order, isolating variables. Strength: efficiency at well-defined problems. Weakness: blind spots when the problem is fundamentally relational.

Encoding cues: characters who say "first we'll do X, then Y", who diagnose before acting, who follow procedures, who win by systematic elimination.

### Holistic (Mental Sex value)

A problem-solving style emphasizing **balance between forces**, simultaneous adjustment of multiple interacting factors, and shifting the *field* rather than picking off individual problems. The Holistic thinker reads the whole configuration and adjusts pressure across it. Strength: pattern-recognition in messy, interrelated systems. Weakness: poor at bottlenecks that need a single targeted action.

Encoding cues: characters who restore balance rather than win, who notice what's been left out, who solve a stated problem by addressing an apparently unrelated one, who say "everything is connected."

### How Mental Sex interacts with the storyform

Mental Sex is independent of biological sex/gender. It's a setting on the Storymind — the way the integrated story-mind processes its central problem. A Linear MC plus a Holistic IC creates a particular friction (and vice versa) that the story works through. In the Storyform, the choice constrains certain Element-pair arrangements via the engine.

---

## Quick reference — the four MC Character Dynamics

For convenience, all four MC dynamics in one place. Three of them are documented in the Dictionary; Resolve was missing (above).

| Dynamic        | Values                  | What it asks |
|----------------|-------------------------|--------------|
| Resolve        | Steadfast / Change      | Does the MC hold their approach or abandon it? |
| Growth         | Stop / Start            | Does the MC need to stop something or start something? |
| Approach       | Do-er / Be-er           | Does the MC act-then-feel or feel-then-act? |
| Mental Sex     | Linear / Holistic       | Does the MC solve via sequential logic or relational balance? |

The four together (plus Story Limit, Driver, Outcome, Judgment, and Plot's Required Element) make the MC unique within the storyform.
