#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")" || exit

status=$(tilt get uiresources datadog-agent --output jsonpath='{.status.disableStatus.state}')

if [ "$status" = "Enabled" ]; then
  tilt disable --labels datadog
else
  tilt enable --labels datadog
fi

sh update-button.sh
