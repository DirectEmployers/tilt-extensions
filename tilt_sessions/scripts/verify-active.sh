#!/usr/bin/env sh
set -u

port=${1-$TILT_PORT}
if tilt get sessions Tiltfile --ignore-not-found --output name --port "$port"; then
  echo "true"
fi
