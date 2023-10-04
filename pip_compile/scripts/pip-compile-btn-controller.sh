#!/usr/bin/env bash
#
# Start a controller that watches Tilt for new DockerImages, and adds new
# buttons to the appropriate Tilt UIResources.
#
# Inspired by: https://github.com/tilt-dev/tilt-extensions/blob/master/cancel/cancel_btn_controller.sh

# Ensure proper working directory
cd "$(dirname "$0")" || exit

# Set unofficial strict-mode for bash 🔏
# Source: http://redsymbol.net/articles/unofficial-bash-strict-mode/ 👀
set -euo pipefail
IFS=$'\n\t'

echo "🕵️‍♀️ ${1}:pip-compile:operator runs in the background and listens to Tilt"
echo "ℹ️ When there are resources with pip-compile, operator:pip-compile adds a 'pip-compile' button to the Tilt UI."
echo

# Currently, we only watch Cmds.
tilt get imagemaps --watch-only -o name | while read -r full_imagemap_name; do
    name=${full_imagemap_name#imagemap.tilt.dev/}
    if [[ "$name" == "$1" ]]; then
      python create-pip-compile-btn.py "$name"
    fi
done
