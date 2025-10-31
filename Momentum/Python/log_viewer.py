"""
MOMENTUM - Log Viewer Tool

View and analyze game logs and crash reports.
"""

import sys
import json
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QListWidget, QLabel, QSplitter, QTabWidget,
    QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QTextCharFormat, QColor, QTextCursor


class LogViewer(QMainWindow):
    """Log file viewer and analyzer"""
    
    def __init__(self):
        super().__init__()
        self.logs_dir = Path("logs")
        self.current_file = None
        self.init_ui()
        self.load_log_files()
    
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("MOMENTUM - Log Viewer")
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        
        # Left panel - File list
        left_panel = QVBoxLayout()
        
        title = QLabel("Log Files")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        left_panel.addWidget(title)
        
        self.file_list = QListWidget()
        self.file_list.itemClicked.connect(self.load_selected_file)
        left_panel.addWidget(self.file_list)
        
        btn_refresh = QPushButton("Refresh")
        btn_refresh.clicked.connect(self.load_log_files)
        left_panel.addWidget(btn_refresh)
        
        btn_open = QPushButton("Open External File")
        btn_open.clicked.connect(self.open_external_file)
        left_panel.addWidget(btn_open)
        
        layout.addLayout(left_panel, 1)
        
        # Right panel - Content viewer
        right_panel = QVBoxLayout()
        
        self.file_label = QLabel("No file selected")
        self.file_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        right_panel.addWidget(self.file_label)
        
        # Tabs for different views
        self.tabs = QTabWidget()
        
        # Raw log view
        self.raw_view = QTextEdit()
        self.raw_view.setReadOnly(True)
        self.raw_view.setFont(QFont("Courier New", 10))
        self.tabs.addTab(self.raw_view, "Raw Log")
        
        # Error-only view
        self.error_view = QTextEdit()
        self.error_view.setReadOnly(True)
        self.error_view.setFont(QFont("Courier New", 10))
        self.tabs.addTab(self.error_view, "Errors Only")
        
        # JSON view (for crash reports)
        self.json_view = QTextEdit()
        self.json_view.setReadOnly(True)
        self.json_view.setFont(QFont("Courier New", 10))
        self.tabs.addTab(self.json_view, "Structured View")
        
        right_panel.addWidget(self.tabs)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        btn_copy = QPushButton("Copy to Clipboard")
        btn_copy.clicked.connect(self.copy_to_clipboard)
        button_layout.addWidget(btn_copy)
        
        btn_export = QPushButton("Export Selected")
        btn_export.clicked.connect(self.export_log)
        button_layout.addWidget(btn_export)
        
        btn_clear_old = QPushButton("Clear Old Logs")
        btn_clear_old.clicked.connect(self.clear_old_logs)
        button_layout.addWidget(btn_clear_old)
        
        right_panel.addLayout(button_layout)
        
        layout.addLayout(right_panel, 3)
    
    def load_log_files(self):
        """Load list of log files"""
        self.file_list.clear()
        
        if not self.logs_dir.exists():
            self.logs_dir.mkdir(exist_ok=True)
            return
        
        # Get all log files
        log_files = sorted(
            list(self.logs_dir.glob("*.log")) + list(self.logs_dir.glob("*.json")),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        for log_file in log_files:
            size = log_file.stat().st_size / 1024  # KB
            item_text = f"{log_file.name} ({size:.1f} KB)"
            self.file_list.addItem(item_text)
    
    def load_selected_file(self, item):
        """Load selected log file"""
        filename = item.text().split(" (")[0]
        file_path = self.logs_dir / filename
        self.load_file(file_path)
    
    def load_file(self, file_path: Path):
        """Load and display log file"""
        self.current_file = file_path
        self.file_label.setText(f"File: {file_path.name}")
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Display raw content
            self.raw_view.setPlainText(content)
            
            # If JSON file, parse and display
            if file_path.suffix == '.json':
                try:
                    data = json.loads(content)
                    formatted = json.dumps(data, indent=2)
                    self.json_view.setPlainText(formatted)
                    
                    # Show structured error info if crash report
                    if 'errors' in data:
                        error_summary = self.format_crash_report(data)
                        self.error_view.setHtml(error_summary)
                
                except json.JSONDecodeError:
                    self.json_view.setPlainText("Invalid JSON file")
            
            # Extract and display errors
            else:
                errors = self.extract_errors(content)
                self.error_view.setHtml(errors)
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load file:\n{str(e)}"
            )
    
    def extract_errors(self, content: str) -> str:
        """Extract error lines from log content"""
        lines = content.split('\n')
        error_lines = []
        
        for i, line in enumerate(lines):
            if 'ERROR' in line or 'CRITICAL' in line or 'Exception' in line:
                # Include context (2 lines before and after)
                start = max(0, i - 2)
                end = min(len(lines), i + 3)
                context = lines[start:end]
                error_lines.append('<br>'.join(context))
                error_lines.append('<hr>')
        
        if not error_lines:
            return "<p>No errors found in this log file.</p>"
        
        return '<pre>' + '\n'.join(error_lines) + '</pre>'
    
    def format_crash_report(self, data: dict) -> str:
        """Format crash report data as HTML"""
        html = "<h2>Crash Report Summary</h2>"
        
        html += f"<p><b>Crash Time:</b> {data.get('crash_time', 'Unknown')}</p>"
        
        if 'system_info' in data:
            html += "<h3>System Information</h3><ul>"
            for key, value in data['system_info'].items():
                html += f"<li><b>{key}:</b> {value}</li>"
            html += "</ul>"
        
        if 'memory_info' in data:
            html += "<h3>Memory Information</h3><ul>"
            for key, value in data['memory_info'].items():
                html += f"<li><b>{key}:</b> {value}</li>"
            html += "</ul>"
        
        html += f"<p><b>Total Errors:</b> {data.get('error_count', 0)}</p>"
        
        if 'exception' in data:
            exc = data['exception']
            html += "<h3>Exception Details</h3>"
            html += f"<p><b>Type:</b> {exc.get('type', 'Unknown')}</p>"
            html += f"<p><b>Message:</b> {exc.get('message', 'No message')}</p>"
            html += f"<pre>{exc.get('traceback', 'No traceback')}</pre>"
        
        if 'errors' in data and data['errors']:
            html += f"<h3>Recent Errors ({len(data['errors'])})</h3>"
            for i, error in enumerate(data['errors'][-10:], 1):
                html += f"<h4>Error {i}</h4>"
                html += f"<p><b>Time:</b> {error.get('timestamp', 'Unknown')}</p>"
                html += f"<p><b>Message:</b> {error.get('message', 'No message')}</p>"
                if error.get('exception_type'):
                    html += f"<p><b>Exception:</b> {error['exception_type']}</p>"
                if error.get('traceback'):
                    html += f"<pre>{error['traceback']}</pre>"
                html += "<hr>"
        
        return html
    
    def copy_to_clipboard(self):
        """Copy current view to clipboard"""
        current_widget = self.tabs.currentWidget()
        text = current_widget.toPlainText()
        
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        
        QMessageBox.information(self, "Copied", "Content copied to clipboard!")
    
    def export_log(self):
        """Export log to file"""
        if not self.current_file:
            QMessageBox.warning(self, "No File", "No file selected")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Log",
            str(self.current_file.name),
            "Text Files (*.txt);;All Files (*.*)"
        )
        
        if filename:
            try:
                content = self.raw_view.toPlainText()
                Path(filename).write_text(content, encoding='utf-8')
                QMessageBox.information(self, "Exported", f"Log exported to:\n{filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export:\n{str(e)}")
    
    def open_external_file(self):
        """Open external log file"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open Log File",
            "",
            "Log Files (*.log *.json *.txt);;All Files (*.*)"
        )
        
        if filename:
            self.load_file(Path(filename))
    
    def clear_old_logs(self):
        """Delete old log files"""
        from logging_system import logger
        
        reply = QMessageBox.question(
            self,
            "Clear Old Logs",
            "Delete log files older than 7 days?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            logger.clear_old_logs(days=7)
            self.load_log_files()
            QMessageBox.information(self, "Done", "Old logs cleared!")


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("MOMENTUM Log Viewer")
    
    viewer = LogViewer()
    viewer.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
