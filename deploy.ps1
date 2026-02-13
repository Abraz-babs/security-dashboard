# CITADEL KEBBI - Deploy to Vercel
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   CITADEL KEBBI - Deploy to Vercel" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

$env:VITE_API_URL = "https://security-dashboard-production-6ffd.up.railway.app"

Write-Host "Building frontend..." -ForegroundColor Yellow
Set-Location frontend
npm run build

Write-Host ""
Write-Host "Deploying to Vercel..." -ForegroundColor Yellow
Write-Host "If this is your first time, you'll need to login to Vercel" -ForegroundColor Gray
npx vercel --prod

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "   Deployment Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
