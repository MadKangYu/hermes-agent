import importlib.util
import json
from pathlib import Path


def _load_script_module():
    path = Path(__file__).resolve().parents[2] / "scripts" / "build_model_catalog.py"
    spec = importlib.util.spec_from_file_location("build_model_catalog_script", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _catalog(*, updated_at: str, model_id: str = "openrouter/test-model") -> dict:
    return {
        "version": 1,
        "updated_at": updated_at,
        "metadata": {
            "source": "test",
            "docs": "https://example.test/docs/reference/model-catalog",
        },
        "providers": {
            "openrouter": {
                "metadata": {"display_name": "OpenRouter"},
                "models": [{"id": model_id, "description": "recommended"}],
            },
            "nous": {
                "metadata": {"display_name": "Nous Portal"},
                "models": [{"id": "nous/test-model"}],
            },
        },
    }


def test_check_mode_does_not_rewrite_catalog(tmp_path, monkeypatch, capsys):
    """--check is a no-write drift check; updated_at alone is not drift."""
    mod = _load_script_module()
    output = tmp_path / "model-catalog.json"
    current = _catalog(updated_at="2026-01-01T00:00:00Z")
    output.write_text(json.dumps(current, indent=2) + "\n", encoding="utf-8")
    before = output.read_text(encoding="utf-8")

    monkeypatch.setattr(mod, "OUTPUT_PATH", str(output))
    monkeypatch.setattr(
        mod,
        "build_catalog",
        lambda: _catalog(updated_at="2026-05-15T00:00:00Z"),
    )

    assert mod.main(["--check"]) == 0
    assert output.read_text(encoding="utf-8") == before
    assert "is up to date" in capsys.readouterr().out


def test_check_mode_fails_when_catalog_payload_is_stale(tmp_path, monkeypatch, capsys):
    """--check fails on provider/model drift and still leaves the file untouched."""
    mod = _load_script_module()
    output = tmp_path / "model-catalog.json"
    current = _catalog(updated_at="2026-01-01T00:00:00Z", model_id="openrouter/old")
    output.write_text(json.dumps(current, indent=2) + "\n", encoding="utf-8")
    before = output.read_text(encoding="utf-8")

    monkeypatch.setattr(mod, "OUTPUT_PATH", str(output))
    monkeypatch.setattr(
        mod,
        "build_catalog",
        lambda: _catalog(updated_at="2026-05-15T00:00:00Z", model_id="openrouter/new"),
    )

    assert mod.main(["--check"]) == 1
    assert output.read_text(encoding="utf-8") == before
    assert "is stale" in capsys.readouterr().err


def test_write_mode_updates_catalog(tmp_path, monkeypatch):
    mod = _load_script_module()
    output = tmp_path / "model-catalog.json"

    monkeypatch.setattr(mod, "OUTPUT_PATH", str(output))
    monkeypatch.setattr(
        mod,
        "build_catalog",
        lambda: _catalog(updated_at="2026-05-15T00:00:00Z", model_id="openrouter/new"),
    )

    assert mod.main([]) == 0
    assert json.loads(output.read_text(encoding="utf-8"))["providers"]["openrouter"]["models"] == [
        {"id": "openrouter/new", "description": "recommended"}
    ]
