@echo off
setlocal
cd /d "%~dp0"
echo Starting JobFit CV Studio...
echo.
python -m streamlit run app.py
echo.
echo App closed. Press any key to exit.
pause >nul

