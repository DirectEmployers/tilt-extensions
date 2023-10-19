#!/usr/bin/env bash
# Helper script to trigger a button.
# Source: https://github.com/tilt-dev/tilt-extensions/blob/dd9e9f70/cancel/test/trigger.sh
set -eu

YAML=$(tilt get uibutton "btn-tarfetch-tarfetch-example" -o yaml)
TIME=$(date '+%FT%T.000000Z')
NEW_YAML=$(echo "$YAML" | sed "s/lastClickedAt.*/lastClickedAt: $TIME/g")

# Currently, kubectl doesn't support subresource APIs.
# Follow this KEP:
# https://github.com/kubernetes/enhancements/issues/2590
# For now, we can handle it with curl.
curl -so /dev/null -X PUT -H "Content-Type: application/yaml" -d "$NEW_YAML" \
   "http://localhost:10350/proxy/apis/tilt.dev/v1alpha1/uibuttons/${1}/status"
