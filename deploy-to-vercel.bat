@echo off
echo ============================================
echo   CITADEL KEBBI - Deploy to Vercel
echo ============================================
echo.
echo This will deploy your frontend to Vercel.
echo.
echo You need:
echo 1. A Vercel account (free at vercel.com)
echo 2. Vercel CLI installed
echo.
echo Press any key to continue...
pause > nul

cd frontend

echo.
echo Setting environment variable...
set VITE_API_URL=https://security-dashboard-production-6ffd.up.railway.app

echo.
echo Building frontend...
call npm run build

echo.
echo Deploying to Vercel...
call npx vercel --prod

echo.
echo ============================================
echo   Deployment Complete!
echo ============================================
pause
