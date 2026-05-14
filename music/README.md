# music/

This is the storage root for the bitwize-music plugin (see
`.claude/bitwize-music.config.template.yaml`). All album work — concepts,
lyrics, mastered audio, research documents — is written here so it lives
inside the repository and gets versioned alongside the rest of the code.

```
music/
├── content/    # albums, tracks, READMEs, lyrics (content_root)
├── audio/      # mastered audio files (audio_root)
├── documents/  # research PDFs and references (documents_root)
├── overrides/  # CLAUDE.md, pronunciation guides, etc. (overrides)
└── IDEAS.md    # album-ideas brainstorming file (ideas_file)
```

The album path layout used by the plugin under `content/` is:

```
content/artists/<artist>/albums/<genre>/<album-slug>/
content/artists/<artist>/albums/<genre>/<album-slug>/tracks/
```

## Heavy binaries are versioned via Git LFS

`music/audio/` (`.wav`, `.flac`, `.mp3`, `.aiff`, `.aif`, `.ogg`, `.m4a`) and
`music/documents/` (`.pdf`, `.epub`, `.docx`) are tracked through
[Git LFS](https://git-lfs.com). Before cloning or pushing on a new
machine, install LFS and run `git lfs install` once. Patterns are
declared in the repo's `.gitattributes`.
