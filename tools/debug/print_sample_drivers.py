"""Print 20 sample drivers from the DB (most-recent first)."""

from __future__ import annotations

import sqlite3
from momentum.config import DATABASE_PATH


def main() -> None:
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        "SELECT id,name,nationality,name_locale,birth_date,speed,racecraft,consistency FROM drivers ORDER BY id DESC LIMIT 20"
    )
    rows = cur.fetchall()
    for r in rows:
        print(
            f"[{r['id']}] {r['name']} ({r['nationality']}) locale={r['name_locale']} dob={r['birth_date']} speed={r['speed']} racecraft={r['racecraft']} consistency={r['consistency']}"
        )


if __name__ == "__main__":
    main()
