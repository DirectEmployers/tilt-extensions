#!/usr/bin/env sh
cd "$(dirname "$0")" || exit

port=${1:-10350}
status=$(tilt get uiresources localstack --port "$port" --output jsonpath='{.status.disableStatus.state}')

if [ "$status" = "Enabled" ]; then
  tilt disable --port "$port" --labels localstack
else
  tilt enable --port "$port" --labels localstack
fi

sh update-button.sh "$port"
