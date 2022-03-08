#!/bin/bash
# Run pip-compile inside of a Kubernetes container and output the results locally.
set -e

POSITIONAL_ARGS=()
while [[ $# -gt 0 ]]; do
  case $1 in
    --cache-dir)
      cache_dir="$2"
      shift
      shift
      ;;
    -v|--verbose)
      verbose=true
      shift
      ;;
    -q|--quiet)
      quiet=true
      shift
      ;;
    --generate-hashes)
      generate_hashes=true
      shift
      ;;
    -*|--*)
      echo "Unknown option $1"
      exit 1
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
  shift
  inputs=("$@")

  for input in "${inputs[@]}"; do
    input_name=$(basename $input)
    output_name="${input_name//.in/.txt}"
    echo
    echo "Compiling ${input_name} → ${output_name}..."
    kubectl exec "${exec_path}" -- pip-compile "${input}"
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

compile_in "${exec_path}" ${requirements[@]}
collect_txt "${exec_path}" "${destination}" ${requirements[@]}
echo
echo "Requirement compilation complete."
