@echo off
echo ==========================================
echo   AI-NATIVE COPILOT RUNNER - HACKATHON
echo ==========================================
echo.
echo Starting FastAPI Backend...
start "FastAPI Backend" cmd /k "cd /d %~dp0backend && venv\Scripts\activate.bat && python main.py"
echo.
echo Starting Next.js Frontend...
start "Next.js Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"
echo.
echo ------------------------------------------
echo All services launched in separate windows!
echo Access Frontend at: http://localhost:3000/ai-copilot
echo Access Swagger API at: http://localhost:8000/docs
echo ==========================================
timeout /t 5
