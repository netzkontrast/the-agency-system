# JULES-REVIEW: Bash-Only Engine Execution Validation

This review validates that a BASH-ONLY agent can drive the `agency` engine using ONLY the shell and the `agency-seed/AGENTS.md` instructions.

## 1. Setup Phase

The setup instructions in `AGENTS.md` are:
```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt   # graphqlite + fastmcp
```

### Findings
Running these initial commands succeeds, but the resulting environment is **insufficient** to run the engine or the tests.

**Gap 1: Missing `pysqlite3-binary` and SQLite extension loading capability.**
Running the test suite (`python -m pytest -q`) immediately failed with:
`RuntimeError: SQLite extension loading not available. Your Python's sqlite3 module may not support extensions.`
This is a common issue because the standard library `sqlite3` in many python builds has extension loading disabled for security reasons.

**Fix 1:** I had to manually install `pysqlite3-binary` and inject it to replace the standard `sqlite3` module before running tests or the CLI:
```bash
pip install pysqlite3-binary
echo "import sys, pysqlite3; sys.modules['sqlite3'] = pysqlite3; sys.modules['sqlite3.dbapi2'] = pysqlite3" > .venv/lib/python3.12/site-packages/sitecustomize.py
```

**Gap 2: Missing `fastmcp[code-mode]` feature flag.**
After fixing the SQLite issue, `python -m pytest -q` passed 4 tests but failed 3, and attempting to run `execute` over the CLI failed with:
`fastmcp.exceptions.ToolError: Error calling tool 'execute': CodeMode requires pydantic-monty for the Monty sandbox provider. Install it with \`fastmcp[code-mode]\``
The `requirements.txt` only specifies `fastmcp` and `fastmcp-slim`.

**Fix 2:** I had to install the `code-mode` extras explicitly:
```bash
pip install "fastmcp[code-mode]"
```
After applying these two fixes, `python -m pytest -q` ran perfectly, resulting in **7 passed** tests in 6.56s.

## 2. Bootstrapping an Intent

Before executing tools against an Intent, we need an intent in the graph. `AGENTS.md` mentions getting an intent id, but does not provide the code snippet to bootstrap one.

**Finding:** Bootstrapping an intent requires knowledge of the `Intent` python class API. I crafted the following bootstrap script to create and confirm an intent:
```python
from agency_seed.engine import Engine
from agency_seed.intent import Intent
engine = Engine("graph.db")
intent = Intent(engine.memory)
i_id = intent.capture(purpose="test intent", deliverable="some deliverable", acceptance="all good")
intent.confirm(i_id)
print(i_id)
```
This outputted the intent ID: `intent:97a29d3a`.

## 3. Driving the Engine purely via Bash CLI

With the intent created, I followed the steps in `AGENTS.md` to interact with the engine.

### a. `search`
**Command:** `python -m agency_seed.cli --db graph.db search "syllables count"`
**Output:**
```
1 of 4 tools:

- capability_syllables_count: Count syllables (transform); recorded as an Invocation that SERVES the intent.
```
**Result:** Worked exactly as documented.

### b. `get-schema`
**Command:** `python -m agency_seed.cli --db graph.db get-schema capability_syllables_count`
**Output:**
```
### capability_syllables_count

Count syllables (transform); recorded as an Invocation that SERVES the intent.

**Parameters**
- `text` (string, required)
- `intent_id` (string, required)

**Returns**
- `result` (integer, required)
```
**Result:** Worked exactly as documented.

### c. `execute` capability_syllables_count
**Command:**
```bash
python -m agency_seed.cli --db graph.db execute --code '
r = await call_tool("capability_syllables_count", {"text": "hello world test bash cli", "intent_id": "intent:97a29d3a"})
return r["result"] if isinstance(r, dict) and "result" in r else r
'
```
**Output:** `6`
**Result:** Worked perfectly. The token-efficiency pattern is very effective.

### d. `execute` memory_graph_provenance
First, I searched for "provenance" to get the tool name (`memory_graph_provenance`) and schema (`intent_id` required parameter).
**Command:**
```bash
python -m agency_seed.cli --db graph.db execute --code '
r = await call_tool("memory_graph_provenance", {"intent_id": "intent:97a29d3a"})
return r["result"] if isinstance(r, dict) and "result" in r else r
'
```
**Output:**
```json
{"serves": [{"id": "invocation:c0fc9ce5", "vfrom": 1, "vto": 1000000000000, "capability": "syllables", "verb": "count", "role": "transform"}], "agents": [], "artefacts": [], "gates": []}
```
**Result:** Worked exactly as documented and proved that the execution mirrored the `capability_syllables_count` invocation into the provenance graph.

## 4. REVIEW SUMMARY

Is `AGENTS.md` accurate and sufficient for a shell-only agent?

**No, not out of the box.** While the CLI commands (`search`, `get-schema`, `execute`) are brilliantly accurate and highly effective, the initial setup phase is broken on standard Linux environments and missing critical dependencies. An agent cannot proceed to the CLI steps without first debugging and fixing the python environment.

### Suggested Fixes for `AGENTS.md` / `requirements.txt`:
1.  **Update Setup Instructions:** Explicitly state the need for `pysqlite3-binary` and document the `sitecustomize.py` hack for SQLite extensions, or better yet, bundle this logic into the codebase's initialization sequence.
2.  **Update `requirements.txt`:** Change `fastmcp` to `fastmcp[code-mode]` in `requirements.txt` or explicitly add `pydantic-monty`.
3.  **Add Intent Bootstrap Script:** Provide the 6-line python snippet to bootstrap an intent into `graph.db`, as the CLI tests require an intent ID but the CLI does not provide a tool to create an intent from scratch.

Once the setup is correct, the bash-only CLI contract is extremely powerful and works exactly as described.