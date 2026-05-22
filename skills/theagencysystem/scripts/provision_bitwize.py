#!/usr/bin/env python3
"""Provision the bitwize-music environment for an artist.

Two safe, opt-in operations (defaults to the Agency System, works for any artist):

  overrides   (Re)generate the CRAFT override files in the repo's `overrides/`
              from the templates in `scripts/templates/`, so bitwize skills
              (lyric-writer, suno-engineer, mastering-engineer, ...) read the
              artist's craft conventions — including the no-labels / function-
              form rule.

  config      Render `~/.bitwize-music/config.yaml` from the repo template
              `.claude/bitwize-music.config.template.yaml` for a given artist.
              Use this to switch the active artist on demand instead of waiting
              for the SessionStart hook.

Safety model (these files are curated and/or live):
  * Dry-run by DEFAULT — prints what WOULD change; writes nothing.
  * `--write` applies changes; every existing target is first copied to
    `<file>.bak-<timestamp>` so any overwrite is reversible.
  * A denylist makes it impossible to touch album/project-specific overrides
    (visual-language-guide, the-eleven, kohaerenz-protokoll, image-style-spec,
    genre-*). Those hold album content, not cross-project craft.
  * After ANY `config` change you must run the bitwize `rebuild_state` MCP tool:
    the indexer caches `overrides_dir`/`artist` into `~/.bitwize-music/cache/
    state.json`, and `load_override` reads that cache, not the live config.

Requires: Python 3.8+. PyYAML is optional (used only to validate the rendered
mastering-presets.yaml); the script degrades gracefully without it.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import difflib
import sys
from pathlib import Path

# scripts/provision_bitwize.py lives at REPO/skills/theagencysystem/scripts/,
# so the repo root is three directories up. Resolve symlinks first.
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[2]
TEMPLATE_DIR = SCRIPT_DIR / "templates"
CONFIG_TEMPLATE = REPO_ROOT / ".claude" / "bitwize-music.config.template.yaml"
HOME_CONFIG = Path.home() / ".bitwize-music" / "config.yaml"

# Cross-project CRAFT overrides this tool may generate: override file -> template.
CRAFT_OVERRIDES = {
    "lyric-writing-guide.md": "lyric-writing-guide.md.tmpl",
    "suno-preferences.md": "suno-preferences.md.tmpl",
    "mastering-presets.yaml": "mastering-presets.yaml.tmpl",
    "research-preferences.md": "research-preferences.md.tmpl",
    "promotion-preferences.md": "promotion-preferences.md.tmpl",
    "pronunciation-guide.md": "pronunciation-guide.md.tmpl",
    "voice-craft-principles.md": "voice-craft-principles.md.tmpl",
}

# Album/project-specific files — NEVER write these via the craft provisioner.
DENYLIST = {
    "visual-language-guide.md",
    "image-style-spec.md",
    "kohaerenz-protokoll-sprach-dna.md",
    "the-eleven.md",
}

DEFAULT_ARTIST_NAME = "the Agency System"
DEFAULT_ARTIST_SLUG = "the-agency-system"


def _stamp() -> str:
    return _dt.datetime.now().strftime("%Y%m%d-%H%M%S")


def _render(text: str, artist_name: str, artist_slug: str) -> str:
    return text.replace("{{ARTIST_NAME}}", artist_name).replace(
        "{{ARTIST_SLUG}}", artist_slug
    )


def _backup(path: Path) -> Path:
    dst = path.with_name(f"{path.name}.bak-{_stamp()}")
    dst.write_bytes(path.read_bytes())
    return dst


def _diffstat(old: str, new: str) -> str:
    if old == new:
        return "unchanged"
    added = removed = 0
    for line in difflib.unified_diff(old.splitlines(), new.splitlines(), n=0):
        if line.startswith("+") and not line.startswith("+++"):
            added += 1
        elif line.startswith("-") and not line.startswith("---"):
            removed += 1
    return f"+{added} -{removed} lines"


def _validate_yaml(path_label: str, text: str) -> bool:
    try:
        import yaml  # type: ignore
    except ImportError:
        print(f"  note: PyYAML not installed; skipped YAML validation of {path_label}")
        return True
    try:
        yaml.safe_load(text)
        return True
    except yaml.YAMLError as exc:  # pragma: no cover - defensive
        print(f"  ERROR: rendered {path_label} is not valid YAML: {exc}", file=sys.stderr)
        return False


def cmd_overrides(args: argparse.Namespace) -> int:
    overrides_dir = Path(args.overrides_dir).expanduser().resolve()
    if not TEMPLATE_DIR.is_dir():
        print(f"ERROR: template dir not found: {TEMPLATE_DIR}", file=sys.stderr)
        return 2
    overrides_dir.mkdir(parents=True, exist_ok=True)

    targets = CRAFT_OVERRIDES
    if args.only:
        if args.only not in CRAFT_OVERRIDES:
            print(
                f"ERROR: {args.only!r} is not a craft override. "
                f"Choose from: {', '.join(sorted(CRAFT_OVERRIDES))}",
                file=sys.stderr,
            )
            return 2
        targets = {args.only: CRAFT_OVERRIDES[args.only]}

    mode = "WRITE" if args.write else "dry-run"
    print(f"[{mode}] overrides dir: {overrides_dir}")
    print(f"        artist: {args.artist_name} ({args.artist_slug})\n")

    rc = 0
    for override_name, tmpl_name in sorted(targets.items()):
        if override_name in DENYLIST:  # belt-and-suspenders; should never happen
            print(f"  SKIP {override_name}: denylisted (album-specific)")
            continue
        tmpl_path = TEMPLATE_DIR / tmpl_name
        if not tmpl_path.is_file():
            print(f"  SKIP {override_name}: template missing ({tmpl_name})")
            continue
        rendered = _render(
            tmpl_path.read_text(encoding="utf-8"), args.artist_name, args.artist_slug
        )
        if override_name.endswith(".yaml") and not _validate_yaml(override_name, rendered):
            rc = 1
            continue
        target = overrides_dir / override_name
        existing = target.read_text(encoding="utf-8") if target.is_file() else ""
        stat = "create" if not target.is_file() else _diffstat(existing, rendered)
        print(f"  {override_name:28} {stat}")
        if args.diff and existing != rendered:
            sys.stdout.writelines(
                difflib.unified_diff(
                    existing.splitlines(keepends=True),
                    rendered.splitlines(keepends=True),
                    fromfile=f"a/{override_name}",
                    tofile=f"b/{override_name}",
                )
            )
        if args.write and existing != rendered:
            if target.is_file():
                bak = _backup(target)
                print(f"      backed up -> {bak.name}")
            target.write_text(rendered, encoding="utf-8")

    if not args.write:
        print("\nDry-run only. Re-run with --write to apply (existing files are backed up).")
    return rc


def cmd_config(args: argparse.Namespace) -> int:
    if not CONFIG_TEMPLATE.is_file():
        print(f"ERROR: config template not found: {CONFIG_TEMPLATE}", file=sys.stderr)
        return 2
    repo = Path(args.repo).expanduser().resolve()
    text = CONFIG_TEMPLATE.read_text(encoding="utf-8").replace("${REPO}", str(repo))

    # Replace the artist.name value (the only `name:` key in the template).
    out_lines, in_artist, swapped = [], False, False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "artist:":
            in_artist = True
        elif in_artist and not swapped and stripped.startswith("name:"):
            indent = line[: len(line) - len(line.lstrip())]
            line = f"{indent}name: {args.artist_slug}"
            swapped = True
        elif line and not line[0].isspace() and stripped != "artist:":
            in_artist = False
        out_lines.append(line)
    rendered = "\n".join(out_lines) + "\n"

    if not _validate_yaml("config.yaml", rendered):
        return 1

    print(f"[{'WRITE' if args.write else 'dry-run'}] target: {HOME_CONFIG}")
    print(f"        artist: {args.artist_slug}   repo: {repo}\n")
    existing = HOME_CONFIG.read_text(encoding="utf-8") if HOME_CONFIG.is_file() else ""
    print(f"  config.yaml  {'create' if not existing else _diffstat(existing, rendered)}")
    if args.diff and existing != rendered:
        sys.stdout.writelines(
            difflib.unified_diff(
                existing.splitlines(keepends=True),
                rendered.splitlines(keepends=True),
                fromfile="a/config.yaml",
                tofile="b/config.yaml",
            )
        )
    if args.write:
        HOME_CONFIG.parent.mkdir(parents=True, exist_ok=True)
        if HOME_CONFIG.is_file() and existing != rendered:
            bak = _backup(HOME_CONFIG)
            print(f"      backed up -> {bak}")
        HOME_CONFIG.write_text(rendered, encoding="utf-8")
        print("\n  Wrote config. NOW RUN the bitwize `rebuild_state` MCP tool so the")
        print("  indexer refreshes overrides_dir/artist before any bitwize skill runs.")
    else:
        print("\nDry-run only. Re-run with --write to apply (existing config is backed up).")
    return 0


def cmd_list(_args: argparse.Namespace) -> int:
    print("Craft overrides this tool can generate (override <- template):")
    for name, tmpl in sorted(CRAFT_OVERRIDES.items()):
        present = "ok" if (TEMPLATE_DIR / tmpl).is_file() else "MISSING"
        print(f"  {name:28} <- templates/{tmpl}   [{present}]")
    print("\nNever touched (album/project-specific):")
    for name in sorted(DENYLIST):
        print(f"  {name}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    # Shared flags live on a parent parser so they work AFTER the subcommand
    # (e.g. `overrides --write`, `config --artist-slug x`), matching the docs.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--artist-name", default=DEFAULT_ARTIST_NAME, help="display name (default: %(default)s)")
    common.add_argument("--artist-slug", default=DEFAULT_ARTIST_SLUG, help="path/config slug (default: %(default)s)")
    common.add_argument("--write", action="store_true", help="apply changes (default: dry-run)")
    common.add_argument("--diff", action="store_true", help="print full unified diff per file")

    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    o = sub.add_parser("overrides", parents=[common], help="(re)generate craft override files")
    o.add_argument("--overrides-dir", default=str(REPO_ROOT / "overrides"), help="default: %(default)s")
    o.add_argument("--only", help="generate a single craft override by filename")
    o.set_defaults(func=cmd_overrides)

    c = sub.add_parser("config", parents=[common], help="render ~/.bitwize-music/config.yaml for an artist")
    c.add_argument("--repo", default=str(REPO_ROOT), help="content root (default: %(default)s)")
    c.set_defaults(func=cmd_config)

    sub.add_parser("list", help="list craft overrides and the denylist").set_defaults(func=cmd_list)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
