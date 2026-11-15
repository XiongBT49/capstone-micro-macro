@echo off
setlocal
wsl.exe -e bash -lc "cd /mnt/d/hkura/codedemo_v2 && .venv/bin/python -m scripts.run_llm_micro_smoke %*"
exit /b %ERRORLEVEL%
