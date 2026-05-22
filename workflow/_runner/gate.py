import json
import importlib
from pathlib import Path
from typing import Dict, Any, Tuple
import yaml
from workflow._runner.envelope import PhaseStateEnvelope

def evaluate_gate(gate_yaml_path: Path, envelope: PhaseStateEnvelope) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Evaluates a gate YAML.
    Returns: (ok, message, emitted_edge_info)
    """
    with gate_yaml_path.open("r", encoding="utf-8") as f:
        gate = yaml.safe_load(f)

    evaluator = gate.get("evaluator", {})
    kind = evaluator.get("kind")
    args = evaluator.get("args", {})

    ok = False
    message = ""

    if kind == "callable":
        module_name = evaluator.get("module")
        callable_name = evaluator.get("callable")

        try:
            module = importlib.import_module(module_name)
            func = getattr(module, callable_name)
            result = func(envelope, args)

            if not isinstance(result, dict) or set(result.keys()) != {"ok", "message"}:
                return False, "evaluator return must be exactly {ok, message}", {}

            ok = result.get("ok", False)
            message = result.get("message", "")
        except Exception as e:
            return False, repr(e), {}

    elif kind == "manual":
        # manual gate is always blocked until resumed
        ok = False
        message = "Manual approval required"
    else:
        # schema, sql
        ok = False
        message = f"Evaluator kind {kind} not implemented"

    emitted_edge_info = {}
    if ok:
        on_success = gate.get("on_success", {})
        emit_edge = on_success.get("emit_edge")
        if emit_edge:
            emitted_edge_info = emit_edge
            emitted_edge_info["type"] = emit_edge.get("type", "SATISFIES_PHASE")

    return ok, message, emitted_edge_info
