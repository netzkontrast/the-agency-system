from typing import Optional

import json
import logging
from pathlib import Path
from typing import Dict, Union, Any

import jsonschema

logger = logging.getLogger(__name__)

class NCPValidator:
    """
    Validates NCP documents against the schema.
    """
    def __init__(self):
        pass

    def _load_json_with_sha_header(self, path: Path) -> Any:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def validate(
        self,
        doc: Union[Dict[str, Any], str, Path],
        schema_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Validates the document.
        Returns {"ok": bool, "errors": list[str]}
        Raises only on unreadable file or malformed JSON, but never on validation failure.
        """
        if schema_path is None:
            schema_path = Path("state/schema/ncp.schema.json")

        schema = self._load_json_with_sha_header(schema_path)

        data = doc
        if isinstance(doc, (str, Path)):
            with open(doc, "r", encoding="utf-8") as f:
                data = json.load(f)

        errors = []
        try:
            jsonschema.validate(instance=data, schema=schema)
        except jsonschema.exceptions.ValidationError:
            # Gather all errors, not just the first one. Wait, jsonschema.validate raises on first error.
            # To get all, use Validator.iter_errors
            validator = jsonschema.Draft202012Validator(schema)
            for error in validator.iter_errors(data):
                errors.append(error.message)

        return {"ok": len(errors) == 0, "errors": errors}

def validate(
    doc: Union[Dict[str, Any], str, Path],
    schema_path: Union[Path, None] = None
) -> Dict[str, Any]:
    return NCPValidator().validate(doc, schema_path)
