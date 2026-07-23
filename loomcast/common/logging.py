import logging

from rich.logging import RichHandler


def setup_logger(name: str = "loomcast", level: int = logging.INFO) -> logging.Logger:
    """Set up and configure a structured logger for Loomcast."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(level)
        handler = RichHandler(
            rich_tracebacks=True,
            show_time=False,
            show_path=False,
        )
        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


logger = setup_logger()
