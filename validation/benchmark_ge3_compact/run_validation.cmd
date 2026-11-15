@echo off
setlocal
wsl.exe -e bash -lc "cd /mnt/d/hkura/codedemo_v2 && .venv/bin/python validation/benchmark_ge3_compact/run_validation.py %*"
exit /b %ERRORLEVEL%
