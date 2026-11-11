param(
    [switch]$Clean = $true,
    [switch]$OneFolder = $true
)

$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir   # packaging/ sits under the repository root

Set-Location $projectRoot

# Pre-clean: stop any running Momentum process and remove previous dist folder
try {
    Stop-Process -Name Momentum -ErrorAction SilentlyContinue -Force
} catch {
    # ignore
}

$distDir = Join-Path $projectRoot 'dist\Momentum'
if (Test-Path $distDir) {
    Write-Output "Removing existing dist folder: $distDir"
    $retries = 5
    for ($i = 0; $i -lt $retries; $i++) {
        try {
            Remove-Item -LiteralPath $distDir -Recurse -Force -ErrorAction Stop
            break
        } catch {
            Write-Output "Failed to remove dist folder (attempt $($i+1)/$retries). Retrying..."
            Start-Sleep -Seconds 1
        }
    }
}

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw 'Python is not available on PATH.'
}

$args = @(
    '--noconfirm'
    '--windowed'
    '--name', 'Momentum'
    '--distpath', 'dist'
    '--workpath', 'build'
    '--specpath', '.'
    '--add-data', 'momentum/gui/assets;momentum/gui/assets'
    '--add-data', 'momentum/database/momentum.db;momentum/database'
    '--collect-all', 'PyQt6'
    '--exclude-module', 'PySide6'
    '--collect-all', 'matplotlib'
    '--paths', '.'
    'momentum/gui/launcher.py'
)

if ($Clean) {
    $args = @('--clean') + $args
}

if ($OneFolder) {
    $args = @('--onedir') + $args
}

python -m PyInstaller @args
