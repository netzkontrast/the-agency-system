---
name: suno-download
description: Downloads preview-quality MP3s from Suno share URLs into the album's audio directory, using the import-audio filename convention. Use when the user has recorded suno_url values on track files and wants the audio fetched directly into the project rather than downloaded manually from the Suno dashboard.
argument-hint: <album-slug> [<NN> | <NN>:<share-url>] ...
model: claude-haiku-4-5-20251001
allowed-tools:
  - Read
  - Bash
  - bitwize-music-mcp
---

## Your Task

**Input**: $ARGUMENTS

Download Suno preview MP3s for one or more tracks of an album and place them
in the album's audio directory under the `import-audio` filename convention.

---

# Suno Download Skill

You fetch audio from Suno **public share links** (`https://suno.com/s/...`)
into the album's audio root. Files land at
`{audio_root}/artists/{artist}/albums/{genre}/{album}/{NN}-{slug}.mp3` —
the exact path that `/bitwize-music:import-audio` would write to.

## Important Quality and Scope Caveats

**Read these before invoking.**

- **Preview quality only.** Suno's public share link serves a 64 kbps MP3.
  This is fine for QA listening, reference checks, and the
  `analyze_audio` / `transcribe_audio` MCP tools, but it is **not**
  production audio. The mastering chain (`mastering-engineer`,
  `release-director`) expects higher-bitrate MP3 or WAV from the user's
  Suno account dashboard.
- **Suno ToS.** This skill is intended for the user fetching audio from
  *their own* share links. Do not use it to bulk-download other users'
  songs.
- **Unstable contract.** Suno's CDN URL pattern (`cdn1.suno.ai/{uuid}.mp3`)
  is undocumented and may change. If this skill stops working, the most
  likely cause is a CDN/URL change — re-derive the pattern by inspecting
  what the Suno player loads.
- **Track frontmatter is the source of truth for `suno_url`.** If the
  caller does not pass an explicit URL, this skill reads
  `track.suno_url` from frontmatter (or the Track Details table) via
  the bitwize-music MCP.

---

## Step 1: Parse Arguments

Accept these forms:

| Form | Behavior |
|---|---|
| `<album-slug>` | Fetch every track whose `suno_url` is set and whose audio file does not already exist. |
| `<album-slug> <NN>` | Fetch just track NN. Use its `suno_url` from the track file. |
| `<album-slug> <NN>:<share-url>` | Fetch track NN using the provided URL (overrides frontmatter). |
| `<album-slug> <NN1> <NN2:url> ...` | Mixed — any combination of forms above for one album. |

If arguments are missing or the album cannot be resolved, ask:

```
Usage: /suno-download <album-slug> [<NN> | <NN>:<share-url>] ...

Examples:
  /suno-download what-lies-ahead
  /suno-download what-lies-ahead 13
  /suno-download what-lies-ahead 13:https://suno.com/s/0V2yElHWcpnsBJsp
  /suno-download what-lies-ahead 5 6 13:https://suno.com/s/XXXX
```

---

## Step 2: Resolve Audio Path

Call `resolve_path("audio", album_slug)` via MCP. Returns the full audio
directory, e.g.
`/home/user/.../audio/artists/the-agency-system/albums/electroacoustic/what-lies-ahead`.

Create the directory if it does not exist (`mkdir -p`).

---

## Step 3: Build the Work Set

For each requested track number:

1. Call `get_track(album_slug, "NN")` via MCP to retrieve the track
   metadata, including `suno_url` and the track slug.
2. If the caller supplied an explicit URL, use that instead of
   `track.suno_url`.
3. If neither source has a URL, **skip with a warning** — do not invent
   one.
4. If the destination file already exists, ask before overwriting.

For the "all tracks" form (`<album-slug>` only), call `find_album` or
`get_album_full(album_slug, summary_only=true)` to enumerate tracks, then
build the work set from every track whose `suno_url` is non-empty.

---

## Step 4: Download Each Track

For each work item — share URL plus destination filename `{NN}-{slug}.mp3`:

