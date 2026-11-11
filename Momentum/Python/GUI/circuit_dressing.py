"""Trackside dressing for the race view: pits, grandstands, gravel and run-off.

All geometry is derived once from the generated centreline and cached as
painter paths, so each frame only replays a handful of fills.
"""

from __future__ import annotations

import math
import random
from typing import Any, Callable, List, Optional, Sequence, Tuple

import numpy as np
from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QPainter,
    QPainterPath,
    QPen,
    QPicture,
    QPixmap,
    QPolygonF,
    QTransform,
)
from scipy.spatial import cKDTree

PIT_OFFSET = 36.0
PIT_HALF_WIDTH = 9.0
PIT_RAMP_FRACTION = 0.2
PIT_BOX_COUNT = 10
STRAIGHT_CURVATURE = 1e-3
TEAM_FALLBACK_COLOURS = [
    (6, 0, 239), (0, 210, 190), (220, 0, 0), (245, 150, 0), (0, 144, 255),
    (182, 186, 189), (53, 140, 117), (201, 45, 75), (255, 220, 0), (100, 100, 100),
]


def infield_side(points: Sequence[Any]) -> int:
    """Return +1 when the infield lies along the left normal (-sin, cos)."""
    xs = np.array([p.x for p in points])
    ys = np.array([p.y for p in points])
    area = 0.5 * float(np.sum(xs * np.roll(ys, -1) - np.roll(xs, -1) * ys))
    return 1 if area >= 0 else -1


def main_straight_window(points: Sequence[Any]) -> List[int]:
    """Indices of the straight running through the start line (wrapping)."""
    n = len(points)
    fwd = 0
    while fwd < n - 1 and abs(points[fwd].curvature) < STRAIGHT_CURVATURE:
        fwd += 1
    back = n - 1
    while back > fwd and abs(points[back].curvature) < STRAIGHT_CURVATURE:
        back -= 1
    return list(range(back + 1, n)) + list(range(0, fwd))


