import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class DramaticaNavigator:
    """
    Navigator for the Dramatica narrative ontology.
    """

    def __init__(
        self,
        ontology_path: Optional[Path] = None,
        scenarios_path: Optional[Path] = None,
    ):
        self._ontology_path = ontology_path or Path("reference/novel/dramatica/ontology.json")
        self._scenarios_path = scenarios_path or Path("reference/novel/dramatica/scenarios.json")
        self._ontology_data: Optional[Dict[str, Any]] = None
        self._scenarios_data: Optional[List[Dict[str, Any]]] = None

    def _load_json_with_sha_header(self, path: Path) -> Any:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_ontology(self) -> List[Dict[str, Any]]:
        self._ensure_loaded()
        return list(self._ontology_data.values())

    def _ensure_loaded(self) -> None:
        if self._ontology_data is None:
            raw_ontology = self._load_json_with_sha_header(self._ontology_path)
            entries = raw_ontology.get("entries", []) if isinstance(raw_ontology, dict) else raw_ontology
            self._ontology_data = {entry["id"]: entry for entry in entries}

        if self._scenarios_data is None:
            raw_scenarios = self._load_json_with_sha_header(self._scenarios_path)
            if isinstance(raw_scenarios, dict) and "scenarios" in raw_scenarios:
                self._scenarios_data = raw_scenarios["scenarios"]
            elif isinstance(raw_scenarios, list):
                self._scenarios_data = raw_scenarios
            else:
                self._scenarios_data = []

    def by_id(self, entry_id: str) -> Optional[Dict[str, Any]]:
        self._ensure_loaded()
        return self._ontology_data.get(entry_id)

    def _by_kind(self, kind: str, name: str) -> List[Dict[str, Any]]:
        self._ensure_loaded()
        name_lower = name.lower()
        return [
            entry for entry in self._ontology_data.values()
            if entry.get("kind") == kind and entry.get("canonical_label", "").lower() == name_lower
        ]

    def by_class(self, name: str) -> List[Dict[str, Any]]:
        return self._by_kind("class", name)

    def by_type(self, name: str) -> List[Dict[str, Any]]:
        return self._by_kind("type", name)

    def by_variation(self, name: str) -> List[Dict[str, Any]]:
        return self._by_kind("variation", name)

    def by_element(self, name: str) -> List[Dict[str, Any]]:
        return self._by_kind("element", name)

    def by_dynamic_pair(self, a: str, b: str) -> Dict[str, Any]:
        """
        Returns {ok, a_entry, b_entry, reason?}
        a and b are IDs.
        """
        self._ensure_loaded()
        a_entry = self.by_id(a)
        b_entry = self.by_id(b)

        if not a_entry:
            return {"ok": False, "a_entry": None, "b_entry": b_entry, "reason": f"Entry '{a}' not found"}
        if not b_entry:
            return {"ok": False, "a_entry": a_entry, "b_entry": None, "reason": f"Entry '{b}' not found"}

        return {"ok": True, "a_entry": a_entry, "b_entry": b_entry}

    def check_dynamic_pair_reciprocity(self, pair: Dict[str, str]) -> Dict[str, Any]:
        """
        Returns {ok: bool, reason?: str}
        Uses the ontology's dynamic_pair field of each entry.
        """
        a = pair.get("a")
        b = pair.get("b")

        if not a or not b:
            return {"ok": False, "reason": "Both 'a' and 'b' must be provided."}

        res = self.by_dynamic_pair(a, b)
        if not res["ok"]:
            return {"ok": False, "reason": res["reason"]}

        a_entry = res["a_entry"]
        b_entry = res["b_entry"]

        a_pair = a_entry.get("dynamic_pair_id") or a_entry.get("dynamic_pair")
        b_pair = b_entry.get("dynamic_pair_id") or b_entry.get("dynamic_pair")

        if a_pair != b:
            return {"ok": False, "reason": f"'{a}' pairs with '{a_pair}', not '{b}'"}

        if b_pair != a:
            return {"ok": False, "reason": f"'{b}' pairs with '{b_pair}', not '{a}'"}

        return {"ok": True}

    def scenarios(self) -> List[Dict[str, Any]]:
        self._ensure_loaded()
        return self._scenarios_data
