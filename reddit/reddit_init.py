import logging
import time
import faktory
from datetime import datetime, timedelta
from faktory import Worker
from dotenv import load_dotenv
import os

load_dotenv()
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')

# FAKTORY_URL = os.getenv('tcp://:social123@localhost:7419')

with faktory.connection() as client:
    run_at = datetime.utcnow() + timedelta(minutes=1)
    run_at = run_at.isoformat()[:-7] + "1"
    logging.info(f'run_at: {run_at}')
    
    # Queue job to crawl popular subreddits
    client.queue("crawl_subreddit", args=('music',), queue="crawl_subreddit", reserve_for=60, at=run_at)

    # Queue job to crawl new subreddits
    client.queue("crawl_subreddit", args=('MusicNews',), queue="crawl_subreddit", reserve_for=60, at=run_at)
    
    # Queue job to crawl new subreddits
    client.queue("crawl_subreddit", args=('LetsTalkMusic',), queue="crawl_subreddit", reserve_for=60, at=run_at)
    
    # Queue job to crawl new subreddits
    client.queue("crawl_subreddit", args=('WeAreTheMusicMakers',), queue="crawl_subreddit", reserve_for=60, at=run_at)
    
    # Queue job to crawl new subreddits
    client.queue("crawl_subreddit", args=('Listentothis',), queue="crawl_subreddit", reserve_for=60, at=run_at)
    
    # Queue job to crawl new subreddits
    client.queue("crawl_subreddit", args=('ElectronicMusic',), queue="crawl_subreddit", reserve_for=60, at=run_at)
