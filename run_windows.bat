@echo off
where python >nul 2>nul || (echo Python 3 is required.& pause & exit /b 1)
start "" http://127.0.0.1:8080
python server.py
