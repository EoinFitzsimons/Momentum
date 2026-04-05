"""
MOMENTUM - Logging System

Comprehensive logging, error tracking, and crash reporting system.
Creates detailed logs for debugging and error analysis.
"""

import logging
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional
import json


class MomentumLogger:
    """
    Centralized logging system for MOMENTUM

    Features:
    - Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - File and console output
    - Rotating log files
    - Crash report generation
    - Structured error tracking
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        """Singleton pattern - only one logger instance"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialise logging system"""
        if self._initialized:
            return

        # Create logs directory
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)

        # Generate log filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.logs_dir / f"momentum_{timestamp}.log"
        self.error_log_file = self.logs_dir / f"errors_{timestamp}.log"
        self.crash_log_file = self.logs_dir / f"crash_{timestamp}.json"

        # Setup main logger
        self.logger = logging.getLogger("MOMENTUM")
        self.logger.setLevel(logging.DEBUG)

        # Remove existing handlers to avoid duplicates
        self.logger.handlers.clear()

        # Create formatters
        detailed_formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        simple_formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S'
        )

        # File handler - detailed logs
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        self.logger.addHandler(file_handler)

        # Error file handler - errors only
        error_handler = logging.FileHandler(
            self.error_log_file, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        self.logger.addHandler(error_handler)

        # Console handler - important messages only
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        self.logger.addHandler(console_handler)

        # Error tracking
        self.error_count = 0
        self.errors = []

        self._initialized = True

        # Log initialisation
        self.info("=" * 80)
        self.info("MOMENTUM Logging System Initialised")
        self.info(f"Log file: {self.log_file}")
        self.info(f"Error log: {self.error_log_file}")
        self.info("=" * 80)

    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(message, extra=kwargs)

    def info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(message, extra=kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(message, extra=kwargs)

    def error(self, message: str,
              exception: Optional[Exception] = None, **kwargs):
        """
        Log error message with optional exception details

        Args:
            message: Error description
            exception: Optional exception object
            **kwargs: Additional context
        """
        self.error_count += 1

        # Format error message
        error_msg = f"[ERROR #{self.error_count}] {message}"

        # Add exception details if provided
        if exception:
            error_msg += f"\nException Type: {type(exception).__name__}"
            error_msg += f"\nException Message: {str(exception)}"
            error_msg += f"\nTraceback:\n{traceback.format_exc()}"

        self.logger.error(error_msg, extra=kwargs)

        # Store error for crash report
        error_data = {
            'error_number': self.error_count,
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'exception_type': type(exception).__name__ if exception else None,
            'exception_message': str(exception) if exception else None,
            'traceback': traceback.format_exc() if exception else None,
            'context': kwargs
        }
        self.errors.append(error_data)

    def critical(self, message: str,
                 exception: Optional[Exception] = None, **kwargs):
        """
        Log critical error (system-threatening)

        Args:
            message: Critical error description
            exception: Optional exception object
            **kwargs: Additional context
        """
        critical_msg = f"CRITICAL: {message}"

        if exception:
            critical_msg += f"\nException: {
                type(exception).__name__}: {
                str(exception)}"
            critical_msg += f"\nTraceback:\n{traceback.format_exc()}"

        self.logger.critical(critical_msg, extra=kwargs)

        # Store in errors list
        self.errors.append({
            'level': 'CRITICAL',
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'exception_type': type(exception).__name__ if exception else None,
            'exception_message': str(exception) if exception else None,
            'traceback': traceback.format_exc() if exception else None,
            'context': kwargs
        })

    def exception(self, message: str, **kwargs):
        """
        Log exception with full traceback
        Automatically captures current exception context
        """
        exc_type, exc_value, _ = sys.exc_info()

        error_msg = f"{message}\n"
        error_msg += f"Exception Type: {
            exc_type.__name__ if exc_type else 'Unknown'}\n"
        error_msg += f"Exception Message: {
            str(exc_value) if exc_value else 'No message'}\n"
        error_msg += f"Traceback:\n{traceback.format_exc()}"

        self.logger.exception(error_msg, extra=kwargs)

        # Store detailed exception info
        self.errors.append({
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'exception_type': exc_type.__name__ if exc_type else None,
            'exception_value': str(exc_value) if exc_value else None,
            'traceback': traceback.format_exc(),
            'context': kwargs
        })

    def log_function_call(self, func_name: str, args=None, kwargs=None):
        """
        Log function call with arguments

        Useful for debugging function execution flow
        """
        msg = f"Function called: {func_name}("

        if args:
            msg += f"args={args}"

        if kwargs:
            if args:
                msg += ", "
            msg += f"kwargs={kwargs}"

        msg += ")"

        self.debug(msg)

    def log_database_operation(
            self, operation: str, table: str, details: str = ""):
        """Log database operations"""
        msg = f"DB Operation: {operation} on {table}"
        if details:
            msg += f" | {details}"
        self.debug(msg)

    def log_game_state(self, state_name: str, state_data: dict):
        """Log game state changes"""
        self.debug(
            f"Game State Change: {state_name}",
            extra={
                'state': state_data})

    def log_performance(self, operation: str, duration: float):
        """Log performance metrics"""
        self.debug(f"Performance: {operation} took {duration:.3f}s")

    def generate_crash_report(self, crash_info: Optional[dict] = None):
        """
        Generate comprehensive crash report

        Args:
            crash_info: Optional additional crash context

        Returns:
            Path to crash report file
        """
        import platform
        import psutil

        crash_report = {
            'crash_time': datetime.now().isoformat(),
            'system_info': {
                'platform': platform.platform(),
                'python_version': sys.version,
                'machine': platform.machine(),
                'processor': platform.processor(),
            },
            'memory_info': {
                'available_mb': psutil.virtual_memory().available / (1024 * 1024),
                'total_mb': psutil.virtual_memory().total / (1024 * 1024),
                'percent_used': psutil.virtual_memory().percent,
            },
            'error_count': self.error_count,
            'errors': self.errors,
            'crash_context': crash_info or {},
        }

        # Add current exception if available
        if sys.exc_info()[0] is not None:
            exc_type, exc_value, _ = sys.exc_info()
            crash_report['exception'] = {
                'type': exc_type.__name__ if exc_type else None,
                'message': str(exc_value) if exc_value else None,
                'traceback': traceback.format_exc(),
            }

        # Write crash report to JSON
        with open(self.crash_log_file, 'w', encoding='utf-8') as f:
            json.dump(crash_report, f, indent=2)

        self.critical(f"Crash report generated: {self.crash_log_file}")

        return self.crash_log_file

    def get_recent_logs(self, lines: int = 50) -> str:
        """
        Get recent log lines

        Args:
            lines: Number of recent lines to retrieve

        Returns:
            String containing recent log entries
        """
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                recent = all_lines[-lines:] if len(
                    all_lines) > lines else all_lines
                return ''.join(recent)
        except Exception as e:
            return f"Error reading logs: {str(e)}"

    def get_all_errors(self) -> list:
        """Get all logged errors"""
        return self.errors.copy()

    def clear_old_logs(self, days: int = 7):
        """
        Delete log files older than specified days

        Args:
            days: Age threshold in days
        """
        import time

        cutoff_time = time.time() - (days * 86400)
        deleted_count = 0

        for log_file in self.logs_dir.glob("*.log"):
            if log_file.stat().st_mtime < cutoff_time:
                log_file.unlink()
                deleted_count += 1
                self.info(f"Deleted old log: {log_file.name}")

        for json_file in self.logs_dir.glob("*.json"):
            if json_file.stat().st_mtime < cutoff_time:
                json_file.unlink()
                deleted_count += 1

        self.info(f"Cleaned up {deleted_count} old log files")


