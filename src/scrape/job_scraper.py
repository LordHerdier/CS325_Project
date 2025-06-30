# src/scrape/job_scraper.py
# Job scraping services

from jobspy import scrape_jobs
from src.config import config
from pandas import DataFrame
from src.storage import DataStorage

class JobScraper:
    def __init__(self, storage: DataStorage):
        """Initialize job scraper"""
        # Get config values
        self.debug = config.get("DEBUG", False)
        self.location = config.get("USER_LOCATION")
        self.job_boards = config.get("JOB_BOARDS")
        self.max_jobs = config.get("MAX_JOBS")

        self.jobs = DataFrame()
        self.storage = storage
    def scrape_jobs(self):
        """Scrape jobs from specified job boards in user's area"""

        if self.debug:
            print(f"Scraping jobs from {self.job_boards} in {self.location} with {self.max_jobs} results wanted")

        self.jobs = scrape_jobs(
            site_name=self.job_boards,
            location=self.location,
            results_wanted=self.max_jobs,
            verbose=self.debug
        )
        if self.debug:
            print(f"Scraped {len(self.jobs)} jobs from {self.job_boards}")
            print(self.jobs.head())

    def dataframe_to_json(self):
        """Convert jobs dataframe to JSON"""
        if self.debug:
            print("Converting jobs dataframe to JSON")
        return self.jobs.to_json(orient="records")

    def save_jobs(self):
        """Save jobs to storage"""
        if self.debug:
            print(f"Saving {len(self.jobs)} jobs to storage")
        self.storage.save_data(self.dataframe_to_json(), "jobs")
        if self.debug:
            print("Jobs saved to storage")

    def get_jobs(self):
        """Get all jobs stored in memory"""
        if self.debug:
            print("Getting jobs from memory")
        return self.jobs
    
    def get_jobs_from_storage(self):
        """Get all jobs stored in storage"""
        if self.debug:
            print("Getting jobs from storage")
        return self.storage.load_data("jobs")
    
    def get_all_jobs(self):
        """Get all jobs stored in memory or storage"""
        if self.jobs.empty:
            if self.debug:
                print("No jobs in memory, loading from storage")
            return self.get_jobs_from_storage()
        else:
            if self.debug:
                print("Jobs in memory, returning them")
        return self.jobs