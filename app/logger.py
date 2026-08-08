import logging

from app.config import LOG_DIR

LOG_FILE = LOG_DIR / "pipeline.log"

logger = logging.getLogger("pipeline")

logger.setLevel(logging.INFO)

if not logger.handlers:

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    file_handler = logging.FileHandler(LOG_FILE)

    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)