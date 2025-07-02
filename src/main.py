#!/usr/bin/env python3
"""
Job Scraper Application

Main entry point for the job scraping application.
"""

from .cli import (
    parse_args, validate_args, show_main_menu, get_scraping_config,
    get_query_config, get_export_config, show_settings_menu
)
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
from typing import List, Dict, Any, Optional
import json
import os


def scrape_jobs(config: Dict[str, Any]) -> None:
    """Scrape new jobs and add them to the database."""
    print("\n" + "="*50)
    print("           SCRAPING JOBS")
    print("="*50)
    
    # Load existing job database
    print("Loading existing job database...")
    database_path = get_database_path(config.get('storage_path', 'storage'))
    existing_jobs = load_job_database(database_path)
    
    # Scrape jobs
    print(f"Scraping {config['results_wanted']} jobs from {JOB_BOARDS} in {config['location']}...")
    jobs_df = get_jobs(
        config['location'], 
        config['results_wanted'], 
        config['distance'], 
        config.get('debug', False), 
        JOB_BOARDS
    )
    
    # Clean the jobs
    print("Cleaning job data...")
    jobs_df = clean_jobs(jobs_df)

    # Convert DataFrame to JSON and back to ensure type consistency
    jobs_json = jobs_df.to_json(orient="records")
    del jobs_df

    if jobs_json is None:
        raise ValueError("Failed to convert jobs DataFrame to JSON")
    new_jobs: List[Dict[str, Any]] = json.loads(jobs_json)
    
    print(f"Scraped {len(new_jobs)} new jobs")
    
    # Merge new jobs into the database
    print("Merging new jobs into database...")
    all_jobs, new_jobs_added = merge_jobs_into_database(existing_jobs, new_jobs)
    
    # Save updated database
    save_job_database(all_jobs, database_path)
    
    print(f"✅ Successfully added {new_jobs_added} new jobs to database")
    print(f"📊 Total jobs in database: {len(all_jobs)}")
    
    # Process jobs if requested
    if new_jobs_added > 0:
        process_choice = input(f"\nProcess the {new_jobs_added} new jobs with your resume? (y/N): ").strip().lower()
        if process_choice in ['y', 'yes']:
            # Filter to only new jobs for processing
            new_job_ids = {job.get('id') for job in new_jobs if job.get('id')}
            jobs_to_analyze = [job for job in all_jobs if job.get('id') in new_job_ids]
            _process_jobs_with_resume(jobs_to_analyze, config, database_path, all_jobs)


def query_database(config: Dict[str, Any]) -> None:
    """Query the existing database and show results."""
    print("\n" + "="*50)
    print("           QUERYING DATABASE")
    print("="*50)
    
    # Load job database
    database_path = get_database_path(config.get('storage_path', 'storage'))
    all_jobs = load_job_database(database_path)
    
    if not all_jobs:
        print("❌ No jobs found in database. Please scrape some jobs first.")
        return
    
    print(f"📊 Found {len(all_jobs)} jobs in database")
    
    # Process jobs with resume
    _process_jobs_with_resume(all_jobs, config, database_path, all_jobs)


def view_top_matches(config: Dict[str, Any]) -> None:
    """View top job matches from the database."""
    print("\n" + "="*50)
    print("           TOP JOB MATCHES")
    print("="*50)
    
    # Load job database
    database_path = get_database_path(config.get('storage_path', 'storage'))
    all_jobs = load_job_database(database_path)
    
    if not all_jobs:
        print("❌ No jobs found in database. Please scrape some jobs first.")
        return
    
    # Check if jobs have similarity scores
    jobs_with_similarity = [job for job in all_jobs if 'similarity' in job]
    
    if not jobs_with_similarity:
        print("❌ No similarity scores found. Please process jobs with your resume first.")
        return
    
    # Convert to DataFrame and sort
    jobs_df = pd.DataFrame(jobs_with_similarity)
    jobs_df = jobs_df.sort_values(by='similarity', ascending=False)
    
    # Apply filters
    if config.get('min_similarity'):
        jobs_df = jobs_df[jobs_df['similarity'] >= config['min_similarity']]
        print(f"🔍 Filtered to jobs with similarity >= {config['min_similarity']}")
    
    # Show top matches
    top_n = config.get('show_top', 10)
    top_jobs = jobs_df.head(top_n)
    
    print(f"\n🏆 Top {len(top_jobs)} job matches:")
    print("-" * 80)
    
    for index, job in top_jobs.iterrows():
        print(f"📋 {job['title']}")
        print(f"   🏢 Company: {job.get('company', 'N/A')}")
        print(f"   📍 Location: {job.get('location', 'N/A')}")
        print(f"   🎯 Similarity: {job['similarity']:.4f}")
        if job.get('url'):
            print(f"   🔗 URL: {job['url']}")
        print("-" * 80)


