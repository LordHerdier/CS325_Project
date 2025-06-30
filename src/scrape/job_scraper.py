# src/scrape/job_scraper.py
# Job scraping services

class JobScraper:
    def __init__(self):
        """Initialize job scraper"""
        self.supported_boards = [] # Probably load this from the .env file
    
    def scrape_jobs(self, location, job_boards=None):
        """Scrape jobs from specified job boards in user's area"""
        # TODO: Implement job scraping logic
        pass
    
    def parse_job_posting(self, raw_posting):
        """Parse individual job posting"""
        # TODO: Implement job posting parsing
        # Might put this in the parse module, not sure yet
        pass 