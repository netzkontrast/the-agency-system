<!--
Imported from https://github.com/netzkontrast/agency/blob/867453e/skills/suno-lyric-writer/pronunciation-guide.md
Source commit: 867453e
Edit upstream and re-import, or edit here and document the divergence.
-->

# Pronunciation Guide for Suno

Suno AI guesses pronunciation. Wrong guess = wrong song = wasted generation. **One wrong word ruins the take.**

---

## Category 1: Homographs (CRITICAL)

Same spelling, different pronunciation. **ALWAYS ask the user — NEVER guess.**

"Context is clear" is NEVER an acceptable resolution. Suno cannot infer from context.

| Word | Meaning A | Phonetic A | Meaning B | Phonetic B |
|------|-----------|------------|-----------|------------|
| live | alive/exist (verb) | lyve | performance (adj) | liv |
| read | present tense | reed | past tense | red |
| lead | to guide | leed | metal | led |
| wind | air movement | wind | to coil/turn | wynd |
| close | nearby | close | to shut | cloze |
| tear | from crying | teer | to rip | tare |
| bass | low sound/music | bayss | the fish | bass |
| wound | injury | woond | past of wind | wownd |
| bow | ribbon | boh | to bend | bow |
| minute | time unit | min-it | tiny | my-noot |
| desert | sand/arid land | dez-ert | to abandon | dih-zert |
| object | thing | ob-ject | to protest | ob-JECT |
| present | gift/current | prez-ent | to give/show | prih-ZENT |
| record | disc/album | rek-ord | to capture | rih-KORD |
| refuse | garbage | ref-yoos | to decline | rih-FYOOZ |

### Homograph Workflow

1. **Identify**: Flag any word with multiple pronunciations
2. **ASK**: Ask user which pronunciation — do NOT assume
3. **Fix**: Replace with phonetic spelling in Suno lyrics only
4. **Document**: Add to Pronunciation Notes table

---

## Category 2: Tech Terms

| Term | Wrong | Right | Phonetic |
|------|-------|-------|----------|
| Linux | "LINE-ucks" | "LIN-ucks" | Lin-ucks |
| SQL | "squeal" | "S-Q-L" or "sequel" | S-Q-L |
| API | varies | "A-P-I" | A-P-I |
| CLI | varies | "C-L-I" | C-L-I |
| AI | varies | "A-I" or "ay-eye" | A-I |
| GUI | usually correct | "gooey" | gooey |
| SSH | varies | "S-S-H" | S-S-H |
| DNS | varies | "D-N-S" | D-N-S |
| VPN | varies | "V-P-N" | V-P-N |
| GPU | varies | "G-P-U" | G-P-U |
| CPU | varies | "C-P-U" | C-P-U |
| USB | varies | "U-S-B" | U-S-B |
| macOS | varies | "mack-oh-ess" | mack-oh-ess |
| iOS | varies | "eye-oh-ess" | eye-oh-ess |

---

## Category 3: Names & Proper Nouns

Non-English names always need phonetic spelling.

| Name | Common Error | Phonetic |
|------|--------------|----------|
| Jose | "joe-SAY" | Ho-zay |
| Maria | "muh-REE-uh" | Mah-ree-ah |
| Ramos | "RAM-ohs" | Rah-mohs |
| Sinaloa | "sin-uh-LOW-uh" | Sin-ah-lo-ah |
| Nguyen | "NEW-win" | Win or Nwin |
| Zhang | "ZANG" | Jahng |
| Mikhail | "mih-KYLE" | Mee-kah-eel |
| Bjork | varies | Bee-york |
| Kiev | varies | Kee-ev or Kye-ev |
| Qatar | varies | Kuh-tar |

---

## Category 4: Acronyms & Initialisms

| Acronym | Say As | Phonetic |
|---------|--------|----------|
| FBI | Individual letters | F-B-I |
| CIA | Individual letters | C-I-A |
| NSA | Individual letters | N-S-A |
| GPS | Individual letters | G-P-S |
| CEO | Individual letters | C-E-O |
| PhD | Individual letters | P-H-D |
| HTML | Individual letters | H-T-M-L |
| NASA | Word | Nah-sah |
| SCUBA | Word | Scoo-bah |
| RICO | Word | Ree-koh |

**Rule**: 3 letters → spell out with hyphens, unless commonly said as a word (NASA, SCUBA).

---

## Category 5: Numbers

| Written | Suno Might Say | Better |
|---------|---------------|--------|
| 1993 | "one nine nine three" | "nineteen ninety-three" or "'93" |
| 2024 | "two zero two four" | "twenty twenty-four" |
| 63 | "six three" | "sixty-three" |
| 404 | "four zero four" | "four-oh-four" |
| 9/11 | "nine slash eleven" | "nine-eleven" |

---

## Category 6: Commonly Mispronounced

| Word | Fix |
|------|-----|
| data | User preference: day-tuh or dah-tuh |
| either | User preference: ee-ther or eye-ther |
| neither | User preference: nee-ther or nye-ther |
| route | User preference: root or rowt |
| legal | lee-gul (not "leh-GAL") |
| illegal | ill-ee-gul (not "ILL-ih-gul") |

---

## Auto-Fix Rules

### Always Auto-Fix (no confirmation needed)
- Tech terms (SQL → S-Q-L, Linux → Lin-ucks)
- Common acronyms (FBI → F-B-I, GPS → G-P-S)
- Numbers (1993 → '93 or nineteen ninety-three)

### Always Ask User First
- Homographs (live, read, lead, wind, tear, bass, bow, close, wound)
- Names (confirm pronunciation preference)
- Regional variants (data, either, route)

---

## Scanning Checklist

When scanning lyrics:
1. Check every word against homograph table above
2. Flag any ALL-CAPS sequences (potential acronyms)
3. Flag any 2+ digit numbers
4. Flag any capitalized proper nouns not in common English
5. Flag any tech/domain terms
6. Cross-reference pronunciation notes table — every entry must be applied in Suno lyrics

---

## No Invented Contractions

Suno only handles standard English contractions.

**Standard (OK):** they'd, he'd, you'd, she'd, we'd, I'd, wouldn't, couldn't, shouldn't

**Invented (WILL BREAK):** signal'd, TV'd, network'd, podcast'd, channel'd

**Rule:** If the base word isn't a pronoun or standard auxiliary verb, don't contract it.

---

## Pronunciation Table Enforcement

Every entry in a track's Pronunciation Notes table MUST appear as phonetic spelling in the Suno lyrics. The table is not documentation — it is a checklist of required substitutions.

**Verification:**
- ❌ "Potrero" in pronunciation table but "Potrero" in lyrics = FAIL
- ✅ "poh-TREH-roh" in lyrics matches table = PASS

**Common failures:**
- Word added to table but never applied to lyrics
- Phonetic applied in one verse but missed in chorus repeat
- New edit introduces a word already in the table but not phonetic
