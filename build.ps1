# PowerShell script to build Whisk Automation Tool
Write-Host "🚀 Building Whisk Automation Tool..." -ForegroundColor Green
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found! Please install Python first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Install/upgrade required packages
Write-Host ""
Write-Host "📦 Installing required packages..." -ForegroundColor Yellow
pip install --upgrade pip
pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install packages!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Clean previous builds
Write-Host ""
Write-Host "🧹 Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }

# Run PyInstaller
Write-Host ""
Write-Host "🔧 Building executable..." -ForegroundColor Yellow
pyinstaller whisk_tool.spec

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "🎉 Build completed successfully!" -ForegroundColor Green
    
    # Check file size
    $exePath = "dist\WhiskAutomationTool_Fixed.exe"
    if (Test-Path $exePath) {
        $fileSize = (Get-Item $exePath).Length / 1MB
        Write-Host "📁 Executable: $exePath" -ForegroundColor Cyan
        Write-Host "📊 Size: $([math]::Round($fileSize, 1)) MB" -ForegroundColor Cyan
        
        # Copy additional files
        Copy-Item "prompts.txt" "dist\" -Force
        Copy-Item "ico_chuan.png" "dist\" -Force
        if (Test-Path "license.json") {
            Copy-Item "license.json" "dist\" -Force
        }
        Write-Host "📋 Additional files copied to dist folder" -ForegroundColor Green
    }
} else {
    Write-Host ""
    Write-Host "❌ Build failed!" -ForegroundColor Red
}

Write-Host ""
Read-Host "Press Enter to exit"
