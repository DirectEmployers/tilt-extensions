#!/bin/bash
# Run pip-compile inside of a Kubernetes container and output the results locally.
set -e

exec_path=$1
requirements=$2
dev_requirements=${3-false}

compile_in()
{
  exec_path=$1
  requirements_input=$2
  requirements_output=${requirements_input//.in/.txt}

  printf "Compiling ${requirements_input} -> ${requirements_output} ...\n"
  kubectl exec "${exec_path}" -- \
    pip-compile --generate-hashes "${requirements_input}"

  printf "Collect files locally...\n"
  kubectl exec "${exec_path}" -- \
    cat "${requirements_output}" > "${requirements_output}"
}

compile_in "${exec_path}" "${requirements}"
if dev_requirements:
  compile_in "${exec_path}" "${dev_requirements}"
