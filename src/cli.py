#!/usr/bin/env python3
"""
CLI Module for Job Scraper Application

Provides interactive menu system and argument parsing.
"""

import argparse
import os
from typing import Optional, Dict, Any

STORAGE_PATH = "storage"


def show_main_menu() -> str:
    """Display the main menu and get user choice."""
    print("\n" + "="*50)
    print("           JOB SCRAPER MENU")
    print("="*50)
    print("1. Scrape new jobs")
    print("2. Query existing database")
    print("3. View top job matches")
    print("4. Database statistics")
    print("5. Export results")
    print("6. Settings")
    print("7. Exit")
    print("-"*50)
    
    while True:
        choice = input("Enter your choice (1-7): ").strip()
        if choice in ['1', '2', '3', '4', '5', '6', '7']:
            return choice
        print("Invalid choice. Please enter a number between 1 and 7.")


def get_scraping_config() -> Dict[str, Any]:
    """Get configuration for scraping jobs."""
    print("\n" + "="*40)
    print("         SCRAPING CONFIGURATION")
    print("="*40)
    
    config = {}
    
    # Get location
    config['location'] = input("Enter location for job search: ").strip()
    while not config['location']:
        config['location'] = input("Location cannot be empty. Please enter location: ").strip()
    
    # Get number of results
    while True:
        try:
            results = input("Number of jobs to scrape (default: 50): ").strip()
            config['results_wanted'] = int(results) if results else 50
            if config['results_wanted'] > 0:
                break
            print("Please enter a positive number.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Get distance
    while True:
        try:
            distance = input("Search distance in miles (default: 25): ").strip()
            config['distance'] = int(distance) if distance else 25
            if config['distance'] >= 0:
                break
            print("Please enter a non-negative number.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Get resume path
    while True:
        resume_path = input("Path to your resume file: ").strip()
        if os.path.exists(resume_path):
            config['resume'] = resume_path
            break
        print(f"File not found: {resume_path}. Please enter a valid path.")
    
    # LLM processing option
    llm_choice = input("Process jobs with LLM for better extraction? (y/N): ").strip().lower()
    config['process_jobs_with_llm'] = llm_choice in ['y', 'yes']
    
    # Debug mode
    debug_choice = input("Enable debug mode? (y/N): ").strip().lower()
    config['debug'] = debug_choice in ['y', 'yes']
    
    return config


def get_query_config() -> Dict[str, Any]:
    """Get configuration for querying the database."""
    print("\n" + "="*40)
    print("         DATABASE QUERY")
    print("="*40)
    
    config = {}
    
    # Get resume path for similarity comparison
    while True:
        resume_path = input("Path to your resume file: ").strip()
        if os.path.exists(resume_path):
            config['resume'] = resume_path
            break
        print(f"File not found: {resume_path}. Please enter a valid path.")
    
    # Get number of top results to show
    while True:
        try:
            top_n = input("Number of top matches to show (default: 10): ").strip()
            config['show_top'] = int(top_n) if top_n else 10
            if config['show_top'] > 0:
                break
            print("Please enter a positive number.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Filter options
    print("\nOptional filters:")
    config['min_similarity'] = None
    min_sim = input("Minimum similarity score (0.0-1.0, default: none): ").strip()
    if min_sim:
        try:
            config['min_similarity'] = float(min_sim)
            if not (0.0 <= config['min_similarity'] <= 1.0):
                print("Similarity score should be between 0.0 and 1.0. Ignoring filter.")
                config['min_similarity'] = None
        except ValueError:
            print("Invalid similarity score. Ignoring filter.")
    
    # Debug mode
    debug_choice = input("Enable debug mode? (y/N): ").strip().lower()
    config['debug'] = debug_choice in ['y', 'yes']
    
    return config


def get_export_config() -> Dict[str, Any]:
    """Get configuration for exporting results."""
    print("\n" + "="*40)
    print("         EXPORT CONFIGURATION")
    print("="*40)
    
    config = {}
    
    # Export format
    print("Export formats:")
    print("1. JSON")
    print("2. CSV")
    print("3. Excel")
    
    while True:
        choice = input("Choose export format (1-3): ").strip()
        if choice == '1':
            config['format'] = 'json'
            config['extension'] = '.json'
            break
        elif choice == '2':
            config['format'] = 'csv'
            config['extension'] = '.csv'
            break
        elif choice == '3':
            config['format'] = 'excel'
            config['extension'] = '.xlsx'
            break
        print("Invalid choice. Please enter 1, 2, or 3.")
    
    # Number of top results to export
    while True:
        try:
            top_n = input("Number of top jobs to export (default: all): ").strip()
            config['top_n'] = int(top_n) if top_n else None
            if config['top_n'] is None or config['top_n'] > 0:
                break
            print("Please enter a positive number.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Custom filename
    default_name = f"job_matches_{config['format']}"
    filename = input(f"Filename (default: {default_name}): ").strip()
    config['filename'] = filename if filename else default_name
    
    # Add extension if not present
    if not config['filename'].endswith(config['extension']):
        config['filename'] += config['extension']
    
    return config


def show_settings_menu() -> Dict[str, Any]:
    """Show settings configuration menu."""
    print("\n" + "="*40)
    print("            SETTINGS")
    print("="*40)
    
    config = {}
    
    # Storage path
    current_storage = STORAGE_PATH
    storage_path = input(f"Storage path (current: {current_storage}): ").strip()
    config['storage_path'] = storage_path if storage_path else current_storage
    
    # Create storage directory if it doesn't exist
    if not os.path.exists(config['storage_path']):
        create = input(f"Storage path doesn't exist. Create '{config['storage_path']}'? (Y/n): ").strip().lower()
        if create not in ['n', 'no']:
            try:
                os.makedirs(config['storage_path'], exist_ok=True)
                print(f"Created directory: {config['storage_path']}")
            except Exception as e:
                print(f"Error creating directory: {e}")
                config['storage_path'] = STORAGE_PATH
    
    return config


def parse_args() -> argparse.Namespace:
    """Parse command line arguments for non-interactive mode."""
    parser = argparse.ArgumentParser(description="Job Scraper - Interactive and CLI modes")
    parser.add_argument("--interactive", action="store_true", default=True, 
                       help="Run in interactive mode (default)")
    parser.add_argument("--location", type=str, help="User location for job search")
    parser.add_argument("--results-wanted", type=int, help="Maximum number of jobs to process")
    parser.add_argument("--show-top", type=int, default=10, help="Number of top jobs to display")
    parser.add_argument("--distance", type=int, help="Distance from user location to search for jobs")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--resume", type=str, help="Path to the user's resume file")
    parser.add_argument("--storage-path", type=str, default=STORAGE_PATH, help="Path to store the jobs")
    parser.add_argument("--process-jobs-with-llm", action="store_true", 
                       help="Enable LLM processing of job information")
    parser.add_argument("--mode", choices=['scrape', 'query', 'export'], 
                       help="Non-interactive mode operation")
    
    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> argparse.Namespace:
    """Validate and prompt for missing arguments in non-interactive mode."""
    if not args.interactive and args.mode == 'scrape':
        if args.location is None:
            args.location = input("Enter your location: ")
        if args.results_wanted is None:
            args.results_wanted = int(input("Enter the number of jobs you want to scrape: "))
        if args.distance is None:
            args.distance = int(input("Enter the distance from your location to search for jobs: "))
        if args.resume is None:
            args.resume = input("Enter the path to your resume file: ")
    
    if args.storage_path is None:
        args.storage_path = STORAGE_PATH
        
    return args 