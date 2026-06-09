@echo off
setlocal EnableExtensions

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "APP_ROOT=%%~fI"

if exist "%SCRIPT_DIR%AudioLabEditor.exe" (
    start "" "%SCRIPT_DIR%AudioLabEditor.exe" %*
    exit /b 0
)

if exist "%APP_ROOT%\AudioLabEditor.exe" (
    start "" "%APP_ROOT%\AudioLabEditor.exe" %*
    exit /b 0
)

set "PYTHONPATH=%APP_ROOT%\src;%PYTHONPATH%"
python -m presentation.main %*
endlocal
