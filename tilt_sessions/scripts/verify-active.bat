@echo off
setlocal

set "port=%~1"
if "%port%"=="" set "port=%TILT_PORT%"

tilt get sessions Tiltfile --ignore-not-found --output name --port %port%
if %errorlevel% equ 0 (
  echo true
)
