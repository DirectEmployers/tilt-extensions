#!/usr/bin/env sh

set -eu

PACK_ARGS="--directory=${TARFETCH_SRC_DIR}"
[ -n "$TARFETCH_EXCLUDE" ] && PACK_ARGS="${PACK_ARGS} ${TARFETCH_EXCLUDE}"

UNPACK_ARGS="--directory=${TARFETCH_TARGET_DIR}"
[ "$TARFETCH_KEEP_NEWER" = "true" ] && UNPACK_ARGS="${UNPACK_ARGS} --keep-newer-files"

if [ "$TARFETCH_VERBOSE" = "true" ]; then
  UNPACK_ARGS="${UNPACK_ARGS} --verbose"
  set -x
fi

pack() {
  kubectl exec -n "$TARFETCH_NAMESPACE" "$TARFETCH_RESOURCE_NAME" -- \
    tar -c -f - $PACK_ARGS .
}

unpack() {
  tar -x -f - $UNPACK_ARGS
}

pack | unpack

echo '[tarfetch] Done: Sync from container has finished.'
