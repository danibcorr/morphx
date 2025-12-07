# Standard libraries
import logging


def create_logger(
    logger_file_name: str, logger_name: str | None = None
) -> logging.Logger:
    """
    Create a logger configured to write messages to a file and console.

    The logger is initialized once per name to avoid duplicate handlers.
    It records informational messages and uses a uniform timestamped
    formatter for both file and stream outputs.

    Args:
        logger_file_name: File path where log entries are written.
        logger_name: Name assigned to the logger, or a default when
            unspecified.

    Returns:
        Logger instance configured with file and console handlers.
    """

    logger = logging.getLogger(logger_name or __name__)
    logger.setLevel(logging.INFO)

    # Prevent adding multiple handlers if logger already exists
    if not logger.handlers:
        # File handler
        file_handler = logging.FileHandler(logger_file_name)
        file_handler.setLevel(logging.INFO)

        # Console handler (optional, comment out if not needed)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        # Avoid log duplication in root logger
        logger.propagate = False

    return logger
