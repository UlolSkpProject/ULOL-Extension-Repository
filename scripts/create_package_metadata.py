#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path


def read_env(name: str, default: str | None = None) -> str:
    value = os.environ.get(name, "").strip()
    if value:
        return value
    if default is not None:
        return default
    raise RuntimeError(f"Missing env: {name}")


def main() -> int:
    output_path = Path(read_env("PACKAGE_METADATA_PATH"))
    metadata = {
        "schema_version": 1,
        "id": read_env("EXTENSION_ID"),
        "name": read_env("EXTENSION_NAME"),
        "version": read_env("EXTENSION_VERSION"),
        "loader": read_env("LOADER_FILE"),
        "source_dir": read_env("SOURCE_DIR"),
        "description": read_env("EXTENSION_DESCRIPTION"),
        "category": read_env("EXTENSION_CATEGORY", "Etc"),
    }

    ruby_abi = read_env("RUBY_ABI", "")
    platform = read_env("PLATFORM", "")
    artifact_id = read_env("ARTIFACT_ID", "")
    if ruby_abi or platform or artifact_id:
        if not (ruby_abi and platform and artifact_id):
            raise RuntimeError(
                "RUBY_ABI, PLATFORM, and ARTIFACT_ID must be provided together"
            )
        metadata.update({
            "ruby_abi": ruby_abi,
            "platform": platform,
            "artifact_id": artifact_id,
        })

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(metadata, file, ensure_ascii=False, indent=2)
        file.write("\n")

    print(f"Created package metadata: {output_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
