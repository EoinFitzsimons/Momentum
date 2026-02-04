"""Idempotent importer for circuits_database.json -> tracks table.

Usage:
    python Momentum/Python/tools/import_circuits_idempotent.py

Behavior:
- For each circuit in `Momentum/Python/data/circuits_database.json`:
  - If a track with the same `name` and `country` exists, update its `geometry_json` and `primary_discipline`.
  - Otherwise insert a new row with `name`, `country`, `primary_discipline`, and `geometry_json`.
"""
import json
from pathlib import Path
import sys

repo_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(repo_root / 'Momentum' / 'Python'))

from database.database_manager import DatabaseManager


def load_json(path: Path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def upsert_tracks(json_path: Path):
    data = load_json(json_path)
    db = DatabaseManager()
    inserted = 0
    updated = 0
    with db.get_connection() as conn:
        for rec in data:
            name = rec.get('name') or ''
            country = rec.get('country') or ''
            primary = rec.get('primary_discipline') or rec.get('discipline') or 'SINGLE_SEATER'
            geom = json.dumps(rec, ensure_ascii=False)

            # find existing by name+country (case-insensitive)
            cur = conn.execute("SELECT id, geometry_json FROM tracks WHERE name = ? AND country = ? COLLATE NOCASE", (name, country)).fetchone()
            if cur:
                # update geometry_json and primary_discipline if different
                existing_geom = cur['geometry_json']
                if existing_geom != geom:
                    conn.execute("UPDATE tracks SET geometry_json = ?, primary_discipline = ? WHERE id = ?", (geom, primary, cur['id']))
                    updated += 1
            else:
                conn.execute("INSERT INTO tracks (name, country, primary_discipline, geometry_json) VALUES (?, ?, ?, ?)", (name, country, primary, geom))
                inserted += 1
        conn.commit()

    print(f"Imported circuits: inserted={inserted}, updated={updated}, total={len(data)}")


if __name__ == '__main__':
    repo_root = Path(__file__).resolve().parents[3]
    p = repo_root / 'Momentum' / 'Python' / 'data' / 'circuits_database.json'
    if not p.exists():
        print(f"circuits file not found: {p}")
        sys.exit(1)
    upsert_tracks(p)
