@echo off
REM Double-click this file (it sits in the T.citybank\tools folder).
REM Downloads 1-minute bid data 2011-2025 for US500, GER40, WTI and XAGUSD from Dukascopy into T.citybank\data.
cd /d "%~dp0.."
python --version >nul 2>&1
if errorlevel 1 (
  echo Python is not installed or not on PATH. Install it from https://www.python.org/downloads/
  echo and tick "Add python.exe to PATH" on the first screen of the installer. Then double-click this file again.
  pause
  exit /b 1
)
python -m pip install --quiet numpy
python tools\dukascopy_m1.py --four 2011 2025
echo.
echo Next: upload the new US500_, GER40_, WTI_ and XAGUSD_ files from the data folder to GitHub (tools\DATA_HOWTO.md).
pause
