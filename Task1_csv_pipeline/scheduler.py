import time
import logging
import schedule
from pipeline import run_pipeline

logger = logging.getLogger(__name__)

def run():
    """Wrapper that runs the full pipeline and logs start/end."""
    logger.info("Scheduled run starting...")
    run_pipeline()
    logger.info("Scheduled run complete.")

# Run every Monday at 08:00 AM

# schedule.every().monday.at("08:00").do(run)

# To test immediately, uncomment the line below:
schedule.every(1).minutes.do(run)

logger.info("Scheduler started. Waiting for next Monday at 08:00...")

while True:
    schedule.run_pending()  # Check if any job is due
    time.sleep(60)          # Wait 60 seconds before checking again