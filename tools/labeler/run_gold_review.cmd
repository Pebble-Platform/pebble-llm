@echo off
setlocal
set PORT=%~1
if not defined PORT set PORT=8001
set SCRIPT_DIR=%~dp0
for %%I in (%SCRIPT_DIR%..\..) do set REPO_ROOT=%%~fI
set PYTHON=%REPO_ROOT%\.venv-vnser\Scripts\python.exe
set SERVER=%REPO_ROOT%\tools\labeler\server.py
set DATA_ROOT=%REPO_ROOT%\data\vietnamese-ser\episodes
set GOLD_USERS=%DATA_ROOT%\gold-users.json
if not exist %PYTHON% exit /b 1
if not exist %DATA_ROOT%\ exit /b 1
if not exist %GOLD_USERS% exit /b 1
echo Gold review server: http://127.0.0.1:%PORT%/gold.html
echo Terminal khac chay: ngrok http %PORT%
cd /d %REPO_ROOT%
%PYTHON% %SERVER% --root %DATA_ROOT% --port %PORT% --no-local-admin --gold-users %GOLD_USERS%