def _smoothstep(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def build_pit_route(points: Sequence[Any], offset: float = PIT_OFFSET) -> Optional[list]:
    """Pit lane alongside the main straight with smooth entry and exit tapers."""
    window = main_straight_window(points)
    if len(window) < 120:
        return None
    trim = int(len(window) * 0.06)
    window = window[trim: len(window) - trim]
    side = infield_side(points)
    point_type = type(points[0])
    n = len(window)
    ramp = max(1, int(n * PIT_RAMP_FRACTION))
    xy = []
    for j, idx in enumerate(window):
        pt = points[idx]
        t = min(j / ramp, (n - 1 - j) / ramp)
        d = side * offset * _smoothstep(t)
        xy.append((pt.x - math.sin(pt.theta) * d, pt.y + math.cos(pt.theta) * d))
    out = []
    s = 0.0
    step_m = 1.0
    for j, (x, y) in enumerate(xy):
        nx, ny = xy[min(j + 1, n - 1)]
        px, py = xy[max(j - 1, 0)]
        theta = math.atan2(ny - py, nx - px)
        out.append(point_type(s=s, x=x, y=y, theta=theta, curvature=0.0))
        s += step_m
    return out


def pit_box_positions(route_length: float) -> List[float]:
    """Arc-length positions of the pit boxes along the pit route."""
    lo, hi = route_length * 0.26, route_length * 0.74
    return [lo + (hi - lo) * (i + 0.5) / PIT_BOX_COUNT for i in range(PIT_BOX_COUNT)]


def _normal(pt: Any) -> Tuple[float, float]:
    return -math.sin(pt.theta), math.cos(pt.theta)


def _band(points: Sequence[Any], inner: Callable[[int, int], float],
          outer: Callable[[int, int], float], sign: int) -> QPainterPath:
    """Polygon between two offset curves; offsets are functions of (j, n)."""
    n = len(points)
    a, b = [], []
    for j, pt in enumerate(points):
        nx, ny = _normal(pt)
        di, do = inner(j, n) * sign, outer(j, n) * sign
        a.append(QPointF(pt.x + nx * di, pt.y + ny * di))
        b.append(QPointF(pt.x + nx * do, pt.y + ny * do))
    path = QPainterPath()
    path.addPolygon(QPolygonF(a + b[::-1]))
    path.closeSubpath()
    return path


def _offset_line(points: Sequence[Any], dist: Callable[[int, int], float], sign: int) -> QPainterPath:
    n = len(points)
    path = QPainterPath()
    for j, pt in enumerate(points):
        nx, ny = _normal(pt)
        d = dist(j, n) * sign
        p = QPointF(pt.x + nx * d, pt.y + ny * d)
        path.moveTo(p) if j == 0 else path.lineTo(p)
    return path


def _crowd_brush(seed: int) -> QBrush:
    rng = random.Random(seed)
    pix = QPixmap(48, 48)
    pix.fill(QColor(54, 62, 78))
    p = QPainter(pix)
    p.setPen(Qt.PenStyle.NoPen)
    palette = [(230, 60, 50), (240, 240, 240), (40, 90, 200), (250, 200, 40),
               (30, 30, 30), (240, 130, 30), (90, 180, 90), (210, 170, 140)]
    for row in range(0, 48, 4):
        for col in range(0, 48, 3):
            if rng.random() < 0.82:
                c = palette[rng.randrange(len(palette))]
                p.setBrush(QColor(*c))
                p.drawEllipse(QRectF(col + rng.random(), row + rng.random(), 2.2, 2.2))
    p.end()
    return QBrush(pix)


class CircuitDressing:
    """Cached trackside geometry and drawing for one circuit."""

    def __init__(self, track_points: Sequence[Any], pit_points: Optional[Sequence[Any]],
                 half_width: float = 14.0, team_colours: Optional[List[QColor]] = None,
                 seed: int = 0) -> None:
        self.points = list(track_points)
        self.pit = list(pit_points) if pit_points else []
        self.hw = half_width
        self.side = infield_side(self.points)
        self.rng = random.Random(seed)
        self.team_colours = team_colours or [QColor(*c) for c in TEAM_FALLBACK_COLOURS]
        xy = np.array([(p.x, p.y) for p in self.points])
        self.tree = cKDTree(xy)
        self.gravel: List[QPainterPath] = []
        self.tyre_walls: List[QPainterPath] = []
        self.runoff: List[QPainterPath] = []
        self.stands: List[dict] = []
        self.pit_paths: dict = {}
        self.crowd = _crowd_brush(seed)
        self._build_corners()
        self._build_main_grandstand()
        self._build_pit_complex()
        self.scenery = self._record_scenery()
        self._scenery_pixmap: Optional[QPixmap] = None
        self._scenery_key: Optional[Tuple[float, float, float]] = None

    # -- geometry helpers -------------------------------------------------
    def _clear_of_track(self, path: QPainterPath, margin: float) -> bool:
        poly = path.toFillPolygon()
        pts = np.array([(p.x(), p.y()) for p in poly])
        if len(pts) == 0:
            return False
        dist, _ = self.tree.query(pts)
        return bool(np.all(dist > self.hw + margin))

    def _slice(self, start: int, end: int) -> List[Any]:
        n = len(self.points)
        return [self.points[i % n] for i in range(start, end)]

    def _corners(self) -> List[dict]:
        pts = self.points
        n = len(pts)
        curv = np.array([p.curvature for p in pts])
        active = np.abs(curv) > 0.004
        corners = []
        i = 0
        while i < n:
            if not active[i]:
                i += 1
                continue
            sign = 1 if curv[i] > 0 else -1
            j = i
            while j < n and active[j] and (curv[j] > 0) == (sign > 0):
                j += 1
            turn = float(np.sum(curv[i:j]))
            corners.append({"start": i, "end": j, "sign": sign, "turn": abs(turn),
                            "max_curv": float(np.max(np.abs(curv[i:j])))})
            i = j
        return corners

    def _build_corners(self) -> None:
        self.corner_list = self._corners()
        n = len(self.points)
        for c in self.corner_list:
            length = c["end"] - c["start"]
            outside = -c["sign"]
            if c["turn"] > math.radians(55) and c["max_curv"] > 0.009:
                pts = self._slice(c["start"] - int(length * 0.1), c["end"] + int(length * 0.45) + 20)
                base = self.hw + 3

                def depth(j, m, base=base):
                    t = j / max(1, m - 1)
                    return base + 5 + 20 * math.sin(math.pi * min(1.0, t ** 0.8)) ** 0.7

                band = _band(pts, lambda j, m: base, depth, outside)
                self.gravel.append(band)
                self.tyre_walls.append(_offset_line(pts, lambda j, m: depth(j, m) + 2, outside))
                c["stand_offset"] = base + 34
            elif c["turn"] > math.radians(20):
                pts = self._slice(c["start"], c["end"] + int(length * 0.3))
                band = _band(pts, lambda j, m: self.hw + 1,
                             lambda j, m: self.hw + 1 + 7 * math.sin(math.pi * j / max(1, m - 1)),
                             outside)
                self.runoff.append(band)
        del n
        heavy = sorted((c for c in self.corner_list if "stand_offset" in c),
                       key=lambda c: c["turn"], reverse=True)[:3]
        for c in heavy:
            mid = (c["start"] + c["end"]) // 2
            span = max(30, int((c["end"] - c["start"]) * 0.8))
            pts = self._slice(mid - span // 2, mid + span // 2)
            self._add_stand(pts, c["stand_offset"], 16.0, -c["sign"], roof=False)

    def _add_stand(self, pts: List[Any], offset: float, depth: float, sign: int, roof: bool) -> None:
        seats = _band(pts, lambda j, m: offset, lambda j, m: offset + depth, sign)
        if not self._clear_of_track(seats, 6.0):
            return
        rows = [_offset_line(pts, lambda j, m, o=o: offset + o, sign)
                for o in np.arange(3.0, depth, 3.0)]
        base = _band(pts, lambda j, m: offset + depth, lambda j, m: offset + depth + 4, sign)
        roof_path = (_band(pts, lambda j, m: offset + depth * 0.62, lambda j, m: offset + depth + 3, sign)
                     if roof else None)
        front = _offset_line(pts, lambda j, m: offset, sign)
        self.stands.append({"seats": seats, "rows": rows, "base": base, "roof": roof_path,
                            "front": front})

    def _build_main_grandstand(self) -> None:
        window = main_straight_window(self.points)
        if len(window) < 80:
            return
        n = len(window)
        outside = -self.side
        sections = [(0.12, 0.42), (0.47, 0.8)] if n > 260 else [(0.2, 0.8)]
        for a, b in sections:
            idx = window[int(n * a): int(n * b)]
            self._add_stand([self.points[i] for i in idx], self.hw + 14, 24.0, outside, roof=True)

    def _build_pit_complex(self) -> None:
        if len(self.pit) < 20:
            return
        pit = self.pit
        side = self.side
        hw = PIT_HALF_WIDTH
        self.pit_paths["lane"] = _band(pit, lambda j, m: -hw, lambda j, m: hw, side)
        self.pit_paths["lines"] = [_offset_line(pit, lambda j, m: -hw, side),
                                   _offset_line(pit, lambda j, m: hw, side)]
        n = len(pit)
        lo, hi = int(n * PIT_RAMP_FRACTION), int(n * (1 - PIT_RAMP_FRACTION))
        flat = pit[lo:hi]
        if len(flat) < 10:
            return
        self.pit_paths["wall"] = _offset_line(flat, lambda j, m: -hw - 4, side)
        self.pit_paths["building"] = _band(flat, lambda j, m: hw + 3, lambda j, m: hw + 27, side)
        self.pit_paths["roof_stripe"] = _band(flat, lambda j, m: hw + 21, lambda j, m: hw + 24, side)
        self.pit_paths["paddock"] = _band(flat, lambda j, m: hw + 30, lambda j, m: hw + 62, side)
        route_len = float(pit[-1].s) or 1.0
        boxes = []
        for k, s in enumerate(pit_box_positions(route_len)):
            j = min(n - 1, int(s / route_len * (n - 1)))
            boxes.append((pit[j], self.team_colours[k % len(self.team_colours)]))
        self.pit_boxes = boxes
        spacing = math.hypot(boxes[1][0].x - boxes[0][0].x, boxes[1][0].y - boxes[0][0].y) if len(boxes) > 1 else 20
        self.box_width = max(6.0, spacing * 0.86)
        tower_pt = flat[-1]
        self.tower = (tower_pt, side)
        if not self._clear_of_track(self.pit_paths["paddock"], 4.0):
            self.pit_paths.pop("paddock")

    def _tree_positions(self) -> List[Tuple[float, float, float, int]]:
        xy = self.tree.data
        lo = xy.min(axis=0) - 220
        hi = xy.max(axis=0) + 220
        rng = self.rng
        phases = []
        for _ in range(5):
            freq, angle = rng.uniform(0.006, 0.02), rng.uniform(0, math.pi)
            phases.append((freq * math.cos(angle), freq * math.sin(angle), rng.uniform(0, 6.3)))
        avoid = [np.array([(p.x, p.y) for p in self.pit])] if self.pit else []
        avoid_tree = cKDTree(np.vstack(avoid)) if avoid else None
        stand_pts = [np.array([(q.x(), q.y()) for q in st["seats"].toFillPolygon()])
                     for st in self.stands]
        stand_tree = cKDTree(np.vstack(stand_pts)) if stand_pts else None
        step = 11.0
        gx, gy = np.meshgrid(np.arange(lo[0], hi[0], step), np.arange(lo[1], hi[1], step))
        x = gx.ravel() + np.array([rng.uniform(-5, 5) for _ in range(gx.size)])
        y = gy.ravel() + np.array([rng.uniform(-5, 5) for _ in range(gx.size)])
        keep_draw = np.array([rng.random() for _ in range(gx.size)])
        density = sum(np.sin(x * a + y * b + c) for a, b, c in phases) / len(phases)
        mask = (density >= -0.05) & (keep_draw <= 0.7)
        x, y = x[mask], y[mask]
        d, _ = self.tree.query(np.column_stack((x, y)))
        mask = (d >= self.hw + 42) & (d <= self.hw + 230)
        if avoid_tree is not None:
            mask &= avoid_tree.query(np.column_stack((x, y)))[0] >= 90
        if stand_tree is not None:
            mask &= stand_tree.query(np.column_stack((x, y)))[0] >= 14
        trees = [(float(px), float(py), rng.uniform(4.5, 8.5), rng.randrange(4))
                 for px, py in zip(x[mask], y[mask])]
        return trees

    def _record_scenery(self) -> QPicture:
        picture = QPicture()
        painter = QPainter(picture)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        centre = QPainterPath()
        centre.moveTo(self.points[0].x, self.points[0].y)
        for p in self.points[1:]:
            centre.lineTo(p.x, p.y)
        centre.closeSubpath()
        verge = QPen(QColor(92, 148, 66), 2 * (self.hw + 30))
        verge.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        verge.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.strokePath(centre, verge)
        stripe = QPen(QColor(104, 160, 74), 2 * (self.hw + 14))
        stripe.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.strokePath(centre, stripe)
        if self.pit:
            lane = QPainterPath()
            lane.moveTo(self.pit[0].x, self.pit[0].y)
            for p in self.pit[1:]:
                lane.lineTo(p.x, p.y)
            pit_grass = QPen(QColor(92, 148, 66), 150)
            pit_grass.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.strokePath(lane, pit_grass)
        canopy = [QColor(38, 92, 44), QColor(52, 110, 50), QColor(30, 78, 40), QColor(66, 122, 56)]
        trees = self._tree_positions()
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(10, 30, 12, 90)))
        for x, y, r, _ in trees:
            painter.drawEllipse(QPointF(x + r * 0.35, y + r * 0.35), r, r)
        for x, y, r, c in trees:
            painter.setBrush(QBrush(canopy[c]))
            painter.drawEllipse(QPointF(x, y), r, r)
        painter.setBrush(QBrush(QColor(140, 190, 100, 70)))
        for x, y, r, _ in trees:
            painter.drawEllipse(QPointF(x - r * 0.3, y - r * 0.3), r * 0.45, r * 0.45)
        painter.end()
        return picture

    # -- drawing ----------------------------------------------------------
    def draw_scenery(self, painter) -> None:
        """Blit scenery from a pixmap cached per zoom level.

        Thousands of trees are too slow to replay every frame, and the camera
        only pans between zoom changes, so the cache is keyed on scale alone.
        """
        t = painter.worldTransform()
        if abs(t.m12()) > 1e-9 or abs(t.m21()) > 1e-9:
            painter.drawPicture(0, 0, self.scenery)
            return
        device = painter.device()
        dpr = float(device.devicePixelRatioF()) if device is not None else 1.0
        scale_only = QTransform(t.m11(), 0.0, 0.0, t.m22(), 0.0, 0.0)
        bounds = scale_only.mapRect(QRectF(self.scenery.boundingRect()))
        if bounds.width() * bounds.height() * dpr * dpr > 25e6:
            painter.drawPicture(0, 0, self.scenery)
            return
        key = (round(t.m11(), 5), round(t.m22(), 5), dpr)
        if self._scenery_key != key or self._scenery_pixmap is None:
            pix = QPixmap(int(math.ceil(bounds.width() * dpr)) + 1,
                          int(math.ceil(bounds.height() * dpr)) + 1)
            pix.setDevicePixelRatio(dpr)
            pix.fill(Qt.GlobalColor.transparent)
            p = QPainter(pix)
            p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            p.setWorldTransform(scale_only * QTransform.fromTranslate(-bounds.left(), -bounds.top()))
            p.drawPicture(0, 0, self.scenery)
            p.end()
            self._scenery_pixmap, self._scenery_key = pix, key
        painter.save()
        painter.resetTransform()
        painter.drawPixmap(QPointF(bounds.left() + t.dx(), bounds.top() + t.dy()), self._scenery_pixmap)
        painter.restore()

    def draw_ground(self, painter, runoff_colour: QColor) -> None:
        painter.save()
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(runoff_colour))
        for path in self.runoff:
            painter.drawPath(path)
        painter.setBrush(QBrush(QColor(214, 196, 150)))
        for path in self.gravel:
            painter.drawPath(path)
        painter.setBrush(QBrush(QColor(196, 178, 132), Qt.BrushStyle.Dense6Pattern))
        for path in self.gravel:
            painter.drawPath(path)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        dark = QPen(QColor(25, 25, 25), 4)
        dashes = QPen(QColor(215, 40, 40), 4)
        dashes.setDashPattern([1.2, 1.2])
        for path in self.tyre_walls:
            painter.setPen(dark)
            painter.drawPath(path)
            painter.setPen(dashes)
            painter.drawPath(path)
        if "paddock" in self.pit_paths:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(86, 88, 92)))
            painter.drawPath(self.pit_paths["paddock"])
        painter.restore()

    def draw_structures(self, painter) -> None:
        painter.save()
        for stand in self.stands:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(0, 0, 0, 60)))
            painter.save()
            painter.translate(3, 3)
            painter.drawPath(stand["seats"])
            painter.restore()
            painter.setBrush(QBrush(QColor(150, 152, 158)))
            painter.drawPath(stand["base"])
            painter.setBrush(self.crowd)
            painter.drawPath(stand["seats"])
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(QColor(30, 34, 44, 160), 0.8))
            for row in stand["rows"]:
                painter.drawPath(row)
            painter.setPen(QPen(QColor(235, 235, 235), 1.6))
            painter.drawPath(stand["front"])
            if stand["roof"] is not None:
                painter.setPen(QPen(QColor(200, 204, 210), 1))
                painter.setBrush(QBrush(QColor(225, 228, 234, 215)))
                painter.drawPath(stand["roof"])
        painter.restore()

    def draw_pit(self, painter) -> None:
        paths = self.pit_paths
        if not paths:
            return
        painter.save()
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(70, 70, 73)))
        painter.drawPath(paths["lane"])
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(235, 235, 235), 1.2))
        for line in paths["lines"]:
            painter.drawPath(line)
        if "wall" in paths:
            painter.setPen(QPen(QColor(200, 200, 205), 3.0))
            painter.drawPath(paths["wall"])
            painter.setPen(QPen(QColor(60, 60, 64), 1.0))
            painter.drawPath(paths["wall"])
        if "building" in paths:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(0, 0, 0, 70)))
            painter.save()
            painter.translate(3, 3)
            painter.drawPath(paths["building"])
            painter.restore()
            painter.setBrush(QBrush(QColor(206, 208, 212)))
            painter.drawPath(paths["building"])
            painter.setBrush(QBrush(QColor(40, 44, 52)))
            painter.drawPath(paths["roof_stripe"])
            self._draw_garages(painter)
            self._draw_tower(painter)
        painter.restore()

    def _draw_garages(self, painter) -> None:
        side = self.side
        bw = self.box_width
        for pt, colour in self.pit_boxes:
            painter.save()
            painter.translate(pt.x, pt.y)
            painter.rotate(math.degrees(pt.theta))
            if side < 0:
                painter.scale(1, -1)
            painter.setPen(QPen(QColor(245, 245, 245), 0.8))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(QRectF(-bw / 2, 1.0, bw, PIT_HALF_WIDTH - 1.5))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(30, 30, 34)))
            painter.drawRect(QRectF(-bw / 2 + 1, PIT_HALF_WIDTH + 3, bw - 2, 7))
            painter.setBrush(QBrush(colour))
            painter.drawRect(QRectF(-bw / 2 + 1, PIT_HALF_WIDTH + 10, bw - 2, 3))
            painter.drawRect(QRectF(-bw / 2 + 2, PIT_HALF_WIDTH + 34, bw * 0.45, 7))
            painter.setBrush(QBrush(QColor(235, 235, 240)))
            painter.drawRect(QRectF(bw * 0.05, PIT_HALF_WIDTH + 36, bw * 0.4, 12))
            painter.restore()

    def _draw_tower(self, painter) -> None:
        pt, side = self.tower
        painter.save()
        painter.translate(pt.x, pt.y)
        painter.rotate(math.degrees(pt.theta))
        if side < 0:
            painter.scale(1, -1)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(0, 0, 0, 70)))
        painter.drawRect(QRectF(3, PIT_HALF_WIDTH + 6, 16, 16))
        painter.setBrush(QBrush(QColor(236, 238, 242)))
        painter.drawRect(QRectF(0, PIT_HALF_WIDTH + 3, 16, 16))
        painter.setBrush(QBrush(QColor(70, 140, 200)))
        painter.drawRect(QRectF(2, PIT_HALF_WIDTH + 5, 12, 4))
        painter.restore()
