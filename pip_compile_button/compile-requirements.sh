#!/bin/bash
# Run pip-compile inside of a Kubernetes container and output the results locally.
set -e

POSITIONAL_ARGS=()
COMPILE_ARGS=()
: "${PIP_UPLOADED_PRIOR_TO:=P5D}"
: "${PIP_COMPILE_VENV:=/tmp/pip-compile-button-venv}"
: "${PIP_VERSION:=26.1}"
: "${PIP_TOOLS_VERSION:=7.6.1}"

# Based on example from:
# https://stackoverflow.com/questions/192249/how-do-i-parse-command-line-arguments-in-bash
while [[ $# -gt 0 ]]; do
  case $1 in
    -*|--*)
      if [ -z "$2" ] || [[ $2 == -* ]]; then
        COMPILE_ARGS+=("$1")
        shift
      fi

      if [ ! -z "$2" ] && [[ $2 != -* ]]; then
        COMPILE_ARGS+=("$1=$2")
        shift
        shift
      fi
      ;;
    *)
      POSITIONAL_ARGS+=("$1")
      shift
      ;;
  esac
done

set -- "${POSITIONAL_ARGS[@]}"

# Get kubectl exec resource name or path.
exec_path=$1
container=$2

# Get local destination path for compiled requirements files.
destination=$3

# Shift previous two arguments and treat remaining as requirements file names.
shift
shift
shift
requirements=$@

compile_in()
{
  # Compile a list of requirements.in files using kubectl.
  # Additional pip-compile arguments are passed in via $compile_args.

  exec_path=$1
  container=$2
  shift
  shift

  compile_args=()
  inputs=()
  while [[ $# -gt 0 ]]; do
    case $1 in
      -*|--*)
        compile_args+=("$1")
        shift
        ;;
      *)
        inputs+=("$1")
        shift
        ;;
    esac
  done

  # Install pip-compile into a dedicated venv inside the container so the
  # application's own Python environment is never modified. The venv lives in
  # a writable location so this works for non-root images, and it is reused
  # across runs until the pod restarts.
  echo "Preparing pip-compile environment at ${PIP_COMPILE_VENV}..."
  if ! kubectl exec "${exec_path}" -c "${container}" -- sh -c '
    set -e
    venv="$1"
    if [ ! -x "${venv}/bin/pip-compile" ]; then
      python="$(command -v python3 || command -v python)"
      "${python}" -m venv "${venv}"
    fi
    "${venv}/bin/pip" install --quiet --upgrade "pip==$2"
    "${venv}/bin/pip" install --quiet --uploaded-prior-to "$4" --upgrade "pip-tools==$3"
  ' sh "${PIP_COMPILE_VENV}" "${PIP_VERSION}" "${PIP_TOOLS_VERSION}" "${PIP_UPLOADED_PRIOR_TO}"; then
    echo "Failed to prepare pip-compile environment in container '${container}'." >&2
    echo "The image must provide Python with the venv module and a writable ${PIP_COMPILE_VENV%/*}" >&2
    echo "(override the location with PIP_COMPILE_VENV)." >&2
    exit 1
  fi

  for input in "${inputs[@]}"; do
    # Get filename only.
    input_name=$(basename $input)

    # Update .in to .txt for compiled filename.
    output_name="${input_name//.in/.txt}"

    echo
    echo "Compiling ${input_name} → ${output_name}..."
    kubectl exec "${exec_path}" -c "${container}" -- "${PIP_COMPILE_VENV}/bin/pip-compile" --uploaded-prior-to="${PIP_UPLOADED_PRIOR_TO}" "${compile_args[@]}" "${input}"
  done
}

collect_txt()
{
  # Copy the contents of compiled requirements files back out
  # to local destination path ($compiled_dest).

  exec_path=$1
  container=$2
  compiled_dest=$3
  shift
  shift
  shift
  inputs=("$@")

  for input in "${inputs[@]}"; do
    # Update .in to .txt for compiled file path.
    output=${input//.in/.txt}

    # Get filename only.
    o_name=$(basename $output)

    # Construct compiled file output path.
    o_dest="${compiled_dest}/${o_name}"

    echo
    echo "Collect ${o_name} file locally..."
    kubectl exec "${exec_path}" -c "${container}" -- cat "${output}" > "${o_dest}"
  done
}

# Compile and then save results to local filesystem.
compile_in "${exec_path}" "${container}" ${COMPILE_ARGS[@]} ${requirements[@]}
collect_txt "${exec_path}" "${container}" "${destination}" ${requirements[@]}
echo
echo "Requirement compilation complete."
