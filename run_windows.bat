@echo off
where python >nul 2>nul || (echo Python 3 is required to use this launcher.& pause & exit /b 1)
start "" http://localhost:8080
python -m http.server 8080
