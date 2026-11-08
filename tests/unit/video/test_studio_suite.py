"""Video Studio suite (skills/video/studio): structure, cross-references and the pure-Python/Node tools."""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
STUDIO = ROOT / "skills" / "video" / "studio"

PLAYBOOKS = [
    "music-video", "album-suite", "lyric-video", "visualizer-loop", "explainer", "product-launch", "brand-title",
    "animated-short", "documentary", "data-story", "social-vertical", "teaser-cutdown", "pathtraced-short",
]
AGENTS = [
    "strategist", "director", "songmap-analyst", "critic", "art-director", "animator", "integrator", "qa-operator",
    "reviewer", "sound", "copywriter", "vertical-editor",
]


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    assert m, "missing YAML frontmatter"
    return dict(line.split(":", 1) for line in m.group(1).splitlines() if ":" in line)


def test_skill_frontmatter():
    fm = frontmatter((STUDIO / "SKILL.md").read_text())
    assert fm["name"].strip() == "video-studio"
    assert len(fm["description"].strip()) > 100


def test_only_one_skill_file_in_the_suite():
    # references and examples must not be picked up as skills by the plugin's SKILL.md scan
    found = [p for p in STUDIO.rglob("SKILL.md") if "node_modules" not in p.parts]
    assert found == [STUDIO / "SKILL.md"]


@pytest.mark.parametrize("name", PLAYBOOKS)
def test_playbook_exists_with_skeleton(name):
    text = (STUDIO / "playbooks" / f"{name}.md").read_text()
    for section in ("## Inputs to collect", "## Defaults", "## Phase deltas", "## Team & fan-out", "## Gates & bar",
                    "## Deliverables", "## Checklist"):
        assert section in text, f"{name}.md lacks {section}"
    assert f"playbooks/{name}.md" in (STUDIO / "SKILL.md").read_text()


@pytest.mark.parametrize("name", AGENTS)
def test_agent_brief_exists_with_skeleton(name):
    text = (STUDIO / "agents" / f"{name}.md").read_text()
    assert text.startswith("# Brief:")
    assert "## Fill before sending" in text
    assert f"agents/{name}.md" in (STUDIO / "SKILL.md").read_text()


def _project_relative(path):
    """engine/<file> and lib/... paths in docs often mean a film project's copy; accept them if the studio has the file."""
    name = Path(path).name
    return path.startswith("engine/") and any((STUDIO / "engine" / d / name).exists() for d in ("paint", "lib", "canvas"))


def test_paths_cited_in_skill_playbooks_and_briefs_exist():
    pat = re.compile(r"(?<![\w/.-])((?:references|tools|engine|playbooks|agents|examples|gallery|bin)/[\w./-]+?\.(?:md|mjs|js|py|sh|html))")
    missing = {}
    for f in [STUDIO / "SKILL.md", *sorted((STUDIO / "playbooks").glob("*.md")), *sorted((STUDIO / "agents").glob("*.md"))]:
        for m in pat.findall(f.read_text()):
            if not (STUDIO / m).exists() and not _project_relative(m):
                missing.setdefault(m, []).append(f.name)
    assert not missing, f"cited but missing: {missing}"


def test_no_upstream_branding_in_the_suite():
    hits = []
    for f in STUDIO.rglob("*"):
        if f.is_file() and "node_modules" not in f.parts and f.suffix in {".md", ".html", ".mjs", ".js", ".sh", ".py", ".svg"}:
            if f.name == "THIRD_PARTY.md" or f.parent.name == "LICENSES":
                continue
            if re.search(r"Take One|take-one-logo|affiliate link", f.read_text(errors="ignore")):
                hits.append(str(f.relative_to(STUDIO)))
    assert not hits, hits


