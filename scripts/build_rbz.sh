#!/usr/bin/env bash
set -euo pipefail

: "${LOADER_FILE:?Missing env: LOADER_FILE}"
: "${EXTENSION_ID:?Missing env: EXTENSION_ID}"
: "${EXTENSION_NAME:?Missing env: EXTENSION_NAME}"
: "${EXTENSION_VERSION:?Missing env: EXTENSION_VERSION}"
: "${EXTENSION_DESCRIPTION:?Missing env: EXTENSION_DESCRIPTION}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# SOURCE_DIR가 명시되지 않으면 loader_file에서 자동 추론
# ex) rm_helper.rb -> rm_helper
SOURCE_DIR="${SOURCE_DIR:-${LOADER_FILE%.rb}}"
RUBY_ABI="${RUBY_ABI:-}"
NATIVE_ARTIFACT_DIR="${NATIVE_ARTIFACT_DIR:-}"

if [ ! -f "$LOADER_FILE" ]; then
  echo "ERROR: Loader file not found: $LOADER_FILE" >&2
  exit 1
fi

if [ ! -d "$SOURCE_DIR" ]; then
  echo "ERROR: Source dir not found: $SOURCE_DIR" >&2
  exit 1
fi

if [ -n "$RUBY_ABI" ] || [ -n "$NATIVE_ARTIFACT_DIR" ]; then
  : "${RUBY_ABI:?RUBY_ABI and NATIVE_ARTIFACT_DIR must be provided together}"
  : "${NATIVE_ARTIFACT_DIR:?RUBY_ABI and NATIVE_ARTIFACT_DIR must be provided together}"

  if [[ ! "$RUBY_ABI" =~ ^3\.(2|4)$ ]]; then
    echo "ERROR: Unsupported RUBY_ABI: $RUBY_ABI" >&2
    exit 1
  fi

  NATIVE_SOURCE_DIR="${NATIVE_ARTIFACT_DIR%/}/${SOURCE_DIR}/native"
  if [ ! -d "$NATIVE_SOURCE_DIR" ]; then
    echo "ERROR: Native artifact directory not found: $NATIVE_SOURCE_DIR" >&2
    exit 1
  fi

  SO_COUNT="$(find "$NATIVE_SOURCE_DIR" -type f -name '*.so' | wc -l | tr -d ' ')"
  if [ "$SO_COUNT" -eq 0 ]; then
    echo "ERROR: No .so files found in: $NATIVE_SOURCE_DIR" >&2
    exit 1
  fi
fi

RBZ_BASENAME="$(
  printf '%s' "$EXTENSION_NAME" \
    | tr ' ' '_' \
    | tr -cd '[:alnum:]_.-'
)"

if [ -n "$RUBY_ABI" ]; then
  RUBY_TAG="ruby${RUBY_ABI//./}"
  PLATFORM_TAG="win64"
  ARTIFACT_ID="${RUBY_TAG}-${PLATFORM_TAG}"
  RBZ_NAME="${RBZ_BASENAME}-${EXTENSION_VERSION}-${ARTIFACT_ID}.rbz"
else
  RUBY_TAG=""
  PLATFORM_TAG=""
  ARTIFACT_ID=""
  RBZ_NAME="${RBZ_BASENAME}-${EXTENSION_VERSION}.rbz"
fi

echo "SOURCE_DIR=$SOURCE_DIR"
echo "RBZ_BASENAME=$RBZ_BASENAME"
echo "RBZ_NAME=$RBZ_NAME"

rm -rf package
mkdir package

cp "$LOADER_FILE" package/
cp -r "$SOURCE_DIR" package/

if [ -n "$RUBY_ABI" ]; then
  rm -rf "package/${SOURCE_DIR}/native"
  mkdir -p "package/${SOURCE_DIR}/native"
  cp -r "$NATIVE_SOURCE_DIR"/. "package/${SOURCE_DIR}/native/"

  INVALID_NATIVE_FILE="$(find "package/${SOURCE_DIR}/native" -type f ! -name '*.so' -print -quit)"
  if [ -n "$INVALID_NATIVE_FILE" ]; then
    echo "ERROR: Native package contains a non-.so file: $INVALID_NATIVE_FILE" >&2
    exit 1
  fi
elif [ "${NATIVE_SO_ONLY:-false}" = "true" ] && [ -d "package/$SOURCE_DIR/native" ]; then
  find "package/$SOURCE_DIR/native" -type f ! -name '*.so' -delete
  find "package/$SOURCE_DIR/native" -type d -empty -delete
fi

SOURCE_DIR="$SOURCE_DIR" \
  PACKAGE_METADATA_PATH="package/seoul_space_package.json" \
  RUBY_ABI="$RUBY_ABI" \
  PLATFORM="$PLATFORM_TAG" \
  ARTIFACT_ID="$ARTIFACT_ID" \
  python3 "$SCRIPT_DIR/create_package_metadata.py"

(
  cd package
  if command -v zip >/dev/null 2>&1; then
    zip -r "../$RBZ_NAME" .
  elif command -v cmake >/dev/null 2>&1; then
    cmake -E tar cf "../$RBZ_NAME" --format=zip .
  else
    echo "ERROR: RBZ packaging requires zip or cmake." >&2
    exit 1
  fi
)

rm -rf package

if [ ! -f "$RBZ_NAME" ]; then
  echo "ERROR: RBZ build failed: $RBZ_NAME" >&2
  exit 1
fi

RBZ_SHA256="$(sha256sum "$RBZ_NAME" | awk '{print $1}')"

if [ -n "${GITHUB_ENV:-}" ]; then
  {
    echo "SOURCE_DIR=$SOURCE_DIR"
    echo "RBZ_BASENAME=$RBZ_BASENAME"
    echo "RBZ_NAME=$RBZ_NAME"
    echo "RBZ_SHA256=$RBZ_SHA256"
  } >> "$GITHUB_ENV"
fi

if [ -n "${GITHUB_OUTPUT:-}" ]; then
  {
    echo "source_dir=$SOURCE_DIR"
    echo "rbz_basename=$RBZ_BASENAME"
    echo "rbz_name=$RBZ_NAME"
    echo "rbz_sha256=$RBZ_SHA256"
    echo "ruby_abi=$RUBY_ABI"
    echo "platform=$PLATFORM_TAG"
    echo "artifact_id=$ARTIFACT_ID"
  } >> "$GITHUB_OUTPUT"
fi

ls -lh "$RBZ_NAME"
