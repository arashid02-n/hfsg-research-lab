@echo off
setlocal
rem ============================================================
rem  HFSG Research Lab - one-click launcher (Windows)
rem
rem  Double-click this file. It runs the portable pre-flight
rem  checks (Python, dependencies, HFSG Core, disk, port) and
rem  then starts the Lab and opens your browser automatically.
rem ============================================================
cd /d "%~dp0"

rem ---- locate a Python interpreter ---------------------------
set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY (
    where python >nul 2>nul && set "PY=python"
)
if not defined PY (
    echo.
    echo Python was not found.
    echo.
    echo Install Python 3.10 or newer from https://www.python.org/downloads/
    echo and make sure "Add Python to PATH" is ticked during installation.
    echo Then double-click START_HFSG.bat again.
    echo.
    pause
    exit /b 1
)

rem ---- run the portable pre-flight launcher ------------------
%PY% "%~dp0scripts\launcher.py" %*
set "CODE=%ERRORLEVEL%"

if not "%CODE%"=="0" (
    echo.
    echo HFSG Research Lab did not start (exit code %CODE%).
    echo Review the message above.
    echo.
    pause
)

endlocal & exit /b %CODE%