def test_licences_and_provenance_present():
    lic = {p.name for p in (STUDIO / "LICENSES").iterdir()}
    assert {"take-one-LICENSE-MIT.txt", "ClaudeAnimationBase-LICENSE-MIT-upstream.txt",
            "higgsfield-video-engineer-LICENSE-MIT.txt", "anidoodle-LICENSE-Apache-2.0.txt"} <= lic
    tp = (STUDIO / "THIRD_PARTY.md").read_text()
    for sha in ("830621cce11127a30120d7878570eb8acaaa5bad", "0ac8bf2b31942376cb6b8c4074715595d512acd2",
                "082bfd7b7b0b863799fa9afcdfeb3e84ba72e015"):
        assert sha in tp


def _words(tmp_path):
    data = {
        "words": [
            {"w": "lass", "t": 1.0, "end": 1.3, "stress": 1.1, "line": 0},
            {"w": "mich", "t": 1.35, "end": 1.6, "stress": 1.4, "line": 0},
            {"w": "atmen", "t": 2.4, "end": 3.1, "stress": 3.0, "line": 0},
            {"w": "ich", "t": 4.0, "end": 4.2, "stress": 4.05, "line": 1},
            {"w": "bin", "t": 4.25, "end": 4.5, "stress": 4.3, "line": 1},
            {"w": "hier", "t": 4.6, "end": 5.2, "stress": 4.8, "line": 1},
        ],
        "lines": [
            {"i": 0, "text": "lass mich atmen", "section": "Verse", "t": 1.0, "end": 3.1, "key": {"w": "atmen", "t": 2.4, "stress": 3.0}},
            {"i": 1, "text": "ich bin hier", "section": "Chorus", "t": 4.0, "end": 5.2, "key": {"w": "hier", "t": 4.6, "stress": 4.8}},
        ],
        "sections": [{"name": "Verse", "t": 1.0, "end": 4.0}, {"name": "Chorus", "t": 4.0, "end": 5.2}],
    }
    p = tmp_path / "words.json"
    p.write_text(json.dumps(data))
    return p


def test_srt_from_word_map(tmp_path):
    words = _words(tmp_path)
    out = tmp_path / "film.srt"
    subprocess.run([sys.executable, str(STUDIO / "tools/audio/srt.py"), "--words", str(words), "--out", str(out)], check=True)
    text = out.read_text()
    assert text.startswith("1\n00:00:00,900 --> 00:00:03,100\nlass mich atmen\n")
    assert "2\n00:00:03,900 --> 00:00:05,200\nich bin hier\n" in text
    ass = tmp_path / "film.ass"
    subprocess.run([sys.executable, str(STUDIO / "tools/audio/srt.py"), "--words", str(words), "--out", str(ass)], check=True)
    assert "\\k" in ass.read_text()


