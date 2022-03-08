#!/bin/bash
# Run pip-compile inside of a Kubernetes container and output the results locally.
set -e

POSITIONAL_ARGS=()
COMPILE_ARGS=()

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

exec_path=$1
destination=$2
shift
shift
requirements=$@

compile_in()
{
  exec_path=$1
  compile_args=$2
  shift
  shift
  inputs=("$@")

  for input in "${inputs[@]}"; do
    input_name=$(basename $input)
    output_name="${input_name//.in/.txt}"
    echo
    echo "Compiling ${input_name} → ${output_name}..."
    kubectl exec "${exec_path}" -- pip-compile ${compile_args[@]} "${input}"
  done
}

collect_txt()
{
  exec_path=$1
  compiled_dest=$2
  shift
  shift
  inputs=("$@")

  for input in "${inputs[@]}"; do
    output=${input//.in/.txt}
    o_name=$(basename $output)
    o_dest="${compiled_dest}/${o_name}"
    echo
    echo "Collect ${o_name} file locally..."
    kubectl exec "${exec_path}" -- cat "${output}" > "${o_dest}"
  done
}

compile_in "${exec_path}" "${COMPILE_ARGS}" ${requirements[@]}
collect_txt "${exec_path}" "${destination}" ${requirements[@]}
echo
echo "Requirement compilation complete."
