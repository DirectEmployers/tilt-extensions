#!/bin/bash
# Run pip-compile inside of a Kubernetes container and output the results locally.
set -e

exec_path=$1
requirements=$2
dev_requirements=${3-""}

compile_in()
{
  exec_path=$1
  input=$2
  output=${input//.in/.txt}

  echo "Compiling ${input}→${output}..."
  kubectl exec "${exec_path}" -- pip-compile --quiet "${input}"
}

collect_txt()
{
  exec_path=$1
  input=$2
  output=${input//.in/.txt}

  echo "Collect ${output} file locally..."
  kubectl exec "${exec_path}" -- cat "${output}" > "${output}"
}

compile_in "${exec_path}" "${requirements}"
if [[ $dev_requirements != "" ]]; then
  compile_in "${exec_path}" "${dev_requirements}"
fi

echo
collect_txt "${exec_path}" "${requirements}"
if [[ $dev_requirements != "" ]]; then
  collect_txt "${exec_path}" "${dev_requirements}"
fi

echo
echo "Requirement compilation complete."
