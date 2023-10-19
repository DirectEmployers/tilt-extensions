#!/usr/bin/env bash
set -eu

cleanup() {
  find ./files -type f -name '*.do' -delete
  find ./files -type f -name '*.dont' -delete
}

cd "$(dirname "$0")"

echo "Preparing sync destination..."
if [ -d ./files ]; then
  cleanup
else
  mkdir ./files
fi

tilt ci
tilt down

echo "Cleaning up test files..."
cleanup
rm -r ./files

echo "Done"
