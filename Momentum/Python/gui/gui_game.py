"""Minimal PyQt6 GUI for the basic-race MVP.

Features:
- Start / Stop controls
- Strategy selector (placeholder)
- Live event feed (pit, incident)
- Standings table updated at the end
- Uses `simulate_race` directly and subscribes to `event_callback`

The module handles missing PyQt6 by printing an explanatory message so it
can be imported in CI or headless environments.
"""
from __future__ import annotations

import os
import threading
import time
from datetime import datetime
from typing import Optional, TYPE_CHECKING

try:
    from PyQt6 import QtWidgets, QtCore
    from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
    from PyQt6.QtCore import pyqtSignal, QObject
    HAS_QT = True
except Exception:  # pragma: no cover - optional dependency
    HAS_QT = False

if TYPE_CHECKING:
    # Help static type checkers (Pylance) resolve Qt symbols when available
    from PyQt6 import QtWidgets as _QtWidgets  # noqa: F401
    from PyQt6.QtWidgets import QApplication as _QApplication, QMainWindow as _QMainWindow, QMessageBox as _QMessageBox  # noqa: F401
    from PyQt6.QtCore import QObject as _QObject, pyqtSignal as _pyqtSignal  # noqa: F401

# If PyQt6 isn't present at analysis/runtime define lightweight Any fallbacks
from typing import Any
if not HAS_QT:
    QtWidgets: Any = None
    QtCore: Any = None
    QApplication: Any = None
    QMainWindow: Any = None
    QMessageBox: Any = None
    pyqtSignal: Any = None
    QObject: Any = None

# Define an EventEmitter that uses Qt signals when available, otherwise a stub.
# We avoid redeclaring the same symbol twice (Pylance warns) by creating a
# small adapter: when Qt is available we create a thin subclass, otherwise a
# plain Python stub is used and assigned to the name `EventEmitter` once.
if TYPE_CHECKING:
    # Provide a typing-time-only EventEmitter shape so static analysis is happy.
    class EventEmitter:  # pragma: no cover - typing-only stub
        event: Any

        def __init__(self):
            ...

        def connect(self, *_args, **_kwargs):
            ...

        def emit(self, *_args, **_kwargs):
            ...
else:
    if HAS_QT:
        class _QtEventEmitter(QObject):
            event = pyqtSignal(object)

        EventEmitter = _QtEventEmitter
    else:
        class EventEmitter:
            def __init__(self):
                self.event = self

            def connect(self, *_args, **_kwargs):
                return None

            def emit(self, *_args, **_kwargs):
                return None

from persistence_sqlite import PersistenceSQLite
from sim_simple import simulate_race


