#!/usr/bin/env bash
set -euo pipefail

: "${LOADER_FILE:?Missing env: LOADER_FILE}"
: "${EXTENSION_NAME:?Missing env: EXTENSION_NAME}"
: "${EXTENSION_VERSION:?Missing env: EXTENSION_VERSION}"

# SOURCE_DIR가 명시되지 않으면 loader_file에서 자동 추론
# ex) rm_helper.rb -> rm_helper
SOURCE_DIR="${SOURCE_DIR:-${LOADER_FILE%.rb}}"

if [ ! -f "$LOADER_FILE" ]; then
  echo "ERROR: Loader file not found: $LOADER_FILE" >&2
  exit 1
fi

if [ ! -d "$SOURCE_DIR" ]; then
  echo "ERROR: Source dir not found: $SOURCE_DIR" >&2
  exit 1
fi

RBZ_BASENAME="$(
  printf '%s' "$EXTENSION_NAME" \
    | tr ' ' '_' \
    | tr -cd '[:alnum:]_.-'
)"

RBZ_NAME="${RBZ_BASENAME}-${EXTENSION_VERSION}.rbz"

echo "SOURCE_DIR=$SOURCE_DIR"
echo "RBZ_BASENAME=$RBZ_BASENAME"
echo "RBZ_NAME=$RBZ_NAME"

rm -rf package
mkdir package

cp "$LOADER_FILE" package/
cp -r "$SOURCE_DIR" package/

(
  cd package
  zip -r "../$RBZ_NAME" .
)

rm -rf package

if [ ! -f "$RBZ_NAME" ]; then
  echo "ERROR: RBZ build failed: $RBZ_NAME" >&2
  exit 1
fi

if [ -n "${GITHUB_ENV:-}" ]; then
  {
    echo "SOURCE_DIR=$SOURCE_DIR"
    echo "RBZ_BASENAME=$RBZ_BASENAME"
    echo "RBZ_NAME=$RBZ_NAME"
  } >> "$GITHUB_ENV"
fi

ls -lh "$RBZ_NAME"