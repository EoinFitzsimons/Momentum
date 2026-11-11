<#
Install Momentum's Python dependencies from the repository root.

    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt -r requirements-dev.txt
#>
$repoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $repoRoot
python -m pip install --upgrade pip
python -m pip install -r requirements.txt -r requirements-dev.txt
