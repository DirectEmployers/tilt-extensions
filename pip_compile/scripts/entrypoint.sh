#!/usr/bin/env sh
set -eux

BUILD_PATH="/.pip-requirements/build"
MOUNT_PATH="/.pip-requirements/mount"

diffcp() {
  # Copy files only when their contents have changed (prevents Tilt reload)
  cmp -s "$1" "$2" || cp "$1" "$2" && echo "No changes made to $1."
}

# Create and enter build directory
# (reduce pip-compile comments to filenames)
mkdir -p "$BUILD_PATH"
cd "$BUILD_PATH"

# Copy source files to build directory
cp $MOUNT_PATH/*.in ./
cp $MOUNT_PATH/*.txt ./

# Compile requirements
for filepath in "$BUILD_PATH"/*.in; do
  requirements=$(basename "$filepath")
  pip-compile --generate-hashes --allow-unsafe "$requirements"
done

set +x

# Copy compiled files back to the mounted host directory
for filepath in "$BUILD_PATH"/*.txt; do
  lockfile=$(basename "$filepath")
  diffcp "$filepath" "$MOUNT_PATH/$lockfile"
done