def test_songmap_js_merges_words_and_beats(tmp_path):
    words = _words(tmp_path)
    beatmap = tmp_path / "beatmap.json"
    beatmap.write_text(json.dumps({"bpm": 120, "beats": [0, 0.5, 1, 1.5, 2], "downbeats": [0, 2], "drop": 1.5,
                                   "hits": [1.0, 2.0], "sections": [{"name": "hook", "kind": "hook", "t": 0, "end": 2}]}))
    out = tmp_path / "songmap.js"
    subprocess.run([sys.executable, str(STUDIO / "tools/audio/songmap_js.py"), "--beatmap", str(beatmap), "--words", str(words),
                    "--out", str(out)], check=True)
    body = out.read_text().split("window.SONGMAP = ", 1)[1].rstrip().rstrip(";")
    m = json.loads(body)
    assert m["beats"] == [0, 0.5, 1, 1.5, 2] and m["drop"] == 1.5 and m["lastHit"] == 2.0
    assert [s["name"] for s in m["sections"]] == ["Verse", "Chorus"]  # lyric sections win over energy sections
    assert len(m["words"]) == 6


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_beat_js_follows_measured_beats_and_words():
    script = (
        "globalThis.SONGMAP={beats:[0,1,2,3,3.5,4],downbeats:[0,3],sections:[{name:'a',t:0},{name:'b',t:3}],"
        "words:[{w:'x',t:1,end:1.4},{w:'y',t:1.5,end:2}],lines:[],drop:3};"
        # beat.js is a classic browser script (the studio package is ESM), so run it as a script, not a module
        f"require('vm').runInThisContext(require('fs').readFileSync({json.dumps(str(STUDIO / 'engine/lib/beat.js'))}, 'utf8'));"
        "const S=globalThis.SONG;"
        "console.log(JSON.stringify([S.beatAt(3.25),S.barAt(1.5),S.section(3.1).name,S.word(1.6).w,S.word(1.45),S.hit('drop')]))"
    )
    out = subprocess.run(["node", "-e", script], capture_output=True, text=True, check=True).stdout
    assert json.loads(out) == [3.5, 0.5, "b", "y", None, 3]


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg not installed")
def test_flash_test_fails_a_strobe_and_passes_a_fade(tmp_path):
    pytest.importorskip("numpy")
    strobe, fade = tmp_path / "strobe.mp4", tmp_path / "fade.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                    "color=black:s=160x90:r=24:d=2,geq=lum='if(lt(mod(N\\,4)\\,2)\\,235\\,16)':cb=128:cr=128",
                    "-pix_fmt", "yuv420p", str(strobe)], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                    "color=black:s=160x90:r=24:d=2,geq=lum='16+219*N/48':cb=128:cr=128", "-pix_fmt", "yuv420p", str(fade)], check=True)
    tool = str(STUDIO / "tools/flash_test.py")
    assert subprocess.run([sys.executable, tool, str(strobe)], capture_output=True).returncode == 1
    assert subprocess.run([sys.executable, tool, str(fade)], capture_output=True).returncode == 0


def test_cli_lists_every_command():
    out = subprocess.run(["bash", str(STUDIO / "bin/studio"), "help"], capture_output=True, text=True, check=True).stdout
    for cmd in ("doctor", "new", "render", "gate", "songmap", "srt", "flash", "loudness", "pack", "review", "sheet"):
        assert f"studio {cmd}" in out


def test_skill_frontmatter_is_valid_yaml():
    # the plugin's skill listing parses frontmatter with yaml.safe_load and silently drops a skill it cannot parse
    yaml = pytest.importorskip("yaml")
    text = (STUDIO / "SKILL.md").read_text()
    data = yaml.safe_load(text.split("---")[1])
    assert data["name"] == "video-studio" and "music videos" in data["description"]


FX_NAMES = ["ink", "toon", "kuwahara", "watercolor", "hatch", "halftone", "riso", "dither", "pixelate", "posterize",
            "crt", "boil", "paper", "grain", "vignette", "chroma", "grade", "glitch", "fade"]


def test_three_pass_catalogue_is_complete_and_documented():
    src = (STUDIO / "engine/three/passes.js").read_text()
    doc = (STUDIO / "references/three-medium.md").read_text()
    for name in FX_NAMES:
        assert re.search(rf"^\s+{name}: \(o\) => pass\('{name}'", src, re.M), f"FX.{name} missing"
        assert f"`{name}`" in doc, f"FX.{name} not documented"
    assert "Math.random" not in src  # our passes hash from uTime; the page seeds Math.random for addons


def test_glsl_library_includes_and_attributions():
    glsl = STUDIO / "engine/glsl"
    assert {p.name for p in glsl.glob("*.glsl")} >= {"hash.glsl", "noise.glsl", "sdf.glsl", "color.glsl", "dither.glsl"}
    assert "MIT License" in (glsl / "noise.glsl").read_text() and "Ashima" in (glsl / "noise.glsl").read_text()
    for f in (STUDIO / "engine/shader").glob("*.frag"):
        for inc in re.findall(r'#include "([^"]+)"', f.read_text()):
            assert (STUDIO / inc).exists(), f"{f.name} includes missing {inc}"


