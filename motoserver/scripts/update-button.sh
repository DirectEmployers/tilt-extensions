#!/usr/bin/env sh
port=${1:-10350}
status=$(tilt get uiresources motoserver --port "$port" --output jsonpath='{.status.disableStatus.state}')

icon="cloud_off"
if [ "$status" = "Enabled" ]; then
  icon="cloud"
fi

tilt patch uibutton motoserver:toggle --port "$port" -p "{\"spec\": {\"iconName\": \"$icon\"}}"
