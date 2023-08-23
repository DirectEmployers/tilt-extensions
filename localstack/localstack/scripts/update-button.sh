#!/usr/bin/env sh
port=${1:-10350}
status=$(tilt get uiresources localstack --port "$port" --output jsonpath='{.status.disableStatus.state}')

icon="cloud_off"
if [ "$status" = "Enabled" ]; then
  icon="cloud"
fi

tilt patch uibutton localstack:toggle --port "$port" -p "{\"spec\": {\"iconName\": \"$icon\"}}"
