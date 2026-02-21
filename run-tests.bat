@echo off
REM Selenium Test Runner for My Adventures (Windows)
REM Usage: run-tests.bat [local|docker|compose]

setlocal EnableDelayedExpansion

set "MODE=%~1"
if "%MODE%"=="" set "MODE=compose"
set "BASE_URL=%~2"
if "%BASE_URL%"=="" set "BASE_URL=http://localhost:9090"

echo 🧪 My Adventures - Selenium Test Runner
echo ======================================
echo Mode: %MODE%
echo Base URL: %BASE_URL%
echo.

if "%MODE%"=="local" (
    echo 📦 Running tests locally...
    echo Installing dependencies...
    pip install -r requirements.txt -q
    if errorlevel 1 (
        echo ❌ Failed to install dependencies
        exit /b 1
    )
    echo Running tests...
    set "BASE_URL=%BASE_URL%"
    set "HEADLESS=false"
    python test.py
    if errorlevel 1 (
        echo ❌ Tests failed
        exit /b 1
    )
) else if "%MODE%"=="docker" (
    echo 🐳 Building Docker image...
    docker build -f Dockerfile.selenium -t my-adventures-selenium .
    if errorlevel 1 (
        echo ❌ Docker build failed
        exit /b 1
    )
    echo Running tests in Docker...
    docker run --network=host -e BASE_URL=%BASE_URL% -e HEADLESS=true my-adventures-selenium
    if errorlevel 1 (
        echo ❌ Tests failed
        exit /b 1
    )
) else (
    echo 🐳 Running with Docker Compose...
    echo This will start both the web server and test runner...
    echo.
    docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
    if errorlevel 1 (
        echo ❌ Tests failed
        docker-compose -f docker-compose.test.yml down
        exit /b 1
    )
    echo.
    echo Cleaning up...
    docker-compose -f docker-compose.test.yml down
)

echo.
echo ✅ Test run complete!
