#!/usr/bin/env sh

set -eux

get_tar() {
  kubectl exec -n "$TARFETCH_NAMESPACE" "$TARFETCH_RESOURCE_NAME" -- \
    tar -c -f - --atime-preserve=system --directory="$TARFETCH_SRC_DIR" "$TARFETCH_EXCLUDE" .
}

unpack() {
  tar -x -f - "$TARFETCH_VERBOSE" "$TARFETCH_KEEP_NEWER" --directory="$TARFETCH_TARGET_DIR"
}

get_tar | unpack

echo '[tarfetch] Done: Sync from container has finished.'
