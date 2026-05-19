import pytest
import yaml
from pathlib import Path
from workflow._runner import evaluate_gate

def test_gate_evaluator_emits_edge_on_success(tmp_path):
    # Given a gate yaml
    gate_content = """
id: lyrics-reviewed
type: hard-blocking
blocks_phase: "03"
evaluator:
  kind: callable
  module: workflow._runner.evaluators.frontmatter_status
  callable: assert_status_equals
  args:
    expected: passed
on_success:
  emit_edge:
    type: SATISFIES_PHASE
    from: artefact
    to: phase:music/02
    target_ontology: workflow.phase
"""
    gate_path = tmp_path / "gate.yaml"
    gate_path.write_text(gate_content)

    env = {} # mock envelope

    # When evaluated
    ok, message, emitted_edge = evaluate_gate(gate_path, env)

    # Then it passes and emits
    assert ok is True
    assert emitted_edge["type"] == "SATISFIES_PHASE"
    assert emitted_edge["from"] == "artefact"
    assert emitted_edge["to"] == "phase:music/02"
