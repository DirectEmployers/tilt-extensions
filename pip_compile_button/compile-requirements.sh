#!/bin/bash
# Run pip-compile inside of a Kubernetes container and output the results locally.
set -e

POSITIONAL_ARGS=()
COMPILE_ARGS=()

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

# Get local destination path for compiled requirements files.
destination=$2

# Shift previous two arguments and treat remaining as requirements file names.
shift
shift
requirements=$@

compile_in()
{
  # Compile a list of requirements.in files using kubectl.
  # Additional pip-compile arguments are passed in via $compile_args.

  exec_path=$1
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

  for input in "${inputs[@]}"; do
    # Get filename only.
    input_name=$(basename $input)

    # Update .in to .txt for compiled filename.
    output_name="${input_name//.in/.txt}"

    echo
    echo "Compiling ${input_name} → ${output_name}..."
    kubectl exec "${exec_path}" -- pip-compile ${compile_args[@]} "${input}"
  done
}

collect_txt()
{
  # Copy the contents of compiled requirements files back out
  # to local destination path ($compiled_dest).

  exec_path=$1
  compiled_dest=$2
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
    kubectl exec "${exec_path}" -- cat "${output}" > "${o_dest}"
  done
}

# Compile and then save results to local filesystem.
compile_in "${exec_path}" ${COMPILE_ARGS[@]} ${requirements[@]}
collect_txt "${exec_path}" "${destination}" ${requirements[@]}
echo
echo "Requirement compilation complete."
