<!-- Vendored from agency repo: skills/dramatica-vocabulary/references/storyform-mechanics.md @ 867453e49065e16b9298b960a22fd34746985572 -->

# Storyform Mechanics — Extended Content

> **⚠ EXTENSION NOTE.** This file documents the *rules* by which a Dramatica storyform is built — rules that govern which choices are compatible with which others. The original term files describe the *parts* but not how they fit together. This is reconstructed from public Dramatica documentation (storymind.com, dramaticapedia.com, narrativefirst.com) and Claude's training knowledge. The full Story Engine is patented (US Patent #5,734,916) and proprietary; what's here is the publicly documented top-level mechanics.

---

## The Four Throughlines and their Class Distribution

Every complete story has four Throughlines — four perspectives on a single problem. Each Throughline lives in **exactly one Class**, and the four Throughlines together cover **all four Classes**.

| Throughline | Whose perspective? | What it explores |
|-------------|--------------------|------------------|
| **Overall Story (OS)** | All characters / "the general's hill" | The shared problem affecting everyone |
| **Main Character (MC)** | One character — the audience's identification point | The personal problem from inside |
| **Impact Character (IC)** | The character who challenges the MC's worldview | The alternative perspective |
| **Relationship Story (RS)** | The MC↔IC relationship as an entity | The growing/changing connection between them |

### The Diametricality Rule

The Main Character and Impact Character must occupy **diametrically opposed Classes**. The two diagonal pairs are:

- **State diagonal**: Universe ↔ Mind (external state ↔ internal state)
- **Process diagonal**: Physics ↔ Psychology (external process ↔ internal process)

Once MC and IC Classes are chosen on one diagonal, OS and RS fill the other diagonal. So one of these four distribution patterns applies to every storyform:

| Pattern | OS | MC | IC | RS |
|---------|----|----|----|----|
| 1 | Physics | Universe | Mind | Psychology |
| 2 | Psychology | Universe | Mind | Physics |
| 3 | Universe | Physics | Psychology | Mind |
| 4 | Mind | Physics | Psychology | Universe |
| (and the four mirror cases swapping MC↔IC) | | | | |

In total there are 8 valid Throughline-to-Class assignments. The rest of the storyform engine narrows this further based on subsequent choices.

### Why the diametricality matters

The MC and IC are designed to argue *opposing approaches* to the same underlying problem. If they were in the same Class, they'd be arguing within the same paradigm — boring. By placing them in diametrical Classes, Dramatica forces the story to examine the problem from genuinely incompatible angles. The MC's "Steadfast or Change" decision at the climax is the question of which paradigm wins.

---

## The Type Sequences — Acts as a Class's Type-Tour

Each Class contains four Types. A Throughline's Acts traverse those four Types in a sequence determined by the Storyform engine.

### The four Types per Class

| Class | Types (the four Acts visit each, in some order) |
|-------|-------------------------------------------------|
| Universe | Past, Present, Progress, Future |
| Physics | Learning, Understanding, Doing, Obtaining |
| Psychology | Conceiving, Conceptualizing, Being, Becoming |
| Mind | Memory, Preconscious, Conscious, Subconscious |

**Mapping to the KTAD fractal** (Knowledge / Thought / Ability / Desire — the universal quad pattern):

| Class       | Knowledge      | Thought         | Ability         | Desire         |
|-------------|----------------|-----------------|-----------------|----------------|
| Universe    | Past           | Present         | Progress        | Future         |
| Physics     | Learning       | Understanding   | Doing           | Obtaining      |
| Psychology  | Conceiving     | Conceptualizing | Being           | Becoming       |
| Mind        | Memory         | Conscious       | Preconscious    | Subconscious   |

### The Act sequence

In a 4-act story, the protagonist's Throughline visits all four Types of its Class. The opening signpost is the first Type; the climax sits between the third and fourth. The exact ordering — which Type opens, which closes — is set by the storyform's other choices (especially Driver, Limit, and Outcome).

Three classic sequences for the Overall Story (Physics) Throughline:

- **Quest pattern**: Learning → Doing → Understanding → Obtaining (gather info → act → consolidate → achieve)
- **Investigation pattern**: Doing → Learning → Understanding → Obtaining (act → discover → integrate → achieve)
- **Linear quest**: Learning → Understanding → Doing → Obtaining (study → comprehend → execute → achieve)

