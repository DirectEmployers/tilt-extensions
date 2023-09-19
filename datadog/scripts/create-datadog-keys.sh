#!/usr/bin/env sh
set -eu

datadog_keys_path="$1"

if [ -z "$DATADOG_API_KEY" ]; then
  echo "DATADOG_API_KEY cannot be empty!"
  exit 1
elif [ -z "$DATADOG_APP_KEY" ]; then
  echo "DATADOG_APP_KEY cannot be empty!"
  exit 1
fi

echo "Creating secrets file for Datadog"
mkdir -p "$(dirname $1)"
printf 'api-key=%s\napp-key=%s' "$DATADOG_API_KEY" "$DATADOG_APP_KEY" > "$datadog_keys_path"

echo "Enabling Datadog resources"
tilt enable --labels datadog

echo "Done"
