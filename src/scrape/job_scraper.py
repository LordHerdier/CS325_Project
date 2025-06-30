# src/scrape/job_scraper.py
# Job scraping services

from jobspy import scrape_jobs
from src.config import config
from pandas import DataFrame, concat

class JobScraper:
    def __init__(self):
        """Initialize job scraper"""
        # Get config values
        self.debug = config.get("DEBUG")
        self.location = config.get("USER_LOCATION")
        self.job_boards = config.get("JOB_BOARDS")
        self.max_jobs = config.get("MAX_JOBS")

        self.jobs = DataFrame()

    def scrape_jobs(self):
        """Scrape jobs from specified job boards in user's area"""

        if config.get("DEBUG"):
            print(f"Scraping jobs from {self.job_boards} in {self.location} with {self.max_jobs} results wanted")

        self.jobs = scrape_jobs(
            site_name=self.job_boards,
            location=self.location,
            results_wanted=self.max_jobs,
            verbose=1
        )
        if config.get("DEBUG"):
            print(f"Scraped {len(self.jobs)} jobs from {self.job_boards}")
            print(self.jobs.head())

    def save_jobs(self):
        """Save jobs to CSV file"""
        self.jobs.to_csv(f"{self.storage_path}/jobs.csv", index=False)

    def _get_all_jobs(self):
        """Get all jobs stored in memory"""
        return self.jobs