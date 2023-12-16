import logging
import faktory
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')

with faktory.connection() as client:
    run_at = datetime.utcnow() + timedelta(minutes=1)
    run_at = run_at.isoformat()[:-7] + "Z"
    logging.info(f'run_at: {run_at}')
    
    # Queue job to crawl YouTube trending music
    client.queue("get_trending_music", at=run_at)
    client.queue("get_video_comments", at=run_at)
