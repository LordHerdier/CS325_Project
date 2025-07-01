import pandas as pd
import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any


def get_jobs_from_json(storage_path: str) -> pd.DataFrame:
    """
    Load jobs from a JSON file.
    
    Args:
        storage_path: Path to the JSON file
        
    Returns:
        DataFrame containing job data
    """
    with open(storage_path, "r") as f:
        jobs = json.load(f)
    return pd.DataFrame(jobs)


def save_to_json(jobs: pd.DataFrame, storage_path: str) -> None:
    """
    Save jobs DataFrame to JSON file.
    
    Args:
        jobs: DataFrame containing job data
        storage_path: Path where to save the JSON file
    """
    # Ensure the directory exists
    os.makedirs(os.path.dirname(storage_path), exist_ok=True)
    
    jobs.to_json(storage_path, orient="records", indent=4)

def dump_list_of_dicts_to_json(data: list[dict], storage_path: str) -> None:
    """
    Save a list of dictionaries to a JSON file.
    
    Args:
        data: List of dictionaries to save
        storage_path: Path where to save the JSON file
    """
    # Ensure the directory exists
    os.makedirs(os.path.dirname(storage_path), exist_ok=True)
    
    with open(storage_path, "w") as f:
        json.dump(data, f, indent=4)


def generate_filename(storage_path: str) -> str:
    """
    Generate a timestamped filename for storing jobs.
    
    Args:
        storage_path: Base storage directory path
        
    Returns:
        Full path with timestamped filename
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{storage_path}/jobs_{timestamp}.json"


def load_job_database(database_path: str) -> List[Dict[str, Any]]:
    """
    Load the persistent job database from JSON file.
    
    Args:
        database_path: Path to the database JSON file
        
    Returns:
        List of job dictionaries, empty list if file doesn't exist
    """
    if os.path.exists(database_path):
        try:
            with open(database_path, "r") as f:
                jobs = json.load(f)
            print(f"Loaded {len(jobs)} existing jobs from database")
            return jobs
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading job database: {e}")
            print("Starting with empty database")
            return []
    else:
        print("No existing job database found, starting with empty database")
        return []


def merge_jobs_into_database(existing_jobs: List[Dict[str, Any]], new_jobs: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], int]:
    """
    Merge new jobs into existing jobs database, avoiding duplicates by job ID.
    Preserves embeddings from existing jobs.
    
    Args:
        existing_jobs: List of existing job dictionaries
        new_jobs: List of new job dictionaries to merge
        
    Returns:
        Tuple of (merged_jobs_list, number_of_new_jobs_added)
    """
    # Create a dictionary of existing jobs by ID for fast lookup and embedding preservation
    existing_jobs_dict = {job.get('id'): job for job in existing_jobs if job.get('id')}
    
    # Filter out jobs that already exist
    unique_new_jobs = []
    for job in new_jobs:
        job_id = job.get('id')
        if job_id and job_id not in existing_jobs_dict:
            unique_new_jobs.append(job)
    
    # Merge the lists (existing jobs already have their embeddings preserved)
    merged_jobs = existing_jobs + unique_new_jobs
    
    print(f"Added {len(unique_new_jobs)} new unique jobs to database")
    print(f"Skipped {len(new_jobs) - len(unique_new_jobs)} duplicate jobs")
    
    return merged_jobs, len(unique_new_jobs)


def separate_jobs_by_embeddings(jobs: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Separate jobs into those with embeddings and those without.
    
    Args:
        jobs: List of job dictionaries
        
    Returns:
        Tuple of (jobs_with_embeddings, jobs_without_embeddings)
    """
    jobs_with_embeddings = []
    jobs_without_embeddings = []
    
    for job in jobs:
        if 'embedding' in job and job['embedding'] is not None:
            jobs_with_embeddings.append(job)
        else:
            jobs_without_embeddings.append(job)
    
    return jobs_with_embeddings, jobs_without_embeddings


def add_embeddings_to_jobs(jobs: List[Dict[str, Any]], embeddings: List[List[float]]) -> List[Dict[str, Any]]:
    """
    Add embeddings to job dictionaries.
    
    Args:
        jobs: List of job dictionaries
        embeddings: List of embedding vectors (same order as jobs)
        
    Returns:
        List of job dictionaries with embeddings added
    """
    if len(jobs) != len(embeddings):
        raise ValueError(f"Number of jobs ({len(jobs)}) must match number of embeddings ({len(embeddings)})")
    
    jobs_with_embeddings = []
    for job, embedding in zip(jobs, embeddings):
        job_copy = job.copy()
        job_copy['embedding'] = embedding
        jobs_with_embeddings.append(job_copy)
    
    return jobs_with_embeddings


def save_job_database(jobs: List[Dict[str, Any]], database_path: str) -> None:
    """
    Save the job database to a JSON file.
    
    Args:
        jobs: List of job dictionaries to save
        database_path: Path where to save the database JSON file
    """
    # Ensure the directory exists
    os.makedirs(os.path.dirname(database_path), exist_ok=True)
    
    try:
        with open(database_path, "w") as f:
            json.dump(jobs, f, indent=4)
        print(f"Saved {len(jobs)} jobs to database: {database_path}")
    except IOError as e:
        print(f"Error saving job database: {e}")


def get_database_path(storage_path: str) -> str:
    """
    Generate the path for the persistent job database.
    
    Args:
        storage_path: Base storage directory path
        
    Returns:
        Full path to the database file
    """
    return f"{storage_path}/jobs_database.json" 