class TelemetryLogger:
    def __init__(self, out_dir: str = "saves"):
        os.makedirs(out_dir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.path = os.path.join(out_dir, f"telemetry_{ts}.csv")
        # write header
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("type,subtype,lap,driver_id,extra\n")

    def handle(self, event: dict) -> None:
        etype = event.get("type")
        subtype = event.get("subtype")
        lap = event.get("lap")
        driver = event.get("driver_id")
        extra = {}
        if "delay" in event:
            extra["delay"] = event["delay"]
        if "pit_time" in event:
            extra["pit_time"] = event["pit_time"]
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(f"{etype},{subtype},{lap},{driver},{extra}\n")


if not HAS_QT:
    def main():
        print("PyQt6 is not installed. Install it (`pip install PyQt6`) to run the GUI.")

    if __name__ == "__main__":
        main()

else:


    if TYPE_CHECKING:
        _BaseWindow = _QMainWindow
    elif HAS_QT:
        _BaseWindow = QMainWindow
    else:
        _BaseWindow = object


    class MainWindow(_BaseWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Momentum - Basic Race MVP")
            self.setGeometry(200, 200, 800, 600)

            # Core widgets
            central = QtWidgets.QWidget()
            self.setCentralWidget(central)
            layout = QtWidgets.QVBoxLayout(central)

            controls = QtWidgets.QHBoxLayout()
            self.start_btn = QtWidgets.QPushButton("Start")
            self.stop_btn = QtWidgets.QPushButton("Stop")
            self.stop_btn.setEnabled(False)
            self.strategy_combo = QtWidgets.QComboBox()
            self.strategy_combo.addItems(["Balanced", "Aggressive", "Conservative"])
            controls.addWidget(self.start_btn)
            controls.addWidget(self.stop_btn)
            controls.addWidget(self.strategy_combo)
            # Real-time demo controls
            self.real_time_cb = QtWidgets.QCheckBox("Real Time")
            self.real_time_cb.setToolTip("Run race in real-time with per-lap delay")
            # Default to real-time mode enabled so races are paced by default
            self.real_time_cb.setChecked(True)
            controls.addWidget(self.real_time_cb)

            self.lap_delay_spin = QtWidgets.QDoubleSpinBox()
            self.lap_delay_spin.setRange(0.0, 10.0)
            self.lap_delay_spin.setSingleStep(0.1)
            self.lap_delay_spin.setValue(0.5)
            self.lap_delay_spin.setSuffix(" s")
            controls.addWidget(QtWidgets.QLabel("Lap delay:"))
            controls.addWidget(self.lap_delay_spin)

            # (No seed/fidelity controls - per user preference)

            layout.addLayout(controls)

            self.progress = QtWidgets.QProgressBar()
            layout.addWidget(self.progress)

            splitter = QtWidgets.QSplitter()
            layout.addWidget(splitter)

            # Event feed
            self.event_list = QtWidgets.QListWidget()
            splitter.addWidget(self.event_list)

            # Standings table
            self.table = QtWidgets.QTableWidget(0, 3)
            self.table.setHorizontalHeaderLabels(["Pos", "Driver", "Time(s)"])
            splitter.addWidget(self.table)

            # wiring
            # Use getattr to avoid static-analysis errors on signal attributes
            getattr(self.start_btn.clicked, "connect")(self.start_race)
            getattr(self.stop_btn.clicked, "connect")(self.stop_race)

            self.emitter = EventEmitter()
            try:
                getattr(self.emitter.event, "connect")(self.on_event)
            except Exception:
                # Signal stubs may not support connect; ignore in that case
                pass

            self._thread: Optional[threading.Thread] = None
            self._stop_flag = threading.Event()
            self._stop_event: Optional[threading.Event] = None
            self.telemetry = TelemetryLogger()

        def append_event(self, text: str) -> None:
            self.event_list.addItem(text)
            self.event_list.scrollToBottom()

        def on_event(self, ev: dict) -> None:
            # Called in the Qt main thread via signal
            # Debug: always print incoming events to console for diagnosis
            try:
                print("GUI event:", ev)
            except Exception:
                pass

            et = ev.get("type")
            if et == "lap_start":
                lap = ev.get("lap")
                self.append_event(f"Lap {lap} start")
                # progress estimate (approx)
                # if laps not known, keep indeterminate
            elif et == "pit":
                self.append_event(f"PIT: driver {ev.get('driver_id')} lap {ev.get('lap')}")
            elif et == "incident":
                st = ev.get("subtype")
                self.append_event(f"INCIDENT({st}): driver {ev.get('driver_id')} lap {ev.get('lap')}")
            elif et == "race_finished":
                self.append_event("Race finished")
                results = ev.get("results", [])
                # At race finish show final table (results are minimal dicts)
                self.update_table(results)
            elif et == "standings":
                # Live per-lap standings: update table with names and times
                standings = ev.get("standings", [])
                # Convert standings to table rows with Pos/Driver/Time(s)
                self.table.setRowCount(len(standings))
                for i, r in enumerate(standings):
                    pos = r.get("position", i + 1)
                    name = r.get("name", str(r.get("driver_id")))
                    t = r.get("time_seconds")
                    self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(str(pos)))
                    self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(name))
                    self.table.setItem(i, 2, QtWidgets.QTableWidgetItem(f"{t:.2f}" if t is not None else "-"))
            elif et == "error":
                # show errors in the GUI as well as telemetry
                msg = ev.get("message", "Unknown error")
                self.append_event(f"ERROR: {msg}")
                print("GUI error:", msg)
            # write to telemetry
            try:
                self.telemetry.handle(ev)
            except Exception:
                pass

        def update_table(self, results: list):
            self.table.setRowCount(len(results))
            for i, r in enumerate(results):
                self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(str(r.get("position", i + 1))))
                self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(str(r.get("driver_id"))))
                t = r.get("time_seconds")
                self.table.setItem(i, 2, QtWidgets.QTableWidgetItem(f"{t:.2f}" if t is not None else "-"))

        def _prepare_db_and_drivers(self):
            """Open persistence, ensure schema, and return (db, drivers, track).

            Loads the first 20 drivers by id from the persistent DB if present,
            otherwise falls back to non-destructive demo seeding.
            """
            db = PersistenceSQLite()
            db.ensure_schema()

            drivers = []
            for did in range(1, 21):
                d = db.get_driver(did)
                if d is not None:
                    drivers.append(d)

            if len(drivers) == 0:
                db.seed_sample_data(count=20)
                drivers = db.list_drivers()

            track = db.get_track(1)
            return db, drivers, track

        def _make_event_callback(self):
            """Return an event callback function that forwards events into Qt."""
            def evcb(e: dict):
                try:
                    print("evcb called:", e)
                except Exception:
                    pass
                try:
                    getattr(self.emitter.event, "emit")(e)
                except Exception:
                    pass

            return evcb

        def _emit_safe(self, event: dict):
            try:
                getattr(self.emitter.event, "emit")(event)
            except Exception:
                pass

        def start_race(self):
            """Start the race on a background thread (cooperative cancellation).

            This method orchestrates DB preparation, event callback creation,
            simulator execution and saving results. Most logic is delegated to
            helper methods to keep cognitive complexity low.
            """
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self._stop_flag.clear()
            self.event_list.clear()
            self.table.setRowCount(0)

            # run simulation in background thread
            def runner():
                results = []
                try:
                    db, drivers, track = self._prepare_db_and_drivers()
                    evcb = self._make_event_callback()

                    # prepare stop event and lap delay if real-time selected
                    self._stop_event = threading.Event()
                    lap_delay = float(self.lap_delay_spin.value()) if self.real_time_cb.isChecked() else 0.0

                    # Run simulator with cooperative stop and optional per-lap delay
                    results = simulate_race(
                        drivers,
                        track,
                        seed=None,
                        verbose=False,
                        event_callback=evcb,
                        stop_event=self._stop_event,
                        lap_delay=lap_delay,
                    )

                    # save results
                    db.save_race_results(race_id=1, results=results)
                except Exception as exc:
                    self._emit_safe({"type": "error", "message": str(exc)})
                finally:
                    # ensure results exists and emit final event
                    try:
                        _results = results
                    except NameError:
                        _results = []
                    self._emit_safe({"type": "race_finished", "results": [{"driver_id": r.driver_id, "time_seconds": getattr(r, 'time_seconds', None), "position": r.position} for r in _results]})

            self._thread = threading.Thread(target=runner, daemon=True)
            self._thread.start()

        def stop_race(self):
            # cooperative stop: set the stop event so simulate_race can exit early
            if self._stop_event is not None:
                self._stop_event.set()
                self.append_event("Stop requested — attempting to cancel race")
            else:
                # fallback: set legacy flag
                self._stop_flag.set()
                self.append_event("Stop requested (legacy fallback)")
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)


    def main():
        app = QApplication([])
        w = MainWindow()
        w.show()
        # No automatic start by default — user initiates runs via the Start button.

        app.exec()


    if __name__ == "__main__":
        main()
