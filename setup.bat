@echo off
echo Setting up MLB Scraper Environment...

REM Create virtual environment
echo Creating virtual environment...
python -m venv .venv

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt

echo.
echo Setup complete! Virtual environment created and dependencies installed.
echo To activate the environment manually, run: .venv\Scripts\activate.bat
echo To run the scraper, use: python mlb_scraper.py
echo.
pause