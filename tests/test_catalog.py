import hashlib
import json
from pathlib import Path

import pytest

from loomcast.adapters.catalog.static import StaticCatalog
from loomcast.common.exceptions import CatalogIntegrityError, LoomcastError
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
    bad_bytes = json.dumps(bad_data).encode("utf-8")
    invalid_json_file.write_bytes(bad_bytes)

    # Write matching checksum so it passes integrity check but fails schema validation
    checksum_file = tmp_path / "bad_catalog.json.sha256"
    checksum_file.write_text(hashlib.sha256(bad_bytes).hexdigest(), encoding="utf-8")

    with pytest.raises(LoomcastError):
        StaticCatalog(catalog_path=invalid_json_file)

    # Case 2: File not found
    with pytest.raises(LoomcastError):
        StaticCatalog(catalog_path=tmp_path / "non_existent.json")


def test_static_catalog_checksum_mismatch(tmp_path: Path):
    """Test that StaticCatalog raises CatalogIntegrityError if catalog.json does not match catalog.json.sha256."""
    catalog_file = tmp_path / "catalog.json"
    checksum_file = tmp_path / "catalog.json.sha256"

    catalog_data = [
        {
            "name": "test-model",
            "publisher": "test",
            "tags": ["test"],
            "default_runtime": "ollama",
        }
    ]
    catalog_file.write_text(json.dumps(catalog_data), encoding="utf-8")

    # Write invalid / tampered checksum
    checksum_file.write_text("invalid_hash_1234567890abcdef", encoding="utf-8")

    with pytest.raises(CatalogIntegrityError) as exc_info:
        StaticCatalog(catalog_path=catalog_file)

    assert "Catalog integrity check failed" in str(exc_info.value)


def test_static_catalog_missing_checksum(tmp_path: Path):
    """Test that StaticCatalog raises CatalogIntegrityError if catalog.json.sha256 is missing."""
    catalog_file = tmp_path / "catalog.json"
    catalog_data = [
        {
            "name": "test-model",
            "publisher": "test",
            "tags": ["test"],
            "default_runtime": "ollama",
        }
    ]
    catalog_file.write_text(json.dumps(catalog_data), encoding="utf-8")

    with pytest.raises(CatalogIntegrityError) as exc_info:
        StaticCatalog(catalog_path=catalog_file)

    assert "Checksum file not found" in str(exc_info.value)


def test_static_catalog_valid_checksum(tmp_path: Path):
    """Test that StaticCatalog initializes successfully when checksum matches."""
    catalog_file = tmp_path / "catalog.json"
    checksum_file = tmp_path / "catalog.json.sha256"

    catalog_data = [
        {
            "name": "valid-model",
            "publisher": "test",
            "tags": ["test"],
            "default_runtime": "ollama",
        }
    ]
    content_bytes = json.dumps(catalog_data).encode("utf-8")
    catalog_file.write_bytes(content_bytes)

    valid_hash = hashlib.sha256(content_bytes).hexdigest()
    checksum_file.write_text(f"{valid_hash}\n", encoding="utf-8")

    catalog = StaticCatalog(catalog_path=catalog_file)
    assert catalog.get_entry("valid-model") is not None


def test_catalog_json_and_sha256_included_in_package_resources():
    """
    REGRESSION TEST:
    Ensure catalog.json and catalog.json.sha256 are bundled as package resources.
    """
    import importlib.resources

    try:
        catalog_resource = importlib.resources.files(
            "loomcast.adapters.catalog"
        ).joinpath("data", "catalog.json")
        checksum_resource = importlib.resources.files(
            "loomcast.adapters.catalog"
        ).joinpath("data", "catalog.json.sha256")
        assert catalog_resource.is_file(), "catalog.json missing from package resources"
        assert checksum_resource.is_file(), (
            "catalog.json.sha256 missing from package resources"
        )
    except AttributeError:
        assert importlib.resources.is_resource(
            "loomcast.adapters.catalog.data", "catalog.json"
        )
        assert importlib.resources.is_resource(
            "loomcast.adapters.catalog.data", "catalog.json.sha256"
        )