The Acts of each *other* Throughline sequence through the *other* three Classes' Types — but each Throughline only ever traverses *its own* Class's Types.

---

## How a Storyform is Built — The Cascade

The Dramatica engine takes a small number of choices and propagates them across the entire storyform. The publicly described top-level cascade:

### Step 1: Throughline Class assignment (8 valid combinations)

Choose which Class each Throughline lives in, respecting the diametricality rule. This single choice already constrains many later decisions.

### Step 2: Concern (Type) per Throughline

Within each Throughline's Class, choose the **Concern** — which of the four Types is the focal point of that Throughline's exploration. The Concern is *not* the entire Throughline; it's the central area.

### Step 3: Issue (Variation) per Throughline

Within the Concern's Type, choose the **Issue** — which Variation is the focal sub-area. Theme lives at the Issue level.

### Step 4: Problem (Element) per Throughline

Within the Issue's Variation, choose the **Problem** — which Element is the source-of-conflict. Each Throughline has its own Problem Element.

### Step 5: MC Dynamics

The four MC Character Dynamics:
- Resolve: Steadfast / Change
- Growth: Stop / Start
- Approach: Do-er / Be-er
- Mental Sex: Linear / Holistic

Each choice constrains the engine further.

### Step 6: Plot Dynamics

The four Plot Dynamics:
- Driver: Action / Decision (do actions provoke decisions or vice versa?)
- Limit: Optionlock / Timelock (does the story end when options run out, or when time runs out?)
- Outcome: Success / Failure (does the OS Goal get achieved?)
- Judgment: Good / Bad (is the MC at peace at the end?)

### What the engine then derives automatically

From these ~12 choices, the engine derives:
- The full Type sequence (Acts) for each Throughline
- The Solution Element (the Element opposite to the Problem Element)
- The Symptom and Response Elements
- The Focus Element
- All Variation and Element placements across all four Throughlines
- Character Element distributions (which character gets which Element pair as their motivation)

This cascade is why two stories with the same Goal but different Resolve choices end up structurally very different — the engine reshuffles the entire storyform downstream.

---

## The Eight Archetypal Characters — Element Pair Assignments

The eight Archetypes are Element-pair carriers. Each Archetype carries two Element pairs (a motivation pair and a methodology pair), and the eight Archetypes together exhaust the 16 character Elements.

| Archetype | Motivation Pair (the "drive") | What they push toward |
|-----------|--------------------------------|------------------------|
| Protagonist | Pursuit + Consideration | Achieving the Goal |
| Antagonist | Avoid + Reconsider | Preventing the Goal |
| Reason | Logic + Knowledge | Rational evaluation |
| Emotion | Feeling + Ability | Emotional expression |
| Sidekick | Faith + Support | Helping the Protagonist |
| Skeptic | Disbelief + Oppose | Doubting / Hindering |
| Guardian | Conscience + Help | Moral guidance |
| Contagonist | Temptation + Hinder | Moral temptation / obstruction |

Real complex characters often combine Elements from multiple Archetypes. The eight are the *atomic* arrangement; complex characters are mixtures.

---

## Encoding consistency — quick checks

When working on a storyform, these checks catch the most common contradictions:

1. **MC and IC in diametrical Classes?** If both feel "external" or both feel "internal", something is wrong.
2. **Goal (OS Concern) is a Type — does it match the OS Class?** A Goal of "Obtaining" implies OS in Physics. A Goal of "Becoming" implies OS in Psychology.
3. **Resolve and Growth alignment.** Steadfast often pairs with Stop (the MC must stop wavering), Change with Start (the MC must start being different) — *but exceptions exist by design*. If your story uses Steadfast+Start or Change+Stop, that's a deliberate complex choice, not an error.
4. **Driver — Action or Decision — is consistent across the story's major beats.** If your turning points are all decisions but you've labelled it Action-driven, the storyform is mis-set.
5. **Limit type matches the climax shape.** Optionlock stories climax when alternatives exhaust; Timelock stories climax when a deadline is reached. Check which feels right for *your* climax.
