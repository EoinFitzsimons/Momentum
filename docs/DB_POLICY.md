# Database Policy and Regeneration

Purpose
- Keep the repository free from binary database files and runtime caches. Store canonical schema and database generation scripts in `Momentum/Python/scripts/` so contributors can reproduce the DB locally.

Why we remove DB binaries
- Database files committed to git (e.g., `momentum.db`) bloat the repository, cause merge conflicts, and leak local state. They are not a reliable source of truth.

Policy
1. Do not commit runtime database files or caches. Add `*.db`, `*.sqlite`, `currency_cache.json` to `.gitignore`.
2. Keep a canonical schema and seeding script in `Momentum/Python/database/models.py` and `Momentum/Python/scripts/generate_initial_database.py`.
3. Store long-term backups outside the repository (shared storage, cloud, or an artifacts server).

Regeneration steps (developer)
1. Ensure you are on the working branch (for example `big-decisions`) and have a clean working tree:

```powershell
git checkout big-decisions
git status
```

2. Run the database generator to create a local `momentum.db` for development:

```powershell
cd Momentum/Python/scripts
python generate_initial_database.py --output ../momentum.db
```

3. If you need to preserve a local copy before removing tracked files, copy it to a safe location outside the repo:

```powershell
Copy-Item Momentum/Python/momentum.db -Destination C:\path\to\safe\backups\momentum_$(Get-Date -Format yyyyMMdd_HHmm).db
```

Removing tracked DBs from Git index (suggested command — run locally)

```powershell
# Back up tracked DBs first
New-Item -ItemType Directory -Path ..\FinalProject_db_backups -Force
git ls-files -- "*.db" | ForEach-Object { Copy-Item $_ -Destination ..\FinalProject_db_backups -Force }

# Remove from index (keeps local files)
git rm --cached --ignore-unmatch momentum.db Momentum/Python/momentum.db Momentum/Python/database/momentum_backup_*.db currency_cache.json Momentum/Python/currency_cache.json
git add .gitignore
git commit -m "chore: remove DB binaries and caches from repo; update .gitignore"
```

Notes about purging history
- If you must remove DBs from repository history (to shrink repo size), consider `git filter-repo` or BFG. These are destructive operations and rewrite history — coordinate with all collaborators.

Developer convenience
- A helper script `tools/remove_tracked_dbs.ps1` is provided to back up tracked DB files and remove them from the index. Run it locally and inspect results before committing.
