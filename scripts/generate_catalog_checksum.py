#!/usr/bin/env python3
"""Script to generate SHA-256 checksum file for embedded catalog.json."""

import hashlib
from pathlib import Path


def generate_checksum() -> Path:
    base_dir = Path(__file__).parent.parent
    catalog_path = (
        base_dir / "loomcast" / "adapters" / "catalog" / "data" / "catalog.json"
    )
    checksum_path = (
        base_dir / "loomcast" / "adapters" / "catalog" / "data" / "catalog.json.sha256"
    )

    if not catalog_path.is_file():
        raise FileNotFoundError(f"Catalog file not found at '{catalog_path}'")

    raw_bytes = catalog_path.read_bytes().replace(b"\r\n", b"\n")
    sha256_hash = hashlib.sha256(raw_bytes).hexdigest()

    checksum_path.write_text(f"{sha256_hash}\n", encoding="utf-8")
    print(f"Generated SHA-256 checksum for {catalog_path.name}: {sha256_hash}")
    return checksum_path


if __name__ == "__main__":
    generate_checksum()