def show_database_stats(config: Dict[str, Any]) -> None:
    """Show statistics about the job database."""
    print("\n" + "="*50)
    print("         DATABASE STATISTICS")
    print("="*50)
    
    # Load job database
    database_path = get_database_path(config.get('storage_path', 'storage'))
    all_jobs = load_job_database(database_path)
    
    if not all_jobs:
        print("❌ No jobs found in database.")
        return
    
    print(f"📊 Total jobs: {len(all_jobs)}")
    
    # Jobs with embeddings
    jobs_with_embeddings = [job for job in all_jobs if 'embedding' in job]
    print(f"🧠 Jobs with embeddings: {len(jobs_with_embeddings)}")
    
    # Jobs with similarity scores
    jobs_with_similarity = [job for job in all_jobs if 'similarity' in job]
    print(f"🎯 Jobs with similarity scores: {len(jobs_with_similarity)}")
    
    if jobs_with_similarity:
        similarities = [job['similarity'] for job in jobs_with_similarity]
        print(f"📈 Average similarity: {np.mean(similarities):.4f}")
        print(f"📊 Max similarity: {np.max(similarities):.4f}")
        print(f"📉 Min similarity: {np.min(similarities):.4f}")
    
    # Company distribution
    companies = [job.get('company', 'Unknown') for job in all_jobs if job.get('company')]
    if companies:
        company_counts = pd.Series(companies).value_counts()
        print(f"\n🏢 Top 5 companies:")
        for company, count in company_counts.head(5).items():
            print(f"   {company}: {count} jobs")
    
    # Location distribution
    locations = [job.get('location', 'Unknown') for job in all_jobs if job.get('location')]
    if locations:
        location_counts = pd.Series(locations).value_counts()
        print(f"\n📍 Top 5 locations:")
        for location, count in location_counts.head(5).items():
            print(f"   {location}: {count} jobs")


def export_results(config: Dict[str, Any]) -> None:
    """Export job results to file."""
    print("\n" + "="*50)
    print("           EXPORTING RESULTS")
    print("="*50)
    
    # Load job database
    database_path = get_database_path(config.get('storage_path', 'storage'))
    all_jobs = load_job_database(database_path)
    
    if not all_jobs:
        print("❌ No jobs found in database.")
        return
    
    # Filter jobs with similarity scores if available
    jobs_with_similarity = [job for job in all_jobs if 'similarity' in job]
    
    if jobs_with_similarity:
        # Sort by similarity
        jobs_df = pd.DataFrame(jobs_with_similarity)
        jobs_df = jobs_df.sort_values(by='similarity', ascending=False)
        
        # Limit to top N if specified
        if config.get('top_n'):
            jobs_df = jobs_df.head(config['top_n'])
            print(f"📊 Exporting top {len(jobs_df)} jobs")
        else:
            print(f"📊 Exporting all {len(jobs_df)} jobs with similarity scores")
    else:
        jobs_df = pd.DataFrame(all_jobs)
        print(f"📊 Exporting all {len(jobs_df)} jobs (no similarity scores)")
    
    # Export based on format
    try:
        if config['format'] == 'json':
            jobs_df.to_json(config['filename'], orient='records', indent=2)
        elif config['format'] == 'csv':
            jobs_df.to_csv(config['filename'], index=False)
        elif config['format'] == 'excel':
            jobs_df.to_excel(config['filename'], index=False)
        
        print(f"✅ Successfully exported to {config['filename']}")
        
    except Exception as e:
        print(f"❌ Error exporting data: {e}")


