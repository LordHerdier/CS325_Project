import pandas as pd
from jobspy import scrape_jobs
from typing import List, Union
import time
import random
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

JOB_BOARDS = ["indeed"] # The api supports more, but we're only using indeed for this project
BATCH_SIZE = 20
MIN_DELAY = 1.0  # Minimum delay between requests in seconds
MAX_DELAY = 3.0  # Maximum delay between requests in seconds
MAX_RETRIES = 3  # Maximum number of retry attempts


@retry(
    stop=stop_after_attempt(MAX_RETRIES),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((ConnectionError, TimeoutError, Exception))
)
def _scrape_jobs(location: str, results_wanted: int, distance: int, offset: int, debug: bool, site_name: Union[str, List[str]]) -> pd.DataFrame:
    """Internal function to scrape jobs using jobspy with retry logic."""
    try:
        print(f"Scraping batch: offset={offset}, results_wanted={results_wanted}")
        result = scrape_jobs(
            location=location,
            results_wanted=results_wanted,
            distance=distance,
            debug=debug,
            site_name=site_name,
            offset=offset
        )
        return result
    except Exception as e:
        print(f"Error scraping jobs (offset={offset}): {str(e)}")
        raise


def _rate_limit_delay():
    """Apply rate limiting delay between requests."""
    delay = random.uniform(MIN_DELAY, MAX_DELAY)
    print(f"Rate limiting: waiting {delay:.2f} seconds...")
    time.sleep(delay)


def get_jobs(location: str, results_wanted: int, distance: int, debug: bool, site_name: Union[str, List[str]]) -> pd.DataFrame:
    """
    Scrape jobs from the specified job board.
    
    If results_wanted is greater than BATCH_SIZE, scrapes in batches with rate limiting.
    Includes automatic retries for failed requests.
    
    Args:
        location: Location to search for jobs
        results_wanted: Number of jobs to scrape
        distance: Distance from location to search
        debug: Enable debug mode
        site_name: Job board(s) to scrape from
        
    Returns:
        DataFrame containing scraped jobs
    """
    if results_wanted > BATCH_SIZE:
        print(f"Results wanted is greater than {BATCH_SIZE}, scraping in batches of {BATCH_SIZE}")
        jobs = []
        batch_count = 0
        
        for i in range(0, results_wanted, BATCH_SIZE):
            # Apply rate limiting between batches (but not before the first batch)
            if batch_count > 0:
                _rate_limit_delay()
            
            try:
                batch_jobs = _scrape_jobs(location, BATCH_SIZE, distance, i, debug, site_name)
                if batch_jobs is not None and not batch_jobs.empty:
                    jobs.append(batch_jobs)
                    print(f"Successfully scraped batch {batch_count + 1}, got {len(batch_jobs)} jobs")
                else:
                    print(f"Batch {batch_count + 1} returned no jobs")
                
                batch_count += 1
                
            except Exception as e:
                print(f"Failed to scrape batch {batch_count + 1} after {MAX_RETRIES} retries: {str(e)}")
                batch_count += 1
                continue
        
        if jobs:
            combined_df = pd.concat(jobs, ignore_index=True)
            print(f"Total jobs scraped: {len(combined_df)}")
            return combined_df
        else:
            print("No jobs were successfully scraped")
            return pd.DataFrame()
    else:
        print(f"Results wanted is less than or equal to {BATCH_SIZE}, scraping in one batch")
        try:
            return _scrape_jobs(location, results_wanted, distance, 0, debug, site_name)
        except Exception as e:
            print(f"Failed to scrape jobs after {MAX_RETRIES} retries: {str(e)}")
            return pd.DataFrame()