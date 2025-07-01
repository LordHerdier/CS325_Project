#!/usr/bin/env python3
"""
Job Scraper Application

Main entry point for the job scraping application.
"""

from .cli import parse_args, validate_args
from .scraper import get_jobs, JOB_BOARDS
from .data_processor import clean_jobs
from .storage import dump_list_of_dicts_to_json, save_to_json, generate_filename
from .llm import LLM
import pandas as pd
import numpy as np
from typing import List, Dict, Any
import json

# Panda dataframes make me want to kill myself :)


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

    # Okay because panda dataframes are just sooooooo great, here's a hack to convert it to a list of dicts
    # (i've spent more time trying to figure out how to convert a panda dataframe to a list of dicts than I have on the rest of this project. fuck pandas)
    # (trust me, it should be super simple. It's not. They even have a built in function to do it for you! That gives you the wrong python type! Literally wtf pandas)

    # 1. Dump it to JSON
    jobs_json = jobs.to_json(orient="records")

    # 2. Delete the original DataFrame to make absolutely sure there's not some type-fuckery going on here
    del jobs

    # 3. Load it back as a list of dicts using json.loads with explicit type
    jobs: List[Dict[str, Any]] = json.loads(jobs_json)
    
    print(f'Type of jobs: {type(jobs)}')

    # Initialize the LLM client
    llm = LLM()

    # Extract job information using the LLM
    print("Extracting job information using LLM...")
    extracted_jobs = llm.extract_job_information(jobs)
    if args.debug:
        print("Extracted job information:")
        print(f"Sample extracted job: {extracted_jobs[0]}")

    # Dump to file
    dump_list_of_dicts_to_json(extracted_jobs, filename)
    print(f"Jobs saved to {filename}")

if __name__ == "__main__":
    main() 