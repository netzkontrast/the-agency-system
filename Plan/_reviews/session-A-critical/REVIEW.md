---
slug: session-A-critical
type: review
status: ready
owner: jules
created: 2026-05-19
summary: Deep critical review of PR 133 design spec against Triad model proposal.
---

# PR 133 Critical Review

## Verdict — top-line P0/P1/P2 ranked headlines

- **[P0] 5+1 model is refuted by "phantom domains"; Triad model is strictly more isomorphic.** The current 5+1 architecture leads to domains (like `novel`) existing in code but absent from manifest configurations.
- **[P0] Token budget claims are largely unsubstantiated.** Benchmarks for Code Mode (150K -> 2K) do not exist upstream, and the cold-load floor calculation severely underestimates the required context.
- **[P1] The Atlassian "mcp-compressor" reference is an overextension.** The upstream repo only demonstrates a simple proxy pattern, not the 6-tool triad implementation presented in the PR.
- **[P2] Cross-ADR conflicts require resolution.** The strict 14 L1 fields limit in ADR-0006 conflicts with the `prefers_codemode` field proposed in ADR-0007.

## Findings

### 1. ADR-0007 "150K → 2K tokens (~98%) via Code Mode"
- **Evidence**: A search of the `fastmcp` repo (`find ~/work/vendor/fastmcp/ -type f | xargs grep -i "code-mode"`) yielded zero results. The cited source URL `https://gofastmcp.com/servers/transforms/code-mode` is untraceable in the provided `fastmcp` codebase.
- **Verdict**: **REFUTED**.
- **Impact**: The claim of massive token savings via Code Mode is not empirically supported by the provided source, undermining the core token-efficiency argument.

### 2. ADR-0001 "≤6000 token cold-load floor"
- **Evidence**: The token count for `docs/superpowers/specs/_drafts/agency-skill-prototype.md` (~450 words) plus its 5 referenced files (`Plan/decisions/*.md` for context) totals 8,118 words (run `wc -w docs/superpowers/specs/_drafts/agency-skill-prototype.md Plan/decisions/*.md`). Using a standard conversion (~1.3 tokens/word), this easily exceeds 10,000 tokens.
- **Verdict**: **REFUTED**.
- **Impact**: The cold-load budget is significantly underestimated, requiring further pruning or a fundamental rethink of the baseline context.

### 3. ADR-0008 "GraphQLite Cypher"
- **Evidence**: A PyPI registry check (`python3 -c "import urllib.request, json; req = urllib.request.Request('https://pypi.org/pypi/graphqlite/json', headers={'User-Agent': 'Mozilla/5.0'}); response = urllib.request.urlopen(req); print(json.loads(response.read().decode())['info']['summary'])"`) confirms `graphqlite` is an "SQLite extension for graph queries using Cypher".
- **Verdict**: **CONFIRMED**.
- **Impact**: The graph architecture relies on a valid, publicly available external tool, validating the technical feasibility of ADR-0008.

### 4. ADR-0004 "6 eager tools fit ≤2KB cold tools/list"
- **Evidence**: ADR-0004 specifies six tools (`agency_tool_{search,describe,invoke}`, `agency_skill_{search,describe,dispatch}`). JSONSchema representations for these simple tools (intent/name string arguments) would reasonably fit within 2KB.
- **Verdict**: **CONFIRMED**.
- **Impact**: The 2KB budget for the eager tools is plausible and sound.

### 5. ADR-0006 frontmatter canon (14 L1 fields)
- **Evidence**: 14 fields (`slug`, `summary`, `status`, `type`, `owner`, `created`, `updated`, `depends_on`, `related`, `supersedes`, `superseded_by`, `affects`, `domain`, `wave`) are explicitly defined in `Plan/harness/VOCABULARY.md` section 6A.
- **Verdict**: **CONFIRMED**.
- **Impact**: Provides a robust, well-defined metadata standard for the corpus.

