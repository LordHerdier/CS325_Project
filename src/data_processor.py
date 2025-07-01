import pandas as pd
import re
from typing import List


def clean_jobs(jobs: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and process job data.
    
    Operations performed:
    1. Drop extraneous columns
    2. Lowercase all strings
    3. Remove special characters (keeping only alphanumeric and spaces)
    
    Args:
        jobs: Raw job data DataFrame
        
    Returns:
        Cleaned job data DataFrame
    """
    df = jobs.copy()
    
    # 1. Drop any of those extraneous columns if they exist
    cols_to_drop = [
        "id", "site",
        "job_url", "job_url_direct",
        "job_type", "salary_source", "interval", "min_amount", "max_amount",
        "currency", "is_remote", "listing_type", "vacancy_count", "work_from_home_type",
        "emails",
        "company_url", "company_logo", "company_url_direct", "company_addresses",
        "company_num_employees", "company_revenue", "company_rating", "company_reviews_count"
    ]
    
    # Only drop columns that actually exist in the DataFrame
    cols_to_drop = [col for col in cols_to_drop if col in df.columns]
    df = df.drop(columns=cols_to_drop)

    # 2. Lowercase all strings
    df = df.map(lambda x: x.lower() if isinstance(x, str) else x)

    # 3. Remove any rows where the row is null
    # df = df.dropna()

    # 4. Remove any escape sequences, or any other special characters
    df = df.map(lambda x: re.sub(r"[^a-zA-Z0-9\s]", "", x) if isinstance(x, str) else x)

    return df 