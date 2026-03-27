<#
Run flake8 and mypy across the Momentum\Python code and log outputs.

Usage:
  # From repository root (PowerShell / pwsh)
  .\scripts\run_linters.ps1            # Run checks, require flake8/mypy already installed
  .\scripts\run_linters.ps1 -InstallMissing  # Install flake8/mypy via pip if missing

Logs are written to `logs/flake8_YYYYMMDD_HHMMSS.log` and `logs/mypy_YYYYMMDD_HHMMSS.log`.
#>
param(
    [switch]$InstallMissing
)

$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
$RepoRoot = Resolve-Path "$ScriptRoot\.." | Select-Object -ExpandProperty Path
$Target = Join-Path $RepoRoot "Momentum\Python"
$FlakeConfig = Join-Path $Target ".flake8"
$LogDir = Join-Path $RepoRoot "logs"
if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir | Out-Null }
$Timestamp = (Get-Date).ToString('yyyyMMdd_HHmmss')
$FlakeLog = Join-Path $LogDir "flake8_$Timestamp.log"
$MypyLog = Join-Path $LogDir "mypy_$Timestamp.log"

function Ensure-Tool {
    param(
        [string]$Name,
        [string]$InstallModuleName
    )
    $cmd = Get-Command $Name -ErrorAction SilentlyContinue
    if ($null -ne $cmd) { return $true }

    if ($InstallMissing) {
        Write-Host "Tool '$Name' not found. Installing via pip: $InstallModuleName"
        & python -m pip install $InstallModuleName
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "Failed to install $InstallModuleName. You may need to install it manually."
            return $false
        }
        # re-check
        $cmd = Get-Command $Name -ErrorAction SilentlyContinue
        return ($null -ne $cmd)
    } else {
        Write-Warning "Tool '$Name' not found. Rerun with -InstallMissing to auto-install."
        return $false
    }
}

Write-Host "Target directory: $Target"

$flakeAvailable = Ensure-Tool -Name flake8 -InstallModuleName flake8
$mypyAvailable = Ensure-Tool -Name mypy -InstallModuleName mypy

if (-not $flakeAvailable -and -not $mypyAvailable) {
    Write-Error "Neither flake8 nor mypy are available. Exiting."
    exit 2
}

# Run flake8 if available
if ($flakeAvailable) {
    Write-Host "Running flake8 on $Target ..."
    if (Test-Path $FlakeConfig) {
        Write-Host "Using flake8 config: $FlakeConfig"
        & flake8 --config $FlakeConfig $Target 2>&1 | Tee-Object -FilePath $FlakeLog
    }
    else {
        Write-Warning "No .flake8 found at $FlakeConfig; running with default flake8 settings."
        & flake8 $Target 2>&1 | Tee-Object -FilePath $FlakeLog
    }
    $flakeExit = $LASTEXITCODE
    Write-Host "flake8 exit code: $flakeExit — log: $FlakeLog"
} else {
    Write-Host "Skipping flake8 (not available)"
    $flakeExit = -1
}

# Run mypy if available
if ($mypyAvailable) {
    Write-Host "Running mypy on $Target ..."
    # Use --ignore-missing-imports for local project modules that may not have stubs
    & mypy $Target --ignore-missing-imports 2>&1 | Tee-Object -FilePath $MypyLog
    $mypyExit = $LASTEXITCODE
    Write-Host "mypy exit code: $mypyExit — log: $MypyLog"
} else {
    Write-Host "Skipping mypy (not available)"
    $mypyExit = -1
}

# Summary
Write-Host "--- Summary ---"
Write-Host "flake8: exit=$flakeExit, log=$FlakeLog"
Write-Host "mypy:  exit=$mypyExit, log=$MypyLog"

# Exit with non-zero if either tool reported errors (choose conservative behavior)
if ($flakeExit -ne 0 -and $flakeExit -ne -1) { exit $flakeExit }
if ($mypyExit -ne 0 -and $mypyExit -ne -1) { exit $mypyExit }
exit 0
