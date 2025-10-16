# SAP ME/MII Folder Analyzer - Example Run Script
# This script demonstrates how to run the analyzer on the example test data

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SAP ME/MII Folder Analyzer - Example Run" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found!" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://www.python.org/downloads/" -ForegroundColor Red
    Write-Host "Or see INSTALLATION.md for detailed instructions" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Check if dependencies are installed
Write-Host "Checking dependencies..." -ForegroundColor Yellow
$missingDeps = @()

$requiredPackages = @("javalang", "lxml", "networkx", "pydantic", "click", "rich")

foreach ($package in $requiredPackages) {
    $installed = python -c "import $package" 2>&1
    if ($LASTEXITCODE -ne 0) {
        $missingDeps += $package
    }
}

if ($missingDeps.Count -gt 0) {
    Write-Host "✗ Missing dependencies: $($missingDeps -join ', ')" -ForegroundColor Red
    Write-Host ""
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Failed to install dependencies!" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ Dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "✓ All dependencies are installed" -ForegroundColor Green
}

Write-Host ""

# Run the analyzer on example test data
Write-Host "Running analyzer on example test data..." -ForegroundColor Yellow
Write-Host ""

python me_mii_folder_analyzer.py --root ./example_test --out ./example_output

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "✓ Analysis completed successfully!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Output files created in ./example_output/:" -ForegroundColor Cyan
    Write-Host "  - SUMMARY.md      (Architecture overview)" -ForegroundColor White
    Write-Host "  - TRAINING.md     (Training document)" -ForegroundColor White
    Write-Host "  - graph.mmd       (Mermaid diagram)" -ForegroundColor White
    Write-Host "  - graph.json      (Relationship data)" -ForegroundColor White
    Write-Host ""
    Write-Host "View the results:" -ForegroundColor Yellow
    Write-Host "  type example_output\SUMMARY.md" -ForegroundColor White
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Review the output files" -ForegroundColor White
    Write-Host "  2. Try with your own project:" -ForegroundColor White
    Write-Host "     python me_mii_folder_analyzer.py --root 'D:\YourProject' --out ./output" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "✗ Analysis failed!" -ForegroundColor Red
    Write-Host "Please check the error messages above" -ForegroundColor Yellow
    exit 1
}
