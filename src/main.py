#!/usr/bin/env python3
"""
Job Scraper Application

Main entry point for the job scraping application.
"""

from .cli import parse_args, validate_args
from .scraper import get_jobs, JOB_BOARDS
from .data_processor import clean_jobs, cosine_similarity
from .storage import (
    dump_list_of_dicts_to_json, 
    save_to_json, 
    generate_filename,
    load_job_database,
    merge_jobs_into_database,
    save_job_database,
    get_database_path,
    separate_jobs_by_embeddings,
    add_embeddings_to_jobs
)
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
    
    # Load existing job database
    print("Loading existing job database...")
    database_path = get_database_path(args.storage_path)
    existing_jobs = load_job_database(database_path)
    
    # Scrape jobs
    print(f"Scraping {args.results_wanted} jobs from {JOB_BOARDS} in {args.location}...")
    jobs_df = get_jobs(args.location, args.results_wanted, args.distance, args.debug, JOB_BOARDS)
    
    # Generate filename with timestamp for backup/historical purposes
    filename = generate_filename(args.storage_path)
    
    # Clean the jobs
    print("Cleaning job data...")
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
    new_jobs: List[Dict[str, Any]] = json.loads(jobs_json)
    
    print(f"Scraped {len(new_jobs)} new jobs")
    
    # Merge new jobs into the database
    print("Merging new jobs into database...")
    all_jobs, new_jobs_added = merge_jobs_into_database(existing_jobs, new_jobs)
    
    # Save updated database
    save_job_database(all_jobs, database_path)
    
    # Also save the current batch to timestamped file for historical purposes
    # dump_list_of_dicts_to_json(new_jobs, filename)
    # print(f"Current batch saved to {filename}")

    # Ask user whether to process only new jobs or all jobs
    if new_jobs_added > 0:
        print(f"\nYou have {new_jobs_added} new jobs and {len(all_jobs)} total jobs in the database.")
        choice = input("Process (n)ew jobs only or (a)ll jobs? [n]: ").lower().strip()
        
        if choice == 'a' or choice == 'all':
            jobs_to_analyze = all_jobs
            print(f"Processing all {len(all_jobs)} jobs...")
        else:
            # Filter to only new jobs for processing
            new_job_ids = {job.get('id') for job in new_jobs if job.get('id')}
            jobs_to_analyze = [job for job in all_jobs if job.get('id') in new_job_ids]
            print(f"Processing {len(jobs_to_analyze)} new jobs...")
    else:
        print("No new jobs found. Processing existing jobs from database...")
        jobs_to_analyze = all_jobs
    
    if not jobs_to_analyze:
        print("No jobs to process. Exiting...")
        return

    # Initialize the LLM client
    llm = LLM()

    # Conditionally extract job information using the LLM
    if args.process_jobs_with_llm:
        print("Extracting job information using LLM...")
        extracted_jobs = llm.extract_job_information(jobs_to_analyze)
        if args.debug:
            print("Extracted job information:")
            print(f"Sample extracted job: {extracted_jobs[0]}")
        
        # Use extracted jobs for processing
        jobs_to_process = extracted_jobs
    else:
        # Use original jobs for processing
        jobs_to_process = jobs_to_analyze

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

    # Separate jobs into those with and without embeddings
    print("Checking which jobs already have embeddings...")
    jobs_with_embeddings, jobs_without_embeddings = separate_jobs_by_embeddings(jobs_to_process)
    
    print(f"Found {len(jobs_with_embeddings)} jobs with existing embeddings")
    print(f"Need to compute embeddings for {len(jobs_without_embeddings)} jobs")

    # Generate embeddings only for jobs that don't have them
    new_job_embeddings = []
    if jobs_without_embeddings:
        print("Generating embeddings for new jobs...")
        new_job_embeddings = [llm.embed_text(str(job)) for job in jobs_without_embeddings]
        
        # Add embeddings to the jobs without embeddings
        jobs_without_embeddings = add_embeddings_to_jobs(jobs_without_embeddings, new_job_embeddings)
        
        if args.debug:
            print(f"Sample new job embedding: {new_job_embeddings[0][:5]}...")

    # Combine all jobs (those with existing embeddings + those with new embeddings)
    all_jobs_with_embeddings = jobs_with_embeddings + jobs_without_embeddings
    
    # Extract all embeddings for similarity calculation
    all_embeddings = [job['embedding'] for job in all_jobs_with_embeddings]

    # Calculate cosine similarity between resume and each job
    print("Calculating cosine similarity between resume and job embeddings...")
    similarities = []
    for job_embedding in all_embeddings:
        similarity = cosine_similarity(resume_embedding, job_embedding)
        similarities.append(similarity)

    # Add similarities to the jobs
    for job, similarity in zip(all_jobs_with_embeddings, similarities):
        job['similarity'] = similarity
    
    # Update the database with new embeddings (if any were computed)
    if jobs_without_embeddings:
        print("Updating database with new embeddings...")
        # Find and update jobs in all_jobs that got new embeddings
        jobs_dict = {job.get('id'): job for job in all_jobs_with_embeddings}
        updated_all_jobs = []
        
        for job in all_jobs:
            job_id = job.get('id')
            if job_id in jobs_dict:
                # Use the version with embedding and similarity
                updated_all_jobs.append(jobs_dict[job_id])
            else:
                # Keep the original job (shouldn't happen, but safety check)
                updated_all_jobs.append(job)
        
        # Save updated database with embeddings
        save_job_database(updated_all_jobs, database_path)

    # Convert to DataFrame for easier manipulation
    jobs_df = pd.DataFrame(all_jobs_with_embeddings)
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