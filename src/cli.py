import argparse
from typing import Optional

STORAGE_PATH = "storage"


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Job Scraper")
    parser.add_argument("--location", type=str, help="User location for job search")
    parser.add_argument("--results-wanted", type=int, help="Maximum number of jobs to process")
    parser.add_argument("--distance", type=int, help="Distance from user location to search for jobs")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--storage-path", type=str, default=STORAGE_PATH, help="Path to store the jobs")
    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> argparse.Namespace:
    """Validate and prompt for missing arguments."""
    if args.location is None:
        args.location = input("Enter your location: ")
    if args.results_wanted is None:
        args.results_wanted = int(input("Enter the number of jobs you want to scrape: "))
    if args.distance is None:
        args.distance = int(input("Enter the distance from your location to search for jobs: "))
    if args.debug is None:
        args.debug = False
    if args.storage_path is None:
        args.storage_path = STORAGE_PATH
    return args 