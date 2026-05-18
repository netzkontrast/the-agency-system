import json
import math
from pathlib import Path

class ContextManifestError(Exception):
    pass

class ContextManifest:
    def __init__(self, data: dict, repo_root: str = None):
        self.data = data
        self.entries = data.get("entries", [])
        self.by_id = {e["id"]: e for e in self.entries}
        self.repo_root = repo_root or "."

        # Load schema for validation
        schema_path = Path(__file__).parent.parent.parent / "codemode" / "context_manifest.schema.json"
        if schema_path.exists():
            with open(schema_path, "r") as f:
                self.schema = json.load(f)
        else:
            self.schema = None

    @classmethod
    def from_dict(cls, data: dict, repo_root: str = None):
        return cls(data, repo_root)

    def validate_against_schema(self):
        import jsonschema

        if self.schema:
            try:
                jsonschema.validate(instance=self.data, schema=self.schema)
            except jsonschema.ValidationError as e:
                raise ContextManifestError(f"Schema validation failed: {e.message}")

        # Additional custom validation
        allowed_prefixes = ("domain:", "kind:", "topic:", "spec:", "slug:", "lesson_id:")

        for entry in self.entries:
            # Tag prefix validation
            for tag in entry.get("tags", []):
                if not tag.startswith(allowed_prefixes):
                    raise ContextManifestError(f"Tag '{tag}' in entry {entry['id']} does not start with an allowed prefix: {allowed_prefixes}")

            # File existence check
            path = Path(self.repo_root) / entry["path"]
            if not path.exists():
                 raise ContextManifestError(f"File referenced in manifest not found: {entry['path']}")

            # Token budget validation
            views = entry.get("views", {})
            summary_view = views.get("summary", {})
            if summary_view.get("token_estimate", 0) > 120:
                 raise ContextManifestError(f"views.summary.token_estimate exceeds 120 tokens for {entry['id']}")
            preview_view = views.get("preview", {})
            if preview_view.get("token_estimate", 0) > 800:
                 raise ContextManifestError(f"views.preview.token_estimate exceeds 800 tokens for {entry['id']}")

    def get(self, id: str):
        return self.by_id.get(id)

    def search(self, query: str, *, domain: str = None, tags: list[str] = None, limit: int = 20):
        # Filter entries
        filtered = []
        for entry in self.entries:
            match = True

            entry_tags = set(entry.get("tags", []))
            if domain:
                if f"domain:{domain}" not in entry_tags:
                    match = False

            if tags:
                for tag in tags:
                    if tag not in entry_tags:
                        match = False
                        break

            if match:
                filtered.append(entry)

        if not filtered:
            return []

        # BM25 Scoring
        try:
            from rank_bm25 import BM25Okapi
            has_bm25 = True
        except ImportError:
            has_bm25 = False

        # Prepare documents
        tokenized_corpus = []
        for entry in filtered:
            doc = f"{entry.get('title', '')} {entry.get('summary', '')} {' '.join(entry.get('tags', []))}"
            tokenized_corpus.append(doc.lower().split())

        tokenized_query = query.lower().split()

        if has_bm25:
            bm25 = BM25Okapi(tokenized_corpus)
            doc_scores = bm25.get_scores(tokenized_query)
        else:
            # Simple fallback BM25
            doc_scores = self._simple_bm25(tokenized_query, tokenized_corpus)

        # Title boost
        for i, entry in enumerate(filtered):
            title = entry.get('title', '').lower()
            query_lower = query.lower()
            if query_lower in title:
                doc_scores[i] += 2.0  # Significant boost for title matches
            elif any(q in title for q in tokenized_query):
                doc_scores[i] += 1.0  # Minor boost for partial title matches

        # Rank
        results = []
        for i, score in enumerate(doc_scores):
            if score > 0:
                entry = filtered[i]
                results.append({
                    "id": entry.get("id"),
                    "title": entry.get("title"),
                    "summary": entry.get("summary"),
                    "tags": entry.get("tags", []),
                    "score": float(score)
                })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

    def _simple_bm25(self, query: list[str], corpus: list[list[str]]):
        # A very basic BM25 implementation
        k1 = 1.5
        b = 0.75

        doc_lengths = [len(doc) for doc in corpus]
        avg_dl = sum(doc_lengths) / len(doc_lengths) if doc_lengths else 0

        N = len(corpus)
        df = {}
        for doc in corpus:
            for term in set(doc):
                df[term] = df.get(term, 0) + 1

        idf = {}
        for term, freq in df.items():
            idf[term] = math.log(1 + (N - freq + 0.5) / (freq + 0.5))

        scores = [0.0] * N
        for i, doc in enumerate(corpus):
            dl = len(doc)
            for term in query:
                if term in doc:
                    tf = doc.count(term)
                    scores[i] += idf.get(term, 0) * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * dl / avg_dl))

        return scores


def load_context_manifest(path: str, repo_root: str = None) -> ContextManifest:
    with open(path, "r") as f:
        data = json.load(f)

    p = Path(path).resolve()

    if repo_root is None:
        # Walk upwards to find .git or Plan
        current = p.parent
        found = False
        while current != current.parent:
            if (current / ".git").exists() or (current / "Plan").exists():
                repo_root = str(current)
                found = True
                break
            current = current.parent
        if not found:
            try:
                repo_root = str(p.parents[5])
            except IndexError:
                repo_root = str(p.parent)

    manifest = ContextManifest.from_dict(data, repo_root=repo_root)
    manifest.validate_against_schema()
    return manifest
