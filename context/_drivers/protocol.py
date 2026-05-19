from typing import Protocol, List, Any, Optional, Dict

class ArtefactDriver(Protocol):
    def get_bytes(self, artefact_node: Dict[str, Any]) -> bytes:
        ...

    def put_bytes(self, artefact_node: Dict[str, Any], payload: bytes) -> None:
        ...

    def list_changes(self, since_token: Optional[str] = None) -> List[Any]:
        ...

    def materialize_for_export(self, artefact_node: Dict[str, Any], target_format: str) -> Any:
        ...
