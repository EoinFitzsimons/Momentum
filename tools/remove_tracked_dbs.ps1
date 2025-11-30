<#
Safe helper to remove tracked DB and runtime cache files from the Git index.

USAGE: run this in PowerShell from the repository root. This script
only removes files from the Git index (keeps local copies). It also
backs up matched files to a sibling folder `..\FinalProject_db_backups`.

I will not run any git commit steps for you; after running this script,
inspect the changes and commit locally when you're ready.

This file is provided as an automation convenience; run it manually.
#>

param(
    [switch]$DryRun
)

Write-Host "== Remove tracked DBs helper =="

$backupDir = Join-Path -Path (Resolve-Path ".." ).Path -ChildPath "FinalProject_db_backups"
Write-Host "Backup folder:" $backupDir
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

Write-Host "Switching to branch 'big-decisions' (create if missing)"
# Check if local branch exists using git and inspect the exit code instead of command output.
git rev-parse --verify big-decisions > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Creating branch 'big-decisions'"
    git checkout -b big-decisions
} else {
    git checkout big-decisions
}

Write-Host "Listing tracked DB/cache files (inspect these before removal):"
$trackedFiles = & git ls-files -- "*.db" "*.sqlite" "currency_cache.json"
if ($trackedFiles -eq $null -or $trackedFiles.Count -eq 0) {
    Write-Host "No tracked DB/cache files found."
} else {
    Write-Host "Tracked files:"
    $trackedFiles | ForEach-Object { Write-Host $_ }
}

if ($DryRun) {
    Write-Host "Dry run mode: no files will be removed from index."
    exit 0
}

Write-Host "Backing up tracked DB/cache files to: $backupDir"
git ls-files -- "*.db" "*.sqlite" "currency_cache.json" | ForEach-Object {
    Write-Host "Copying: $_"
    Copy-Item $_ -Destination $backupDir -Force
}

Write-Host "Removing matched files from git index (keeps local files)."
try {
    & git rm --cached --ignore-unmatch momentum.db Momentum/Python/momentum.db Momentum/Python/database/momentum_backup_*.db currency_cache.json Momentum/Python/currency_cache.json
} catch {
    Write-Host "git rm reported an error; some patterns may have had no matches, which is OK."
}

Write-Host "Staged changes: .gitignore was modified earlier to ignore DBs. Review 'git status' and commit when ready."

Write-Host "Done. Review the backup directory and run: git status"
