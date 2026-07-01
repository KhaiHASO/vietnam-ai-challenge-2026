# Script to start both FastAPI Backend and Next.js Frontend easily on Windows

Write-Host "==========================================" -ForegroundColor Green
Write-Host "  AI-NATIVE COPILOT RUNNER - HACKATHON" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# 1. Start FastAPI Backend in a new window
Write-Host "Starting FastAPI Backend on http://localhost:8000..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; python -m venv venv; .\\venv\\Scripts\\Activate.ps1; pip install -r requirements.txt; python main.py" -WindowStyle Normal

# 2. Start Next.js Frontend in a new window
Write-Host "Starting Next.js Frontend on http://localhost:3000..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm install --legacy-peer-deps; npm run dev" -WindowStyle Normal

Write-Host "------------------------------------------" -ForegroundColor Yellow
Write-Host "Done! Backend and Frontend processes launched in new windows." -ForegroundColor Green
Write-Host "Access Frontend at: http://localhost:3000/ai-copilot" -ForegroundColor Green
Write-Host "Access Swagger API at: http://localhost:8000/docs" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
