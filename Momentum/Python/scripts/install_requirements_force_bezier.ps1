# Backward-compatible script: kept so old commands still work.
# It simply forwards to install_requirements.ps1.

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$target = Join-Path $scriptDir "install_requirements.ps1"

if (Test-Path $target) {
	& $target
} else {
	Write-Host "install_requirements.ps1 not found."
	Write-Host "Run: python -m pip install --upgrade pip"
	Write-Host "Run: python -m pip install -r Momentum/Python/requirements.txt"
}