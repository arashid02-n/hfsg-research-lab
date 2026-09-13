@echo off
setlocal EnableExtensions
rem ============================================================
rem  HFSG Research Lab - one-click launcher (Windows)
rem
rem  Double-click this file. It:
rem    1. finds a base Python interpreter
rem    2. runs scripts\bootstrap.py, which creates a
rem       project-local .venv (if missing), installs the
rem       dependencies into it, and starts the Lab
rem    3. keeps this window open if anything fails so you can
rem       read the message
rem ============================================================
cd /d "%~dp0"

rem ---- locate a base Python (to bootstrap the local .venv) ----
set "BASE_PY="
where py >nul 2>nul
if not errorlevel 1 set "BASE_PY=py -3"
if not defined BASE_PY (
    where python >nul 2>nul
    if not errorlevel 1 set "BASE_PY=python"
)
if not defined BASE_PY (
    echo.
    echo ============================================================
    echo HFSG STARTUP FAILED
    echo.
    echo Reason: Python was not found.
    echo.
    echo Action: Install Python 3.10 or newer from
    echo         https://www.python.org/downloads/
    echo         and enable "Add Python to PATH", then restart HFSG.
    echo ============================================================
    echo.
    pause
    exit /b 1
)

rem ---- bootstrap .venv + dependencies + launch ----
%BASE_PY% "%~dp0scripts\bootstrap.py" %*
set "CODE=%ERRORLEVEL%"

if not "%CODE%"=="0" (
    echo.
    echo HFSG STARTUP FAILED - see the message above for the reason.
    echo.
    pause
)

endlocal & exit /b %CODE%
