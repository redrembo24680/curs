"""Logging configuration for Flask application."""
import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logger(app):
    """Configure logging for the Flask application."""
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(logs_dir, exist_ok=True)

    # Set log level based on environment
    log_level = logging.INFO
    if app.config.get('DEBUG'):
        log_level = logging.DEBUG

    # Configure root logger
    app.logger.setLevel(log_level)

    # Remove default handlers
    app.logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    app.logger.addHandler(console_handler)

    # File handler - rotating log files (max 10MB, keep 10 backups)
    file_handler = RotatingFileHandler(
        os.path.join(logs_dir, 'app.log'),
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10
    )
    file_handler.setLevel(log_level)
    file_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    app.logger.addHandler(file_handler)

    # Error file handler - only errors and critical
    error_handler = RotatingFileHandler(
        os.path.join(logs_dir, 'error.log'),
        maxBytes=10 * 1024 * 1024,
        backupCount=10
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    app.logger.addHandler(error_handler)

    app.logger.info('Logging configured successfully')
    return app.logger
