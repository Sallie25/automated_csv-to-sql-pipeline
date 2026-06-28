import logging
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone
from sqlalchemy import create_engine, text
from transform import transform_dataframe


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


def run_pipeline():
    # ── Configuration ──────────────────────────────────────────────────────────
    raw_data_path = Path("data/raw")
    engine = create_engine("sqlite:///pipeline.db")

    # ── [NEW] Create pipeline_metadata table if it doesn't exist ───────────────
    # This table tracks every file that has been successfully loaded so we can
    # skip already-processed files on subsequent runs.
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS pipeline_metadata (
                filename   TEXT        NOT NULL,
                loaded_at  TIMESTAMP   NOT NULL,
                row_count  INTEGER     NOT NULL,
                status     TEXT        NOT NULL
            )
        """))
        conn.commit()
        logger.info("pipeline_metadata table ready")

    # ── [NEW] Query metadata table for already-loaded filenames ────────────────
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT filename FROM pipeline_metadata WHERE status = 'success'")
        )
        already_loaded = {row[0] for row in result}  # a set for O(1) lookups

    logger.info(f"Files already loaded in previous runs: {len(already_loaded)}")

    # ── Scan for CSV files ─────────────────────────────────────────────────────
    csv_files = list(raw_data_path.glob("*.csv"))

    if not csv_files:
        logger.warning("No CSV files found in data/raw/")
        return  # use return instead of exit() so scheduler isn't killed

    logger.info(f"Found {len(csv_files)} CSV file(s) in data/raw/")

    # ── [NEW] Filter out files that have already been loaded ───────────────────
    new_files = [f for f in csv_files if f.name not in already_loaded]

    if not new_files:
        logger.info("No new CSV files to process — skipping run")
        return

    logger.info(f"{len(new_files)} new file(s) to process: {[f.name for f in new_files]}")

    def clean_table_name(file_path: Path) -> str:
        """Convert filename into a safe SQL table name."""
        return file_path.stem.replace("-", "_").replace(" ", "_").lower()

    # ── Process each new file ──────────────────────────────────────────────────
    success_count = 0
    error_count = 0

    for file in new_files:
        table_name = clean_table_name(file)
        logger.info(f"Processing: {file.name} -> table: '{table_name}'")

        try:
            # Read CSV
            df = pd.read_csv(file)
            logger.info(f"  Shape before transform: {df.shape[0]} rows x {df.shape[1]} columns")

            # Transform the dataframe
            df = transform_dataframe(df, source_filename=file.name)
            logger.info(f"  Shape after transform:  {df.shape[0]} rows x {df.shape[1]} columns")

            # Load into database
            df.to_sql(name=table_name, con=engine, if_exists="replace", index=False)
            logger.info(f"  [OK] Loaded into '{table_name}'")

            # ── [NEW] Insert success record into pipeline_metadata ──────────────
            with engine.connect() as conn:
                conn.execute(
                    text("""
                        INSERT INTO pipeline_metadata (filename, loaded_at, row_count, status)
                        VALUES (:filename, :loaded_at, :row_count, :status)
                    """),
                    {
                        "filename": file.name,
                        "loaded_at": datetime.now(timezone.utc).isoformat(),
                        "row_count": len(df),
                        "status": "success"
                    }
                )
                conn.commit()
            logger.info(f"  [META] Recorded '{file.name}' in pipeline_metadata")

            success_count += 1

        except Exception as e:
            # Log the error but continue to the next file
            logger.error(f"  [FAILED] {file.name}: {e}")

            # ── [NEW] Insert failure record into pipeline_metadata ──────────────
            # Tracking failed attempts helps with debugging and audit trails.
            try:
                with engine.connect() as conn:
                    conn.execute(
                        text("""
                            INSERT INTO pipeline_metadata (filename, loaded_at, row_count, status)
                            VALUES (:filename, :loaded_at, :row_count, :status)
                        """),
                        {
                            "filename": file.name,
                            "loaded_at": datetime.now(timezone.utc).isoformat(),
                            "row_count": 0,
                            "status": "failed"
                        }
                    )
                    conn.commit()
            except Exception as meta_err:
                logger.error(f"  [META] Could not record failure for '{file.name}': {meta_err}")

            error_count += 1

    # ── Summary ────────────────────────────────────────────────────────────────
    logger.info(f"\nPipeline complete — {success_count} loaded, {error_count} failed")


if __name__ == "__main__":
    run_pipeline()