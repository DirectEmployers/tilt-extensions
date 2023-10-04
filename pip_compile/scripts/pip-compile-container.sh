#!/usr/bin/env bash

# Set unofficial strict-mode for bash 🔏
# Source: http://redsymbol.net/articles/unofficial-bash-strict-mode/ 👀
set -uo pipefail
IFS=$'\n\t'

# Docker Arguments
IMAGE_REF="$1"
IMAGE_CONTEXT="$2"
DOCKERFILE="$3"
IMAGE_TARGET="$4"
BUILD_TAG="$IMAGE_REF:build"

# Requirements Paths
LOCAL_REQ_PATH="$5"
REQ_MOUNT_PATH="/.pip-requirements/mount/"

# Script Paths
LOCAL_SCRIPT_PATH=$(dirname "$0")
REQ_SCRIPT_PATH="/.pip-requirements/scripts/"

COMPILE_ARGS="$6"

# Build image.
echo "Please wait: Building Docker image..."
docker build --quiet \
  --tag "$BUILD_TAG" \
  --target "$IMAGE_TARGET" \
  --cache-from "$IMAGE_REF" \
  --file "$DOCKERFILE" "$IMAGE_CONTEXT"

# Compile pip requirements.
echo "Please wait: Compiling pip requirements with pip-tools..."
docker run -i --rm \
  --user 0 \
  --name "pip-compile-$IMAGE_REF" \
  --volume "$LOCAL_REQ_PATH:$REQ_MOUNT_PATH:rw" \
  --volume "$LOCAL_SCRIPT_PATH:$REQ_SCRIPT_PATH:ro" \
  --entrypoint "$REQ_SCRIPT_PATH/entrypoint.sh $COMPILE_ARGS" \
  "$BUILD_TAG"

echo
echo "Done: Pip requirements have been compiled!"
echo
