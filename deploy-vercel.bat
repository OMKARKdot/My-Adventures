@echo off
REM My Adventures - Vercel Deployment Script (Windows)
REM This script helps deploy your website to Vercel

echo 🚀 My Adventures - Vercel Deployment Script
echo ==========================================
echo.

REM Check if Vercel CLI is installed
vercel --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Vercel CLI not found. Please install it first:
    echo    npm install -g vercel
    pause
    exit /b 1
)

REM Check if logged in to Vercel
vercel whoami >nul 2>&1
if %errorlevel% neq 0 (
    echo 🔐 Please log in to Vercel first:
    echo    vercel login
    pause
    exit /b 1
)

echo ✅ Vercel CLI is installed and you're logged in
echo.

REM Check for required files
echo 📋 Checking required files...
set missing_files=0

if exist "index.html" (
    echo    ✅ index.html
) else (
    echo    ❌ index.html
    set missing_files=1
)

if exist "vercel.json" (
    echo    ✅ vercel.json
) else (
    echo    ❌ vercel.json
    set missing_files=1
)

if exist "package.json" (
    echo    ✅ package.json
) else (
    echo    ❌ package.json
    set missing_files=1
)

if %missing_files%==1 (
    echo.
    echo ❌ Missing required files. Please ensure all required files are present before deploying.
    pause
    exit /b 1
)

echo.
echo 🔍 Validating configuration...

REM Check for HTML files
for /f %%A in ('dir /b *.html 2^>nul ^| find /c /v ""') do set html_files=%%A
echo    📄 Found %html_files% HTML files

REM Check for image files
for /f %%A in ('dir /b *.webp *.jpeg *.jpg *.png 2^>nul ^| find /c /v ""') do set image_files=%%A
echo    🖼️  Found %image_files% image files

echo.
echo 🚀 Starting deployment...
echo    Deploying to Vercel...

vercel --yes
if %errorlevel% neq 0 (
    echo    ❌ Deployment failed!
    pause
    exit /b 1
)

echo    ✅ Deployment successful!
echo.

set /p deploy_prod="🎯 Do you want to deploy to production? (y/N): "
if /i "%deploy_prod%"=="y" (
    echo    Deploying to production...
    vercel --prod --yes
    if %errorlevel% neq 0 (
        echo    ❌ Production deployment failed!
        pause
        exit /b 1
    )
    echo    ✅ Production deployment successful!
)

echo.
echo 🎉 Deployment completed successfully!
echo.
echo 📋 Next steps:
echo    1. Visit your deployed site (URL will be shown above)
echo    2. Test all pages and functionality
echo    3. Consider setting up a custom domain
echo    4. Add analytics if needed
echo    5. Monitor performance in Vercel Dashboard
echo.
echo 📚 For more information, see README-VERCEL.md
echo.
pause