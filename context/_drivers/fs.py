import os
from typing import List, Any, Optional, Dict
from .protocol import ArtefactDriver

class FSArtefactDriver(ArtefactDriver):
    def _get_path(self, artefact_node: Dict[str, Any]) -> str:
        # artefact_node is the node payload validated against artefact-node.schema.json
        path = artefact_node.get("artefact_path")
        if not path:
            raise ValueError("artefact_node missing 'artefact_path'")
        # Default to repo root if not absolute
        if not os.path.isabs(path):
            # Resolve relative to repo root. For simplicity, assume PWD is repo root
            path = os.path.abspath(path)
        return path

    def get_bytes(self, artefact_node: Dict[str, Any]) -> bytes:
        path = self._get_path(artefact_node)
        with open(path, "rb") as f:
            return f.read()

    def put_bytes(self, artefact_node: Dict[str, Any], payload: bytes) -> None:
        path = self._get_path(artefact_node)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(payload)

    def list_changes(self, since_token: Optional[str] = None) -> List[Any]:
        return []

    def materialize_for_export(self, artefact_node: Dict[str, Any], target_format: str) -> Any:
        # v0 stub
        return self.get_bytes(artefact_node)
