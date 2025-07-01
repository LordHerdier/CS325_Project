#!/usr/bin/env python3
"""
Job Scraper Application

Main entry point for the job scraping application.
"""

from .cli import parse_args, validate_args
from .scraper import get_jobs, JOB_BOARDS
from .data_processor import clean_jobs
from .storage import save_to_json, generate_filename


def main():
    """Main application entry point."""
    # Parse and validate command line arguments
    args = parse_args()
    args = validate_args(args)
    
    # Scrape jobs
    print(f"Scraping {args.results_wanted} jobs from {JOB_BOARDS} in {args.location}...")
    jobs = get_jobs(args.location, args.results_wanted, args.distance, args.debug, JOB_BOARDS)
    
    # Generate filename with timestamp
    filename = generate_filename(args.storage_path)
    
    # Clean the jobs
    print("Cleaning job data...")
    jobs = clean_jobs(jobs)
    
    # Save the jobs
    print(f"Saving jobs to {filename}...")
    save_to_json(jobs, filename)
    print(f"Jobs saved to {filename}")


if __name__ == "__main__":
    main() 