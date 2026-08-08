from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"

RAW_DATA = DATA_DIR / "raw"
BRONZE_DATA = DATA_DIR / "bronze"
SILVER_DATA = DATA_DIR / "silver"
GOLD_DATA = DATA_DIR / "gold"

LOG_DIR = BASE_DIR / "logs"

for folder in (
    RAW_DATA,
    BRONZE_DATA,
    SILVER_DATA,
    GOLD_DATA,
    LOG_DIR,
):
    folder.mkdir(parents=True, exist_ok=True)