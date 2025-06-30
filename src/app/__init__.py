# src/app/__init__.py
# Main application package

from src.scrape.job_scraper import JobScraper
from src.parse.llm_agent import LLMAgent
from src.database import VectorDatabase
from src.embed.embedding_service import EmbeddingService
from src.storage import DataStorage
from src.resume import ResumeProcessor
from src.matching import JobMatcher
from src.config import Config

class App:
    def __init__(self):
        """Initialize the main application with all services"""
        self.config = Config()
        self.job_scraper = JobScraper()
        self.llm_agent = LLMAgent()
        self.vector_db = VectorDatabase()
        self.embedding_service = EmbeddingService()
        self.data_storage = DataStorage()
        self.resume_processor = ResumeProcessor()
        self.job_matcher = JobMatcher()
    
    def run(self, user_location=None, max_jobs=None, job_boards=None, debug=None, storage_path=None):
        """Run the complete job matching pipeline"""
        print("Starting Job Matching Application...")

        # Get location from config
        user_location = user_location or self.config.get("USER_LOCATION")
        if not user_location:
            # Get from user input
            user_location = input("Enter your location: ")
            user_location = user_location.strip()
        
        # Get optional values with defaults
        job_boards = job_boards or self.config.get("JOB_BOARDS")
        max_jobs = max_jobs or self.config.get("MAX_JOBS")
        debug = debug or self.config.get("DEBUG")

        # Update config with runtime overrides
        self.config.update_from_args(
            user_location=user_location, 
            max_jobs=max_jobs, 
            job_boards=job_boards, 
            debug=debug,
            storage_path=storage_path
        )

        if self.config.get("DEBUG"):
            print(self.config.to_dict())
        
        # Get required values (will raise error if missing)
        try:
            api_key = self.config.get_required("OPENAI_API_KEY")
        except ValueError as e:
            print(f"Configuration error: {e}")
            return

        # Initialize storage
        self.storage = DataStorage(storage_path=storage_path)
        
        # TODO: Continue with actual implementation
        # Step 1: Scrape jobs from the specified location
        # jobs = self.job_scraper.scrape_jobs(user_location, job_boards)
        
        # Step 2-6: Process jobs with LLM and generate embeddings
        # processed_jobs = self.process_jobs(jobs)
        
        # Step 7-8: Process resume
        # resume_embedding = self.process_resume()
        
        # Step 9-10: Find and return matching jobs
        # matching_jobs = self.find_matching_jobs(resume_embedding, processed_jobs)
        
        return



app = App()