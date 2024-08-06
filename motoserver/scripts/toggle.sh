#!/usr/bin/env sh
cd "$(dirname "$0")" || exit

port=${1:-10350}
status=$(tilt get uiresources motoserver --port "$port" --output jsonpath='{.status.disableStatus.state}')

if [ "$status" = "Enabled" ]; then
  tilt disable --port "$port" motoserver
else
  tilt enable --port "$port" motoserver
fi

sh update-button.sh "$port"
