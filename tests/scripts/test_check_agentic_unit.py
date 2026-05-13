from scripts.check_agentic_unit import discover_unit_files, main, validate_text


VALID_UNIT = """
unit_id: example-unit-2026-05-13
surface: docs
goal: Prove the validator accepts a complete unit.
current_state: A markdown unit has all required fields.
authority_boundary: Test data only.
verification_criteria: The validator returns no errors.
log_location: tests/scripts/test_check_agentic_unit.py
completion_condition: All required fields are accepted.
contract_category: runtime-contract
status: verified
"""


def test_accepts_complete_unit_record():
    assert validate_text(VALID_UNIT) == []


def test_rejects_missing_required_field():
    text = VALID_UNIT.replace("authority_boundary: Test data only.\n", "")

    assert "missing required field: authority_boundary" in validate_text(text)


def test_rejects_empty_required_field():
    text = VALID_UNIT.replace(
        "verification_criteria: The validator returns no errors.",
        "verification_criteria:",
    )

    assert "empty required field: verification_criteria" in validate_text(text)


def test_rejects_unknown_status():
    text = VALID_UNIT.replace("status: verified", "status: maybe")

    errors = validate_text(text)

    assert "invalid status: maybe" in errors[0]


def test_rejects_unknown_surface():
    text = VALID_UNIT.replace("surface: docs", "surface: unknown")

    errors = validate_text(text)

    assert "invalid surface: unknown" in errors[0]


def test_rejects_unknown_contract_category():
    text = VALID_UNIT.replace(
        "contract_category: runtime-contract",
        "contract_category: vibes",
    )

    errors = validate_text(text)

    assert "invalid contract_category: vibes" in errors[0]


def test_rejects_non_ascii_unit_id():
    text = VALID_UNIT.replace(
        "unit_id: example-unit-2026-05-13",
        "unit_id: 예시-unit",
    )

    assert (
        "invalid unit_id: use lowercase ASCII letters, digits, and hyphens"
        in validate_text(text)
    )


def test_discovers_only_markdown_files_with_unit_id(tmp_path):
    unit = tmp_path / "unit.md"
    unit.write_text(VALID_UNIT, encoding="utf-8")
    non_unit = tmp_path / "ordinary.md"
    non_unit.write_text("# Ordinary Plan\n\nNo unit record here.\n", encoding="utf-8")
    nested = tmp_path / "nested"
    nested.mkdir()
    nested_unit = nested / "nested-unit.md"
    nested_unit.write_text(VALID_UNIT, encoding="utf-8")

    assert set(discover_unit_files([tmp_path])) == {unit, nested_unit}


def test_discovery_does_not_treat_empty_unit_id_as_concrete(tmp_path):
    template = tmp_path / "template.md"
    template.write_text(
        "unit_id:\nsurface: docs\nstatus: planned\n",
        encoding="utf-8",
    )

    assert discover_unit_files([tmp_path]) == []


def test_discover_mode_rejects_missing_path(tmp_path):
    assert main(["--discover", str(tmp_path / "missing")]) == 1
