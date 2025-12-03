#!/usr/bin/env pwsh
# Local CI Check Script
# Run quality checks locally that are executed in GitHub Actions

param(
    [Parameter(Position=0)]
    [ValidateSet('black', 'flake8', 'mypy', 'pytest', 'all')]
    [string]$Check = 'all'
)

$ErrorActionPreference = 'Continue'

function Write-Header {
    param([string]$Message)
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host $Message -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "[PASS] $Message" -ForegroundColor Green
}

function Write-Error-Message {
    param([string]$Message)
    Write-Host "[FAIL] $Message" -ForegroundColor Red
}

function Run-Black {
    Write-Header "Black: Code Format Check"
    black --check src tests 2>&1 | Out-Host
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Black check passed"
        return $true
    } else {
        Write-Error-Message "Black check failed: Format issues found"
        Write-Host "To fix: black src tests" -ForegroundColor Yellow
        return $false
    }
}

function Run-Flake8 {
    Write-Header "Flake8: Code Style Check"
    flake8 src tests 2>&1 | Out-Host
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Flake8 check passed"
        return $true
    } else {
        Write-Error-Message "Flake8 check failed: Style violations found"
        return $false
    }
}

function Run-Mypy {
    Write-Header "Mypy: Type Check"
    mypy src 2>&1 | Out-Host
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Mypy check passed"
        return $true
    } else {
        Write-Error-Message "Mypy check failed: Type errors found"
        return $false
    }
}

function Run-Pytest {
    Write-Header "Pytest: Test Execution"
    pytest --cov=src/serdevmock --cov-report=xml --cov-report=term 2>&1 | Out-Host
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Pytest check passed"
        return $true
    } else {
        Write-Error-Message "Pytest check failed: Tests failed"
        return $false
    }
}

# Main execution
$results = @{}

switch ($Check) {
    'black' {
        $results['black'] = Run-Black
    }
    'flake8' {
        $results['flake8'] = Run-Flake8
    }
    'mypy' {
        $results['mypy'] = Run-Mypy
    }
    'pytest' {
        $results['pytest'] = Run-Pytest
    }
    'all' {
        $results['black'] = Run-Black
        $results['flake8'] = Run-Flake8
        $results['mypy'] = Run-Mypy
        $results['pytest'] = Run-Pytest
    }
}

# Results summary
Write-Header "Check Results Summary"
$allPassed = $true
foreach ($key in $results.Keys) {
    if ($results[$key]) {
        Write-Host "  [PASS] $key" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] $key" -ForegroundColor Red
        $allPassed = $false
    }
}

if ($allPassed) {
    Write-Host "`nAll checks passed!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`nSome checks failed" -ForegroundColor Red
    exit 1
}
