#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path


VALID_VISIBILITY = {"visible", "hidden"}
VALID_DISTRIBUTION = {"active", "preview", "deprecated", "disabled"}


def read_env(name: str, default: str | None = None) -> str:
    value = os.environ.get(name)

    if value is None or value.strip() == "":
        if default is not None:
            return default
        raise RuntimeError(f"Missing env: {name}")

    return value.strip()


def load_manifest(path: Path) -> tuple[dict | list, list[dict]]:
    if not path.exists():
        data = []
        return data, data

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        return data, data

    if isinstance(data, dict):
        extensions = data.get("extensions")
        if extensions is None:
            extensions = []
            data["extensions"] = extensions

        if not isinstance(extensions, list):
            raise RuntimeError("manifest.json field 'extensions' must be a JSON array")

        return data, extensions

    raise RuntimeError("manifest.json must be a JSON array or an object with 'extensions' array")


def save_manifest(path: Path, data: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main() -> int:
    extension_id = read_env("EXTENSION_ID")
    loader_file = read_env("LOADER_FILE")
    source_dir = read_env("SOURCE_DIR")

    extension_name = read_env("EXTENSION_NAME")
    extension_version = read_env("EXTENSION_VERSION")
    extension_creator = read_env("EXTENSION_CREATOR")
    extension_description = read_env("EXTENSION_DESCRIPTION")

    rbz_name = read_env("RBZ_NAME")
    pages_base_url = read_env("PAGES_BASE_URL").rstrip("/")

    visibility = read_env("INPUT_VISIBILITY", "visible")
    distribution = read_env("INPUT_DISTRIBUTION", "active")
    category = read_env("INPUT_CATEGORY", "Etc")
    release_note = read_env(
        "INPUT_RELEASE_NOTE_URL",
        f"{extension_name} {extension_version}",
    )

    if visibility not in VALID_VISIBILITY:
        raise RuntimeError(f"Invalid visibility: {visibility}")

    if distribution not in VALID_DISTRIBUTION:
        raise RuntimeError(f"Invalid distribution: {distribution}")

    manifest_path = Path(read_env("MANIFEST_PATH", "deploy_repo/manifest.json"))

    download_url = (
        f"{pages_base_url}/rbz/{extension_id}/{rbz_name}"
    )

    manifest_data, extensions = load_manifest(manifest_path)

    existing = None
    for item in extensions:
        if item.get("id") == extension_id:
            existing = item
            break

    if existing is None:
        existing = {}
        extensions.append(existing)

    existing.update({
        "id": extension_id,
        "name": extension_name,
        "version": extension_version,
        "creator": extension_creator,
        "description": extension_description,
        "loader": loader_file,
        "source_dir": source_dir,
        "download_url": download_url,
        "release_note": release_note,
        "visibility": visibility,
        "distribution": distribution,
        "category": category,
    })

    extensions.sort(key=lambda item: item.get("id", ""))

    save_manifest(manifest_path, manifest_data)

    print("Updated manifest")
    print(f"- id: {extension_id}")
    print(f"- name: {extension_name}")
    print(f"- version: {extension_version}")
    print(f"- visibility: {visibility}")
    print(f"- distribution: {distribution}")
    print(f"- category: {category}")
    print(f"- download_url: {download_url}")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        raise SystemExit(1)
