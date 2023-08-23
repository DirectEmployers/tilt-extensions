#!/usr/bin/env sh
port=${1:-10350}

tilt disable localstack --port "$port"
tilt wait --for=delete uiresource/localstack --port "$port" --timeout 10s

kubectl delete pvc localstack
tilt trigger localstack-storage --port "$port"
tilt wait --for=condition=Ready uiresource/localstack-storage --port "$port" --timeout 10s

tilt enable localstack --port "$port"