@pytest.mark.parametrize("medium,files", [
    ("three", ["film.html", "scenes/scene.js", "engine/passes.js", "engine/beat.js", "config.js", "songmap.js"]),
    ("shader", ["film.html", "scenes/film.js", "scenes/main.frag", "scenes/trails.frag", "engine/runtime.js", "engine/glsl/noise.glsl"]),
    ("paint", ["film.html", "scenes/ch01.js", "engine/core.js", "engine/beat.js"]),
    ("canvas", ["film.html", "engine/springs.js", "engine/beat.js"]),
])
def test_new_project_scaffolds_each_medium(tmp_path, medium, files):
    if not (STUDIO / "node_modules").exists():
        pytest.skip("studio packages not installed (bin/studio doctor)")
    d = tmp_path / medium
    subprocess.run(["bash", str(STUDIO / "tools/new-project.sh"), str(d), "--medium", medium, "--duration", "3"],
                   check=True, capture_output=True)
    for f in files:
        assert (d / f).exists(), f"{medium}: {f} missing"
    assert (d / ".studio-medium").read_text().strip() == medium


def test_importmap_targets_exist_when_installed():
    if not (STUDIO / "node_modules").exists():
        pytest.skip("studio packages not installed")
    imp = json.loads((STUDIO / "engine/lib/importmap.json").read_text())["imports"]
    for name, path in imp.items():
        assert (STUDIO / path.replace("./", "", 1)).exists(), f"{name} → {path} missing"


def test_pipeline_smoke_run_is_recorded():
    run = STUDIO / "examples/pipeline-smoke"
    text = (run / "RUN.md").read_text()
    assert "CLEAR" in text and "PASS on all six" in text
    assert sorted(p.name for p in (run / "review").glob("critique-*.md"))[-1] == "critique-6.md"
    assert len(list((run / "review").glob("review-[0-9].md"))) == 3   # the 3-round reviewer limit per cycle was honoured
    assert len(list((run / "review").glob("review-take*.md"))) == 11   # later takes, each with its own fresh reviewer
    assert "score stalled" in text


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_pulse_soft_has_no_one_frame_jump():
    script = (
        "globalThis.SONGMAP={beats:[0,0.5,1,1.5,2]};"
        f"require('vm').runInThisContext(require('fs').readFileSync({json.dumps(str(STUDIO / 'engine/lib/beat.js'))}, 'utf8'));"
        "const S=globalThis.SONG; const v=[1.0,1+1/24,1+2/24,1+3/24].map(t=>S.pulseSoft(t));"
        "console.log(JSON.stringify(v))"
    )
    v = json.loads(subprocess.run(["node", "-e", script], capture_output=True, text=True, check=True).stdout)
    assert v[0] == 0 and max(b - a for a, b in zip(v, v[1:])) < 0.6   # rises over several frames


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_beat_fallback_reads_const_project_bpm():
    # config.js declares `const PROJECT` (not a window property); without a song map the beat must follow its bpm
    beat = json.dumps(str(STUDIO / "engine/lib/beat.js"))
    script = (
        "const vm=require('vm'),fs=require('fs');const c={};c.globalThis=c;vm.createContext(c);"
        "vm.runInContext('const PROJECT={bpm:90,offset:0};',c);"
        f"vm.runInContext(fs.readFileSync({beat},'utf8'),c);console.log(c.SONG.beatAt(2))"
    )
    out = subprocess.run(["node", "-e", script], capture_output=True, text=True, check=True).stdout
    assert float(out) == pytest.approx(3.0)


def test_gate_serves_module_scripts():
    src = (STUDIO / "tools/gate.mjs").read_text()
    assert "'.mjs': 'text/javascript'" in src


def test_toon_pass_never_floors_to_black():
    src = (STUDIO / "engine/three/passes.js").read_text()
    toon = src[src.index("toon: (o)"):src.index("kuwahara: (o)")]
    assert "pluma(" in toon and "+ .5" in toon


def test_recipe_sampler_record():
    readme = (STUDIO / "examples/recipe-sampler/README.md").read_text()
    assert "PASS 4/4" in readme and "Status after the sampler" in readme
    for m in ("three", "shader", "canvas"):
        sheet = STUDIO / f"gallery/recipes-{m}.jpg"
        assert sheet.exists() and sheet.stat().st_size < 1_000_000
