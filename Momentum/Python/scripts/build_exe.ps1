param(
    [switch]$Clean = $true,
    [switch]$OneFolder = $true
)

$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir

Set-Location $projectRoot

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
    '--add-data', 'GUI/assets;GUI/assets'
    '--collect-all', 'PyQt6'
    '--exclude-module', 'PySide6'
    '--collect-all', 'matplotlib'
    '--paths', '.'
    'GUI/launcher.py'
)

if ($Clean) {
    $args = @('--clean') + $args
}

if ($OneFolder) {
    $args = @('--onedir') + $args
}

python -m PyInstaller @args