# Global logger instance
logger = MomentumLogger()


def setup_exception_handler():
    """
    Setup global exception handler to catch uncaught exceptions
    """
    def handle_exception(exc_type, exc_value, exc_traceback):
        """Handle uncaught exceptions"""
        if issubclass(exc_type, KeyboardInterrupt):
            # Allow Ctrl+C to work normally
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logger.critical(
            "UNCAUGHT EXCEPTION - APPLICATION CRASH",
            exception=exc_value
        )

        # Generate crash report
        crash_report_path = logger.generate_crash_report({
            'type': 'uncaught_exception',
            'exception_type': exc_type.__name__,
            'exception_message': str(exc_value),
        })

        print("\n" + "=" * 80)
        print("FATAL ERROR - Application Crashed")
        print("=" * 80)
        print(f"\nCrash report saved to: {crash_report_path}")
        print("\nPlease send this crash report to the developer.")
        print("\nRecent errors:")
        for error in logger.get_all_errors()[-5:]:
            print(f"  - {error.get('message', 'Unknown error')}")
        print("\n" + "=" * 80)

        # Call original exception handler
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

    # Set custom exception handler
    sys.excepthook = handle_exception

    logger.info("Global exception handler installed")


# Decorator for automatic function logging
def log_function(func):
    """
    Decorator to automatically log function calls and exceptions

    Usage:
        @log_function
        def my_function(arg1, arg2):
            # function code
    """
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        logger.log_function_call(func_name, args, kwargs)

        try:
            result = func(*args, **kwargs)
            logger.debug(f"Function completed: {func_name}")
            return result

        except Exception as e:
            logger.error(
                f"Exception in function {func_name}",
                exception=e,
                args=args,
                kwargs=kwargs
            )
            raise

    return wrapper


# Context manager for timed operations
class LoggedOperation:
    """
    Context manager for logging timed operations

    Usage:
        with LoggedOperation("Load Database"):
            # operation code
    """

    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None

    def __enter__(self):
        self.start_time = datetime.now()
        logger.info(f"Starting: {self.operation_name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        start_time = self.start_time or datetime.now()
        duration = (datetime.now() - start_time).total_seconds()

        if exc_type is None:
            logger.info(f"Completed: {self.operation_name} ({duration:.3f}s)")
        else:
            logger.error(
                f"Failed: {self.operation_name} ({duration:.3f}s)",
                exception=exc_val
            )

        return False  # Don't suppress exceptions


if __name__ == "__main__":
    # Test logging system
    print("Testing MOMENTUM Logging System\n")

    logger.info("This is an info message")
    logger.debug("This is a debug message")
    logger.warning("This is a warning message")

    # Test error logging
    try:
        raise ValueError("Test error for logging")
    except Exception as e:
        logger.error("Caught test exception", exception=e)

    # Test function logging
    @log_function
    def test_function(x, y):
        return x + y

    result = test_function(5, 3)

    # Test timed operation
    with LoggedOperation("Test Operation"):
        import time
        time.sleep(0.1)

    # Test crash report generation
    logger.generate_crash_report({'test': 'crash report'})

    print(f"\nLog files created in: {logger.logs_dir}")
    print(f"Main log: {logger.log_file}")
    print(f"Error log: {logger.error_log_file}")
    print(f"Crash report: {logger.crash_log_file}")

    print("\nRecent logs:")
    print(logger.get_recent_logs(10))
