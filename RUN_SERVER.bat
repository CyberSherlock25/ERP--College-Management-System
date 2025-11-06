@echo off
REM ERP College Management System - Quick Start
REM This script will run the Django development server

color 0A
echo.
echo ╔════════════════════════════════════════════════╗
echo ║  ERP College Management System - Dev Server   ║
echo ╚════════════════════════════════════════════════╝
echo.

cd /d "E:\MIT\Python\ERP--College-Management-System\college_erp_system"

REM Check if migrations are needed
echo [1/4] Checking system...
py manage.py check
if errorlevel 1 (
    echo ERROR: System check failed!
    pause
    exit /b 1
)
echo ✓ System check passed!
echo.

REM Run migrations
echo [2/4] Applying migrations...
py manage.py migrate
if errorlevel 1 (
    echo ERROR: Migration failed!
    pause
    exit /b 1
)
echo ✓ Migrations applied!
echo.

REM Collect static files
echo [3/4] Collecting static files...
py manage.py collectstatic --noinput
if errorlevel 1 (
    echo ERROR: Static collection failed!
    pause
    exit /b 1
)
echo ✓ Static files collected!
echo.

REM Start server
echo [4/4] Starting server...
echo.
echo ════════════════════════════════════════════════
echo Server is starting...
echo ════════════════════════════════════════════════
echo.
echo Access the application at:
echo   http://127.0.0.1:8000
echo.
echo Admin panel at:
echo   http://127.0.0.1:8000/admin/
echo.
echo Teacher features:
echo   - Schedule Exams: /teachers/exams/
echo   - View Timetable: /teachers/timetable/
echo.
echo Press CTRL+C to stop the server
echo ════════════════════════════════════════════════
echo.

py manage.py runserver

REM If server stops
echo.
echo Server stopped.
pause
