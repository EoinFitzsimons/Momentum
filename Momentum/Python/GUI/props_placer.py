"""Simple procedural props placer for infield: deterministic seeded placement.

Provides a small API to compute a list of props (x,y,type,size) given an
infield polygon and seed, and a draw helper to render simple primitives.
This is intentionally lightweight: sprites or atlas-based rendering can be
added later.
"""
import random
import math
from typing import List, Dict, Tuple
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QPixmap
from PyQt6.QtCore import Qt
from pathlib import Path
from typing import Optional

# Try to load sprite assets from GUI/assets/props. Sprites should be named
# with a prefix indicating type, e.g. 'tree_oak.png', 'bush_1.png'. If none
# found, the module will fall back to vector drawing.
_ASSETS_DIR = Path(__file__).resolve().parents[0] / 'assets' / 'props'
_SPRITE_INDEX: Dict[str, List[QPixmap]] = {}


def _load_sprites() -> None:
    try:
        if not _ASSETS_DIR.exists():
            return
        for p in sorted(_ASSETS_DIR.glob('*.png')):
            name = p.stem.lower()
            # type prefix up to first underscore or dash
            if '_' in name:
                typ = name.split('_', 1)[0]
            elif '-' in name:
                typ = name.split('-', 1)[0]
            else:
                typ = name
            pix = QPixmap(str(p))
            if pix and not pix.isNull():
                _SPRITE_INDEX.setdefault(typ, []).append(pix)
    except Exception:
        # non-fatal; assets are optional
        pass


# Load sprites at import time (optional)
_load_sprites()


def place_props(points: List[Tuple[float, float]], seed: int = 0, density: float = 0.0005, style: str = 'default') -> List[Dict]:
    """Place props inside polygon defined by `points` (list of (x,y)).

    density is props per pixel^2 of bounding box; this function returns a
    list of prop dicts with x,y,type,size.
    """
    if not points:
        return []
    # Compute bbox
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)
    w = max(2, maxx - minx)
    h = max(2, maxy - miny)
    area = w * h

    rnd = random.Random(seed or 0)
    count = max(0, int(area * density))
    props = []
    attempts = 0
    placed = 0
    # Simple point-in-polygon test
    def point_in_poly(x, y):
        inside = False
        j = len(points) - 1
        for i in range(len(points)):
            xi, yi = points[i]
            xj, yj = points[j]
            intersect = ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi)
            if intersect:
                inside = not inside
            j = i
        return inside

    max_attempts = count * 6 + 50
    while placed < count and attempts < max_attempts:
        attempts += 1
        rx = rnd.uniform(minx, maxx)
        ry = rnd.uniform(miny, maxy)
        if not point_in_poly(rx, ry):
            continue
        ptype = 'tree' if rnd.random() < 0.6 else 'bush'
        size = rnd.uniform(6.0, 18.0) if ptype == 'tree' else rnd.uniform(3.0, 8.0)
        props.append({'x': rx, 'y': ry, 'type': ptype, 'size': size})
        placed += 1

    return props


def draw_props(painter: QPainter, props: List[Dict], offset_x: float = 0.0, offset_y: float = 0.0):
    """Draw simple circular props on the provided QPainter. Painter is
    expected to be in world coordinates (no extra translation applied).
    offset_x/offset_y are used if props were computed in local bbox coords.
    """
    if not props:
        return
    painter.save()
    for prop in props:
        x = prop['x'] - offset_x
        y = prop['y'] - offset_y
        size = prop.get('size', 8.0)
        # deterministic integer seed from position
        rx = int(x * 1000)
        ry = int(y * 1000)
        rnd_seed = (rx * 73856093) ^ (ry * 19349663) & 0xffffffff
        # Lightweight deterministic jitter for rotation/scale
        # small deterministic jitter for natural variation (-15..+15 degrees)
        rot = (((rnd_seed % 100) / 100.0) - 0.5) * 30.0

        sprite_drawn = False
        if prop['type'] in _SPRITE_INDEX and _SPRITE_INDEX.get(prop['type']):
            # Choose sprite deterministically by position
            variants = _SPRITE_INDEX[prop['type']]
            idx = (int(x * 13) ^ int(y * 17)) % len(variants)
            sprite = variants[idx]
            if not sprite.isNull():
                sw = int(size * 1.2)
                sh = int(size * 1.2)
                painter.drawPixmap(int(x - sw/2), int(y - sh/2), sw, sh, sprite)
                sprite_drawn = True

        if sprite_drawn:
            continue

        if prop['type'] == 'tree':
            # Draw soft shadow
            painter.setBrush(QBrush(QColor(0, 0, 0, 60)))
            painter.setPen(Qt.PenStyle.NoPen)
            sh_w = int(size * 0.9)
            sh_h = int(size * 0.35)
            painter.drawEllipse(int(x - sh_w/2), int(y + size*0.15), sh_w, sh_h)

            # Trunk (small rectangle)
            trunk_w = max(1, int(size * 0.14))
            trunk_h = max(2, int(size * 0.28))
            painter.setBrush(QBrush(QColor(90, 55, 30)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(int(x - trunk_w/2), int(y - trunk_h/2), trunk_w, trunk_h)

            # Canopy: layered overlapping ellipses for organic shape
            painter.save()
            painter.translate(x, y - trunk_h/2)
            painter.rotate(rot)
            canopy_colors = [QColor(30, 90, 30, 230), QColor(48, 110, 48, 210), QColor(20, 70, 20, 200)]
            offsets = [(-0.25, 0.0), (0.2, -0.15), (0.4, 0.05)]
            for i, (ox, oy) in enumerate(offsets):
                col = canopy_colors[i % len(canopy_colors)]
                painter.setBrush(QBrush(col))
                rw = int(size * (0.9 - i * 0.15))
                rh = int(size * (0.6 - i * 0.12))
                painter.drawEllipse(int(ox * size - rw/2), int(oy * size - rh/2), rw, rh)
            painter.restore()

        else:
            # Bush: irregular blob using multiple small ellipses
            painter.setPen(Qt.PenStyle.NoPen)
            base_col = QColor(40, 80, 40, 220)
            painter.setBrush(QBrush(base_col))
            # main body
            painter.drawEllipse(int(x - size/2), int(y - size/2), int(size), int(size*0.7))
            # add a couple of overlapping darker lumps
            painter.setBrush(QBrush(QColor(30, 70, 30, 200)))
            painter.drawEllipse(int(x - size*0.35), int(y - size*0.6), int(size*0.5), int(size*0.45))
            painter.drawEllipse(int(x + size*0.05), int(y - size*0.55), int(size*0.45), int(size*0.4))

    painter.restore()
