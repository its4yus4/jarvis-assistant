@echo off
echo Jarvis Assistant - Auto Setup
echo =============================
 
REM Create directories if they don't exist
if not exist logs mkdir logs
if not exist images mkdir images
if not exist examples mkdir examples

REM Create log file if it doesn't exist
if not exist logs\jarvis.log type nul > logs\jarvis.log

echo.
echo ✅ Setup complete!
echo.
echo Starting Jarvis...
echo.

python jarvis.py
pause
