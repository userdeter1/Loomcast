import json
import pytest
from pathlib import Path

from loomcast.adapters.catalog.static import StaticCatalog
from loomcast.common.exceptions import LoomcastError
from loomcast.ports.catalog import CatalogPort


def test_static_catalog_protocol_compliance():
    """Verify that StaticCatalog implements CatalogPort protocol."""
    catalog = StaticCatalog()
    assert isinstance(catalog, CatalogPort)


def test_static_catalog_search_code_query():
    """Test searching for 'code' returns matching code models."""
    catalog = StaticCatalog()
    results = catalog.search("code")
    model_names = [entry.name for entry in results]

    assert "codellama" in model_names
    assert "deepseek-coder" in model_names


def test_static_catalog_search_case_insensitivity():
    """Test that search() is case-insensitive."""
    catalog = StaticCatalog()

    results_lower = catalog.search("mistral")
    results_upper = catalog.search("MISTRAL")
    results_mixed = catalog.search("MiStRaL")

    assert len(results_lower) > 0
    assert [e.name for e in results_lower] == [e.name for e in results_upper]
    assert [e.name for e in results_lower] == [e.name for e in results_mixed]


def test_static_catalog_get_entry_exact():
    """Test retrieving entry by exact name."""
    catalog = StaticCatalog()
    entry = catalog.get_entry("llama3")

    assert entry is not None
    assert entry.name == "llama3"
    assert entry.publisher == "meta"


def test_static_catalog_get_entry_absent():
    """Test retrieving a non-existent entry returns None."""
    catalog = StaticCatalog()
    assert catalog.get_entry("non_existent_model_xyz") is None


def test_static_catalog_invalid_json_validation(tmp_path: Path):
    """Test that invalid entry schema or corrupted JSON raises LoomcastError at initialization."""
    invalid_json_file = tmp_path / "bad_catalog.json"

    # Case 1: Invalid schema (missing name field)
    bad_data = [{"description": "Missing name field"}]
    invalid_json_file.write_text(json.dumps(bad_data), encoding="utf-8")

    with pytest.raises(LoomcastError):
        StaticCatalog(catalog_path=invalid_json_file)

    # Case 2: File not found
    with pytest.raises(LoomcastError):
        StaticCatalog(catalog_path=tmp_path / "non_existent.json")