```bash
# 1. Resolve the share link to the song UUID by following the redirect.
UUID=$(curl -sI -k -L "$SHARE_URL" \
  | grep -i '^location:' \
  | grep -oE '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}' \
  | head -1)

# 2. Fetch the preview MP3 from Suno's CDN.
curl -sk -o "${AUDIO_DIR}/${NN}-${SLUG}.mp3" \
     -w "[$NN] %{http_code} %{size_download} bytes\n" \
     "https://cdn1.suno.ai/${UUID}.mp3"
```

**Notes:**
- `-k` (insecure) is required when the container's outbound proxy uses
  a self-signed CA. Drop it in environments with trusted certificates.
- The Suno share URL follows a redirect of the form
  `https://suno.com/s/<short>` → `https://suno.com/song/<uuid>?sh=<short>`.
  The UUID is what `cdn1.suno.ai/<uuid>.mp3` expects.
- Expected response: HTTP 200, content-type `audio/mp3`, size ~3–6 MB
  for typical 3–5 minute tracks at 64 kbps.

After download, **validate**:
- File size > 100 KB (a 4–5 KB file is the OpenGraph stub, not the song —
  retry or re-resolve the UUID).
- `ffprobe -v error -show_entries format=duration -of
  default=noprint_wrappers=1:nokey=1 "$OUT"` returns a positive duration.

If validation fails, leave the broken file in place but mark the track
as failed in the summary.

---

## Step 5: Report

Print a per-track summary:

```
[01] OK   3.95 MB  3:04  01-where-i-begin.mp3
[02] OK   4.64 MB  3:28  02-the-closed-loop.mp3
[03] FAIL stub returned (4 KB)
...
```

Then point the user at follow-up options:

- `/bitwize-music:analyze_audio` — verify the file is what they expect
- Replace with WAVs from the Suno dashboard before invoking
  `mastering-engineer`
- These are previews — do NOT advance the album to **Final** based on
  them alone

---

## Error Handling

| Symptom | Likely Cause | Fix |
|---|---|---|
| `curl: (60) SSL certificate problem` | Container proxy self-signs HTTPS | Use `-k` (already in template) |
| 200 response but file is 4–5 KB | Suno page returned OpenGraph stub, not the song | UUID resolution failed; check the redirect manually |
| 403 from `cdn1.suno.ai` | UUID is wrong or the song was deleted | Re-resolve via the share link |
| `Unable to download webpage` (yt-dlp legacy paths) | yt-dlp's generic extractor — do not use it | Use the curl pattern in Step 4 |
| Track UUID returns the wrong song | The share link was for a *different* generation of the same prompt | Use the explicit `<NN>:<url>` form to override |

---

## Example Session

```
User: /suno-download what-lies-ahead 13

Skill:
  Album:        what-lies-ahead
  Destination:  audio/artists/the-agency-system/albums/electroacoustic/what-lies-ahead
  Track 13:     suno_url = https://suno.com/s/0V2yElHWcpnsBJsp
  Resolving... UUID = 4d00c2a4-c1d4-4c90-983b-c22da706cd7c
  Downloading... 3.92 MB
  ✓ audio/.../13-from-outside.mp3 (3:07)

Done. Preview quality — replace with WAV from the Suno dashboard before
mastering.
```

---

## What This Skill Does NOT Do

- **Does not commit the audio.** The user decides whether to commit
  (typically via Git LFS — see the repo's `.gitattributes`) and from
  which machine.
- **Does not update track status to Generated.** Status reflects
  whether the user has accepted the take, not whether a file was
  fetched. Use `update_track_field("status", "Generated")` separately
  if that transition is intended.
- **Does not add Generation Log entries.** The Generation Log is the
  user's listening history; this skill fetches the file, not the
  listening decision.
- **Does not download WAVs or stems.** The public share link does not
  expose them. Those come from the user's authenticated Suno account.
- **Does not invoke `mastering-engineer`.** Previews are not master
  candidates.
