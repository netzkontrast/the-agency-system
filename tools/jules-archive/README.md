# Jules silent-fail patch archive (2026-05-17 / 2026-05-18)

On 2026-05-17 the Jules backend's auto-publish flow ("finalize") failed
silently across several sessions — state transitioned to `COMPLETED` but
no branch reached `github.com`. The orchestrator discovered the work was
still recoverable via `session.outputs[].changeSet.gitPatch.unidiffPatch`
on the Jules API. This directory archives those raw patches.

| Patch file | Spec | Session ID | Bytes | Status |
|---|---|---|---|---|
| `10206939400882938422-out0.patch` | 013 novel-handlers-structural (retry) | 10206939400882938422 | 40,349 | ✅ Applied via PR #47 (merged) |
| `11564636258482547195-out0.patch` | 007 jules-skills-and-commands-port (fresh) | 11564636258482547195 | 52,048 | ⚠️ Superseded — local subagent impl merged via PR #46 |
| `1268417896232581641-out0.patch`  | 008 codemode-registry | 1268417896232581641 | 23,049 | ⚠️ Superseded — local subagent impl merged via PR #46 |
| `14396551699037073836-out0.patch` | 005 music-skills-port | 14396551699037073836 | 1,094,422 | ⚠️ Superseded — local subagent impl merged via PR #46 |
| `18184265143767655568-out0.patch` | 007 jules-skills-and-commands-port (initial) | 18184265143767655568 | 53,451 | ⚠️ Superseded — local subagent impl merged via PR #46 |

The four "Superseded" patches collide with the merged subagent
implementations: their files already exist with different content on
Master. They are kept here for forensic comparison only — should never
be applied directly to a Master checkout.

To inspect a patch:
```bash
git apply --stat tools/jules-archive/<filename>.patch  # filenames + +/- counts only
```

To extract more patches from future Jules sessions:
```bash
python3 tools/jules-patch-extract.py <session_id>
python3 tools/jules-patch-extract.py <session_id> --apply --branch jules-NNN-extracted
```

The extractor never echoes patch body to stdout, only `{bytes, files,
first_files[]}` stats — safe for orchestrator context.
