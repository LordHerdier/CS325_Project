#!/usr/bin/env python3
"""
Job Scraper Application

Main entry point for the job scraping application.
"""

from .cli import parse_args, validate_args
from .scraper import get_jobs, JOB_BOARDS
from .data_processor import clean_jobs, cosine_similarity
from .storage import dump_list_of_dicts_to_json, save_to_json, generate_filename
from .llm import LLM
import pandas as pd
import numpy as np
from typing import List, Dict, Any
import json

def main():
    """Main application entry point."""
    # Parse and validate command line arguments
    args = parse_args()
    args = validate_args(args)
    
    # Scrape jobs
    print(f"Scraping {args.results_wanted} jobs from {JOB_BOARDS} in {args.location}...")
    jobs_df = get_jobs(args.location, args.results_wanted, args.distance, args.debug, JOB_BOARDS)
    
    # Generate filename with timestamp
    filename = generate_filename(args.storage_path)
    
    # Clean the jobs
    # print("Cleaning job data...")
    jobs_df = clean_jobs(jobs_df)

    # Convert DataFrame to JSON and back to ensure type consistency
    # This is a workaround for the issue where pandas DataFrame can cause type inconsistencies
    # 1. Dump it to JSON
    jobs_json = jobs_df.to_json(orient="records")

    # 2. Delete the original DataFrame to make absolutely sure there's not some type-related issue
    del jobs_df

    # 3. Load it back as a list of dicts using json.loads with explicit type
    if jobs_json is None:
        raise ValueError("Failed to convert jobs DataFrame to JSON")
    jobs: List[Dict[str, Any]] = json.loads(jobs_json)
    
    # print(f'Type of jobs: {type(jobs)}')

    # Initialize the LLM client
    llm = LLM()

    # Conditionally extract job information using the LLM
    if args.process_jobs_with_llm:
        print("Extracting job information using LLM...")
        extracted_jobs = llm.extract_job_information(jobs)
        if args.debug:
            print("Extracted job information:")
            print(f"Sample extracted job: {extracted_jobs[0]}")
        
        # Use extracted jobs for processing
        jobs_to_process = extracted_jobs
    else:
        # Use original jobs for processing
        jobs_to_process = jobs

    # Dump to file
    # dump_list_of_dicts_to_json(extracted_jobs, filename)
    # print(f"Jobs saved to {filename}")

    # Load resume
    with open(args.resume, 'r') as file:
        resume_text = file.read()

    # Extract resume information using the LLM
    print("Extracting resume information using LLM...")
    resume_info = llm.extract_resume_information(resume_text)
    if args.debug:
        print("Extracted resume information:")
        print(resume_info)

    # Embed the resume text
    print("Generating embeddings for resume information...")
    resume_embedding = llm.embed_text(resume_text)
    if args.debug:
        print(f"Resume embedding: {resume_embedding[:5]}...")

    # Embed the jobs
    print("Generating embeddings for job information...")
    job_embeddings = [llm.embed_text(str(job)) for job in jobs_to_process]

    if args.debug:
        print(f"Sample job embedding: {job_embeddings[0][:5]}...")

    # Calculate cosine similarity between resume and each job
    print("Calculating cosine similarity between resume and job embeddings...")
    similarities = []
    for job_embedding in job_embeddings:
        similarity = cosine_similarity(resume_embedding, job_embedding)
        similarities.append(similarity)

    # Add similarities to the extracted jobs
    for job, similarity in zip(jobs_to_process, similarities):
        job['similarity'] = similarity

    # Convert to DataFrame for easier manipulation
    jobs_df = pd.DataFrame(jobs_to_process)
    if args.debug:
        print("Sample jobs DataFrame:")
        print(jobs_df.head())

    # Sort jobs by similarity
    jobs_df = jobs_df.sort_values(by='similarity', ascending=False)
    print("Jobs sorted by similarity to resume.")

    # Save the sorted jobs to JSON
    sorted_filename = f"sorted_{filename}"
    save_to_json(jobs_df, sorted_filename)
    print(f"Sorted jobs saved to {sorted_filename}")

    # Print the top 10 jobs
    print("Top 10 jobs based on similarity:")
    for index, job in jobs_df.head(10).iterrows():
        print(f"Job Title: {job['title']}, Similarity: {job['similarity']:.4f}")
        # print(f"Company: {job['company']}, Location: {job['location']}")
        print()
    

if __name__ == "__main__":
    main() 