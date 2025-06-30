# src/storage/__init__.py
# Data storage services

# TODO: Implement data storage services

import json
import os
from src.config import Config
from datetime import datetime

class DataStorage:
    def __init__(self, storage_path=None):
        """Initialize data storage"""
        self.storage_path = storage_path or Config().get("STORAGE_PATH")
        self.ensure_storage_directory()
    
    def ensure_storage_directory(self):
        """Ensure storage directory exists"""
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)
    
    def save_job_data(self, job_data, filename=None):
        """Save job data to JSON file"""
        if not filename:
            filename = f"{self.storage_path}/jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(job_data, f)
    
    def load_job_data(self, filename):
        """Load job data from JSON file"""
        with open(filename, 'r') as f:
            return json.load(f)
    
    def save_embeddings(self, embeddings, metadata, filename=None):
        """Save embeddings with metadata to JSON file"""
        if not filename:
            filename = f"{self.storage_path}/embeddings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(embeddings, f)
    
    def load_embeddings(self, filename):
        """Load embeddings from JSON file"""
        with open(filename, 'r') as f:
            return json.load(f)
    
    def list_stored_files(self):
        """List all stored data files"""
        return [f for f in os.listdir(self.storage_path) if f.endswith('.json')]