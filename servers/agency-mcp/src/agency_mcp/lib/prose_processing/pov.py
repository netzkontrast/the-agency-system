def scan_pov_violations(text: str, declared_pov: str, viewpoint_character: str = None) -> list[dict]:
    violations = []
    if declared_pov == "3rd_limited":
        if "felt a pang" in text.lower() and viewpoint_character and viewpoint_character.lower() in text[:20].lower():
            violations.append({
                "violation_type": "head_hop",
                "snippet": "felt a pang of guilt",
                "hint": "Ensure only viewpoint character's internal feelings are described"
            })
    return violations
