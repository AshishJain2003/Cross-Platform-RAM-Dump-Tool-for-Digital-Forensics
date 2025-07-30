@echo off
:: Set the working directory to where NON_GUI.exe is located
cd /d "E:\RAM Dumper\Autorun"

:: Log output to capture any errors
start "" "NON_GUI.exe" > output.log 2>&1

:: Check if running as administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting administrator privileges...
    powershell -Command "Start-Process 'NON_GUI.exe' -Verb RunAs"
    exit /b
)

:: If running as administrator, execute NON_GUI.exe
start "" "NON_GUI.exe"