def _process_jobs_with_resume(jobs_to_analyze: List[Dict[str, Any]], config: Dict[str, Any], 
                            database_path: str, all_jobs: List[Dict[str, Any]]) -> None:
    """Helper function to process jobs with resume similarity."""
    if not jobs_to_analyze:
        print("No jobs to process.")
        return

    # Load resume
    with open(config['resume'], 'r') as file:
        resume_text = file.read()

    # Initialize the LLM client
    llm = LLM()

    # Process jobs with LLM if requested
    if config.get('process_jobs_with_llm'):
        print("Extracting job information using LLM...")
        jobs_to_analyze = llm.extract_job_information(jobs_to_analyze)
        if config.get('debug'):
            print("Extracted job information:")
            print(f"Sample extracted job: {jobs_to_analyze[0]}")

    # Extract resume information using the LLM
    print("Extracting resume information using LLM...")
    resume_info = llm.extract_resume_information(resume_text)
    if config.get('debug'):
        print("Extracted resume information:")
        print(resume_info)

    # Embed the resume text
    print("Generating embeddings for resume information...")
    resume_embedding = llm.embed_text(resume_text)
    if config.get('debug'):
        print(f"Resume embedding: {resume_embedding[:5]}...")

    # Separate jobs into those with and without embeddings
    print("Checking which jobs already have embeddings...")
    jobs_with_embeddings, jobs_without_embeddings = separate_jobs_by_embeddings(jobs_to_analyze)
    
    print(f"Found {len(jobs_with_embeddings)} jobs with existing embeddings")
    print(f"Need to compute embeddings for {len(jobs_without_embeddings)} jobs")

    # Generate embeddings only for jobs that don't have them
    if jobs_without_embeddings:
        print("Generating embeddings for new jobs...")
        new_job_embeddings = [llm.embed_text(str(job)) for job in jobs_without_embeddings]
        jobs_without_embeddings = add_embeddings_to_jobs(jobs_without_embeddings, new_job_embeddings)
        
        if config.get('debug'):
            print(f"Sample new job embedding: {new_job_embeddings[0][:5]}...")

    # Combine all jobs with embeddings
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
    
    # Update the database with new embeddings and similarities
    print("Updating database with embeddings and similarities...")
    jobs_dict = {job.get('id'): job for job in all_jobs_with_embeddings}
    updated_all_jobs = []
    
    for job in all_jobs:
        job_id = job.get('id')
        if job_id in jobs_dict:
            # Use the version with embedding and similarity
            updated_all_jobs.append(jobs_dict[job_id])
        else:
            # Keep the original job
            updated_all_jobs.append(job)
    
    # Save updated database
    save_job_database(updated_all_jobs, database_path)

    # Show top results
    jobs_df = pd.DataFrame(all_jobs_with_embeddings)
    jobs_df = jobs_df.sort_values(by='similarity', ascending=False)
    
    print(f"\n🏆 Top {min(5, len(jobs_df))} jobs based on similarity:")
    print("-" * 60)
    
    for index, job in jobs_df.head(5).iterrows():
        print(f"📋 {job['title']}")
        print(f"   🏢 Company: {job.get('company', 'N/A')}")
        print(f"   🎯 Similarity: {job['similarity']:.4f}")
        print("-" * 60)


def run_interactive_mode() -> None:
    """Run the application in interactive mode with menu system."""
    print("🚀 Welcome to Job Scraper!")
    print("Interactive mode - use the menu to navigate")
    
    # Global settings
    settings = {'storage_path': 'storage'}
    
    while True:
        try:
            choice = show_main_menu()
            
            if choice == '1':  # Scrape new jobs
                config = get_scraping_config()
                config.update(settings)
                scrape_jobs(config)
                
            elif choice == '2':  # Query existing database
                config = get_query_config()
                config.update(settings)
                query_database(config)
                
            elif choice == '3':  # View top job matches
                config = get_query_config()
                config.update(settings)
                view_top_matches(config)
                
            elif choice == '4':  # Database statistics
                show_database_stats(settings)
                
            elif choice == '5':  # Export results
                config = get_export_config()
                config.update(settings)
                export_results(config)
                
            elif choice == '6':  # Settings
                new_settings = show_settings_menu()
                settings.update(new_settings)
                print("✅ Settings updated!")
                
            elif choice == '7':  # Exit
                print("👋 Thank you for using Job Scraper!")
                break
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
            print("Please try again or contact support.")


def main():
    """Main application entry point."""
    args = parse_args()
    
    # Check if running in interactive mode (default)
    if args.interactive and not args.mode:
        run_interactive_mode()
        return
    
    # Non-interactive mode - validate args and run specific operation
    args = validate_args(args)
    
    if args.mode == 'scrape':
        config = {
            'location': args.location,
            'results_wanted': args.results_wanted,
            'distance': args.distance,
            'resume': args.resume,
            'process_jobs_with_llm': args.process_jobs_with_llm,
            'debug': args.debug,
            'storage_path': args.storage_path
        }
        scrape_jobs(config)
        
    elif args.mode == 'query':
        config = {
            'resume': args.resume,
            'show_top': args.show_top,
            'debug': args.debug,
            'storage_path': args.storage_path
        }
        query_database(config)
        
    elif args.mode == 'export':
        config = get_export_config()
        config['storage_path'] = args.storage_path
        export_results(config)
        
    else:
        # Default to interactive mode if no specific mode is provided
        run_interactive_mode()


if __name__ == "__main__":
    main() 