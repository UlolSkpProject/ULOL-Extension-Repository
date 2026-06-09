#!/usr/bin/env python3
import os
import re
import sys
from pathlib import Path


REQUIRED_KEYS = [
    "EXTENSION_NAME",
    "EXTENSION_VERSION",
    "EXTENSION_CREATOR",
    "EXTENSION_DESCRIPTION",
]


def read_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing env: {name}")
    return value


def extract_constant(text: str, key: str) -> str:
    patterns = [
        rf"{key}\s*=\s*['\"]([^'\"]+)['\"]",
        rf"{key}\s*=\s*%q\{{([^}}]+)\}}",
        rf"{key}\s*=\s*%Q\{{([^}}]+)\}}",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()

    raise RuntimeError(f"Missing Ruby constant: {key}")


def github_output(key: str, value: str) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")

    if not output_path:
        print(f"{key}={value}")
        return

    with open(output_path, "a", encoding="utf-8") as f:
        f.write(f"{key}={value}\n")


def main() -> int:
    loader_file = read_env("LOADER_FILE")
    loader_path = Path(loader_file)

    if not loader_path.exists():
        raise RuntimeError(f"Loader file not found: {loader_file}")

    text = loader_path.read_text(encoding="utf-8")

    values = {
        key: extract_constant(text, key)
        for key in REQUIRED_KEYS
    }

    github_output("name", values["EXTENSION_NAME"])
    github_output("version", values["EXTENSION_VERSION"])
    github_output("creator", values["EXTENSION_CREATOR"])
    github_output("description", values["EXTENSION_DESCRIPTION"])

    print("Extracted extension metadata")
    for key, value in values.items():
        print(f"- {key}: {value}")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        raise SystemExit(1)