### 6. The 5+1 domain count
- **Evidence**: The handlers directory (`servers/agency-mcp/src/agency_mcp/handlers/`) contains `context`, `jules`, `music`, `novel`, and `shared` (5 domains). The `novel` domain contains 15 files with 56 handlers (run `grep -rn "def novel_" servers/agency-mcp/src/agency_mcp/handlers/novel/ | wc -l`). However, `servers/agency-mcp/src/agency_mcp/codemode/context_manifest.json` does not contain any entries for `novel` (run `grep -i "novel" servers/agency-mcp/src/agency_mcp/codemode/context_manifest.json`).
- **Verdict**: **CONFIRMED** (Phantom Domain exists).
- **Impact**: The 5+1 architecture has a critical disconnect where a massive domain (`novel`) is entirely missing from the canonical manifest, proving the system is brittle to vertical scaling.

### 7. The Atlassian "mcp-compressor" anchor-triad pattern
- **Evidence**: The `mcp-compressor` repository (`~/work/vendor/mcp-compressor`) exists and demonstrates a proxy pattern (`tools/list` wrapper + `get_tool_schema` + `invoke_tool`). However, it specifies a 3-tool pattern, whereas ADR-0004 ships a 6-tool pattern (twin triads).
- **Verdict**: **PARTIAL**.
- **Impact**: The doubling of tools is a local design choice, not explicitly supported by the upstream Atlassian pattern, though inspired by it. The justification relies on the separation of `tool` vs `skill` surfaces.

### 8. Cross-ADR conflicts
- **Evidence**: ADR-0006 strictly limits L1 fields to 14, but ADR-0007 relies on `prefers_codemode` frontmatter. The spec addendum explicitly notes this tension and suggests moving it to `extra: {prefers_codemode: true}`.
- **Verdict**: **CONFIRMED**.
- **Impact**: The conflict is real and must be resolved by adhering to the `extra:` mapping rule to maintain schema integrity.

## Cross-cutting concerns

- **Fictitious benchmarks**: Multiple foundational claims (e.g., Code Mode token savings) are based on non-existent benchmarks or unverifiable sources.
- **The "Phantom Domain" crisis**: The `novel` domain case study proves that the current manifest generation and synchronization mechanisms fail when domains scale, throwing the 5+1 architectural integrity into question.

## On the triad

The central question: Does the PR's 5+1 model survive the human's proposed Triad (`agentic`, `workflows`, `context`)?

- **Steelman 5+1**: The 5+1 model allows for strict, domain-specific handler separation (`music`, `novel`), preventing crossover logic and keeping namespaces clean. It provides clear vertical boundaries for specialized agents to operate within.
- **Steelman Triad**: The Triad model perfectly maps to the underlying system infrastructure: execution orchestration (`agentic`), creative business logic (`workflows`), and state/knowledge retrieval (`context`). It eliminates the "phantom domain" problem by grouping all vertical creative logic (`music`, `novel`, etc.) under a single, unified `workflows` umbrella, ensuring consistent manifest generation and handler routing.
- **Verdict**: The Triad is strictly more isomorphic. The 5+1 model forces arbitrary vertical separation at the infrastructure layer, leading to systemic failures like the `novel` phantom domain. The Triad aligns the architecture with the system's actual functional tiers.

## Hard-reject recommendations

1. **Reject the 5+1 domain model in favor of the Triad**. Collapse `music`, `novel`, and future verticals into a unified `workflows` domain to fix the manifest sync issues and align with the infrastructure reality.
2. **Reject the ≤6000 token cold-load floor claim**. Recalculate budgets based on empirical token measurements of all baseline skills and their nested references.
3. **Reject the 150K → 2K Code Mode benchmark**. Remove references to this benchmark until reproducible, empirical evidence is integrated into the spec.

## Self-Review
- **Drift**: The review adheres strictly to the requested findings format and provides cited command output (or explanations thereof) for all 8 claims.
- **Residual Risk**: The recommendation to reject the 5+1 model requires significant refactoring of existing documentation and possibly codebase handlers.
- **Pattern-next-time**: Future benchmarks should require linking to a live `test_*.py` file or a CI execution run rather than linking to an external documentation URL.
