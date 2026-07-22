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


def test_catalog_json_included_in_package_resources():
    """
    REGRESSION TEST (Bug fixed in version 0.1.1):
    In version 0.1.0 published on PyPI, `adapters/catalog/data/catalog.json` was missing from
    the built wheel and sdist distributions because `include-package-data = true`,
    `[tool.setuptools.package-data]`, and `MANIFEST.in` were missing from packaging configs.
    This rendered almost all loomcast commands unusable after a standard `pip install`.

    DO NOT DELETE THIS TEST: This test ensures that `catalog.json` is registered and accessible
    as a Python package resource via `importlib.resources`, guaranteeing it will be bundled
    and accessible when installed from PyPI.
    """
    import importlib.resources

    try:
        catalog_resource = importlib.resources.files("loomcast.adapters.catalog").joinpath("data", "catalog.json")
        assert catalog_resource.is_file(), "catalog.json missing from package resources"
    except AttributeError:
        assert importlib.resources.is_resource("loomcast.adapters.catalog.data", "catalog.json")

