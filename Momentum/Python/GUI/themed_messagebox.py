"""Small wrapper providing themed message dialog functions.

These mirror the common `QMessageBox` static helpers but ensure the
dialog receives the application's stylesheet so captures show the
intended theme.
"""
from __future__ import annotations

from typing import Any


def _apply_theme(widget) -> None:
    try:
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        if app is None:
            return
        ss = app.styleSheet() or ""
        if ss:
            try:
                widget.setStyleSheet(ss)
            except Exception:
                pass
    except Exception:
        pass


def information(parent, title: str, text: str, *args: Any, **kwargs: Any) -> int:
    from PyQt6.QtWidgets import QMessageBox
    m = QMessageBox(parent)
    m.setIcon(QMessageBox.Icon.Information)
    m.setWindowTitle(title)
    m.setText(text)
    # forward optional standard buttons if provided
    if args:
        try:
            m.setStandardButtons(args[0])
        except Exception:
            pass
    _apply_theme(m)
    return m.exec()


def warning(parent, title: str, text: str, *args: Any, **kwargs: Any) -> int:
    from PyQt6.QtWidgets import QMessageBox
    m = QMessageBox(parent)
    m.setIcon(QMessageBox.Icon.Warning)
    m.setWindowTitle(title)
    m.setText(text)
    if args:
        try:
            m.setStandardButtons(args[0])
        except Exception:
            pass
    _apply_theme(m)
    return m.exec()


def critical(parent, title: str, text: str, *args: Any, **kwargs: Any) -> int:
    from PyQt6.QtWidgets import QMessageBox
    m = QMessageBox(parent)
    m.setIcon(QMessageBox.Icon.Critical)
    m.setWindowTitle(title)
    m.setText(text)
    if args:
        try:
            m.setStandardButtons(args[0])
        except Exception:
            pass
    _apply_theme(m)
    return m.exec()


def question(parent, title: str, text: str, buttons=None, default=None) -> Any:
    from PyQt6.QtWidgets import QMessageBox
    m = QMessageBox(parent)
    m.setIcon(QMessageBox.Icon.Question)
    m.setWindowTitle(title)
    m.setText(text)
    if buttons is not None:
        try:
            m.setStandardButtons(buttons)
        except Exception:
            pass
    if default is not None:
        try:
            m.setDefaultButton(default)
        except Exception:
            pass
    _apply_theme(m)
    return m.exec()


def about(parent, title: str, text: str) -> None:
    # Use a themed dialog instance to mimic QMessageBox.about behaviour
    from PyQt6.QtWidgets import QMessageBox
    m = QMessageBox(parent)
    m.setIcon(QMessageBox.Icon.Information)
    m.setWindowTitle(title)
    m.setText(text)
    _apply_theme(m)
    m.exec()
