import pandas as pd
from jobspy import scrape_jobs
from typing import List, Union

JOB_BOARDS = ["indeed"] # The api supports more, but we're only using indeed for this project
BATCH_SIZE = 20


def _scrape_jobs(location: str, results_wanted: int, distance: int, debug: bool, site_name: Union[str, List[str]]) -> pd.DataFrame:
    """Internal function to scrape jobs using jobspy."""
    return scrape_jobs(
        location=location,
        results_wanted=results_wanted,
        distance=distance,
        debug=debug,
        site_name=site_name
    )


def get_jobs(location: str, results_wanted: int, distance: int, debug: bool, site_name: Union[str, List[str]]) -> pd.DataFrame:
    """
    Scrape jobs from the specified job board.
    
    If results_wanted is greater than BATCH_SIZE, scrapes in batches.
    
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
        for i in range(0, results_wanted, BATCH_SIZE):
            batch_jobs = _scrape_jobs(location, BATCH_SIZE, distance, debug, site_name)
            jobs.extend(batch_jobs)
        return pd.DataFrame(jobs)
    else:
        print(f"Results wanted is less than {BATCH_SIZE}, scraping in one batch")
        return _scrape_jobs(location, results_wanted, distance, debug, site_name) 