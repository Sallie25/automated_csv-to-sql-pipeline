import logging
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine

# ── Logging Setup ──────────────────────────────────────────────────────────
# Writes to both terminal and pipeline.log simultaneously
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    handlers=[
        logging.FileHandler("pipeline.log"),  # Save to file
        logging.StreamHandler()               # Print to terminal
    ]
)
logger = logging.getLogger(__name__)

# ── Configuration ──────────────────────────────────────────────────────────
raw_data_path = Path("data/raw")
engine = create_engine("sqlite:///pipeline.db")

# ── Scan for CSV files ─────────────────────────────────────────────────────
csv_files = list(raw_data_path.glob("*.csv"))

if not csv_files:
    logger.warning("No CSV files found in data/raw/")
    exit()

logger.info(f"Found {len(csv_files)} CSV file(s)")


def clean_table_name(file_path: Path) -> str:
    """Convert filename into a safe SQL table name."""
    return file_path.stem.replace("-", "_").replace(" ", "_").lower()


# ── Process each file ──────────────────────────────────────────────────────
success_count = 0
error_count = 0

for file in csv_files:
    table_name = clean_table_name(file)
    logger.info(f"Processing: {file.name} - table: '{table_name}'")

    try:
        # Read CSV
        df = pd.read_csv(file)
        logger.info(f"  Shape: {df.shape[0]} rows x {df.shape[1]} columns")

        # Load into database
        df.to_sql(name=table_name, con=engine, if_exists="replace", index=False)
        logger.info(f"  [OK] Loaded into '{table_name}'")
        success_count += 1

    except Exception as e:
        # Log the error but continue to the next file
        logger.error(f"  [FAILED] Failed to process {file.name}: {e}")
        error_count += 1

# ── Summary ────────────────────────────────────────────────────────────────
logger.info(f"\nPipeline complete — {success_count} loaded, {error_count} failed")