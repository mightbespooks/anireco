@echo off

if exist "database.db" (
    echo Database found! Starting application...
) else (
    echo Creating a new database...
    py backend\database.py
)

start "Frontend Dev" cmd /k "cd /d "%~dp0" && npm run dev"

cd /d "%~dp0backend"
uvicorn routes:app --reload
pause
