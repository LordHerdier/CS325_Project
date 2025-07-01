import pandas as pd
import json
import os
from datetime import datetime
from typing import Optional


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