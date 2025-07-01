from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import time
import tempfile
from typing import List, Dict, Optional

# Load environment variables
dotenv_path = os.getenv("DOTENV_PATH")
if dotenv_path:
    load_dotenv(dotenv_path)
else:
    load_dotenv()

class LLM:
    def __init__(self, model: str = "gpt-3.5-turbo"):
        """
        Initialize the LLM wrapper.

        Args:
            model: The name of the chat/completion model to use.
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set in environment")
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.embedding_model = "text-embedding-3-small"

    def extract_job_information(self, jobs: List[Dict]) -> List[Dict]:
        """
        Extract key information from job postings using the LLM with Batch API.

        Args:
            jobs: List of job posting dicts. Each dict should contain at least
                  'title', 'company', and 'description' keys.

        Returns:
            A list of dicts containing exactly the fields:
            - title (str)
            - company (str)
            - skills (List[str])
            - experience (int)
        """
        if not jobs:
            return []

        # For small batches, use sequential processing to avoid batch API overhead
        if len(jobs) <= 5:
            return self._extract_job_information_sequential(jobs)

        return self._extract_job_information_batch(jobs)

    def _extract_job_information_sequential(self, jobs: List[Dict]) -> List[Dict]:
        """
        Extract job information using sequential API calls (for small batches).
        """
        extracted_info: List[Dict] = []

        system_prompt = (
            "You are a data-extraction agent. Your job is to take a job-posting object and "
            "pull out exactly four pieces of information, then return them as pure JSON—no apologies, no commentary.\n"
            "Requirements:\n"
            "- \"title\": copy it from the posting's title field\n"
            "- \"company\": copy it from the posting's company field\n"
            "- \"skills\": an array of all relevant skills mentioned or implied by the job description\n"
            "- \"experience\": the minimum years of experience required, as a number (e.g. 4)\n"
            "Output format:\n"
            "{\n"
            "  \"title\": \"...\",\n"
            "  \"company\": \"...\",\n"
            "  \"skills\": [\"skill1\", \"skill2\", …],\n"
            "  \"experience\": 4\n"
            "}\n"
        )

        for job in jobs:
            # Construct the user prompt with the job posting JSON
            user_prompt = "Here's the job posting to analyze as JSON:\n```json\n" + json.dumps(job, indent=2) + "\n```"

            # Call the OpenAI Chat Completion endpoint
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0,
            )

            content = response.choices[0].message.content
            if content is None:
                continue
            
            content = content.strip()
            try:
                parsed_content = json.loads(content) if content.startswith('{') else {}
                extracted_info.append(parsed_content)
            except json.JSONDecodeError:
                # Skip invalid JSON responses
                continue

        return extracted_info

    def _extract_job_information_batch(self, jobs: List[Dict]) -> List[Dict]:
        """
        Extract job information using OpenAI's Batch API for efficient processing.
        """
        system_prompt = (
            "You are a data-extraction agent. Your job is to take a job-posting object and "
            "pull out exactly four pieces of information, then return them as pure JSON—no apologies, no commentary.\n"
            "Requirements:\n"
            "- \"title\": copy it from the posting's title field\n"
            "- \"company\": copy it from the posting's company field\n"
            "- \"skills\": an array of all relevant skills mentioned or implied by the job description\n"
            "- \"experience\": the minimum years of experience required, as a number (e.g. 4)\n"
            "Output format:\n"
            "{\n"
            "  \"title\": \"...\",\n"
            "  \"company\": \"...\",\n"
            "  \"skills\": [\"skill1\", \"skill2\", …],\n"
            "  \"experience\": 4\n"
            "}\n"
        )

        # Create batch requests
        batch_requests = []
        for i, job in enumerate(jobs):
            user_prompt = "Here's the job posting to analyze as JSON:\n```json\n" + json.dumps(job, indent=2) + "\n```"
            
            batch_request = {
                "custom_id": f"job-{i}",
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": 0,
                }
            }
            batch_requests.append(batch_request)

        # Create temporary file for batch input
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as temp_file:
            for request in batch_requests:
                temp_file.write(json.dumps(request) + '\n')
            temp_file_path = temp_file.name

        try:
            # Upload the batch file
            with open(temp_file_path, 'rb') as file:
                batch_file = self.client.files.create(
                    file=file,
                    purpose="batch"
                )

            # Create the batch
            batch = self.client.batches.create(
                input_file_id=batch_file.id,
                endpoint="/v1/chat/completions",
                completion_window="24h"
            )

            # Wait for batch completion
            print(f"Batch {batch.id} created, waiting for completion...")
            batch = self._wait_for_batch_completion(batch.id)

            if batch.status == "completed" and batch.output_file_id:
                # Retrieve results
                results = self._retrieve_batch_results(batch.output_file_id)
                return self._process_batch_results(results, len(jobs))
            else:
                print(f"Batch failed with status: {batch.status}")
                # Fallback to sequential processing
                return self._extract_job_information_sequential(jobs)

        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    def _wait_for_batch_completion(self, batch_id: str, max_wait_time: int = 3600):
        """
        Wait for batch completion with polling.
        
        Args:
            batch_id: The ID of the batch to wait for
            max_wait_time: Maximum time to wait in seconds (default: 1 hour)
        """
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            batch = self.client.batches.retrieve(batch_id)
            
            if batch.status in ["completed", "failed", "expired", "cancelled"]:
                return batch
            
            print(f"Batch status: {batch.status}, waiting...")
            time.sleep(10)  # Wait 10 seconds between checks
        
        raise TimeoutError(f"Batch {batch_id} did not complete within {max_wait_time} seconds")

    def _retrieve_batch_results(self, output_file_id: str) -> List[Dict]:
        """
        Retrieve and parse batch results from the output file.
        """
        file_response = self.client.files.content(output_file_id)
        file_contents = file_response.read().decode('utf-8')
        
        results = []
        for line in file_contents.strip().split('\n'):
            if line:
                results.append(json.loads(line))
        
        return results

    def _process_batch_results(self, results: List[Dict], expected_count: int) -> List[Dict]:
        """
        Process batch results and return extracted job information.
        """
        # Sort results by custom_id to maintain order
        results.sort(key=lambda x: int(x['custom_id'].split('-')[1]))
        
        extracted_info = []
        for result in results:
            if result.get('error'):
                print(f"Error in batch result {result['custom_id']}: {result['error']}")
                continue
            
            response_body = result.get('response', {}).get('body', {})
            choices = response_body.get('choices', [])
            
            if choices:
                content = choices[0].get('message', {}).get('content')
                if content:
                    content = content.strip()
                    try:
                        parsed_content = json.loads(content) if content.startswith('{') else {}
                        extracted_info.append(parsed_content)
                    except json.JSONDecodeError:
                        continue
        
        return extracted_info
    
    def extract_resume_information(self, resume: str) -> Dict:
        """
        Extract key information from a resume using the LLM.

        Args:
            resume: The resume text to analyze.

        Returns:
            A dict containing extracted information such as name, skills, and experience.
        """
        system_prompt = (
            "You are a data-extraction agent. Your job is to take a resume and "
            "pull out key information, then return it as pure JSON—no apologies, no commentary.\n"
            "Requirements:\n"
            "- \"name\": the full name of the person\n"
            "- \"skills\": an array of all relevant skills mentioned in the resume\n"
            "- \"experience\": the total years of experience, as a number (e.g. 5)\n"
            "Output format:\n"
            "{\n"
            "  \"name\": \"...\",\n"
            "  \"skills\": [\"skill1\", \"skill2\", …],\n"
            "  \"experience\": 5\n"
            "}\n"
        )

        user_prompt = "Here's the resume to analyze:\n" + resume

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0,
        )

        content = response.choices[0].message.content
        if content is None:
            return {}
        
        content = content.strip()
        try:
            return json.loads(content) if content.startswith('{') else {}
        except json.JSONDecodeError:
            return {}

    def embed_text(self, text) -> List[float]:
        """
        Generate embeddings for a given text using the LLM.

        Args:
            text: The text to embed.

        Returns:
            A list of floats representing the embedding vector.
        """
        response = self.client.embeddings.create(
            model=self.embedding_model,
            input=text
        )
        return response.data[0].embedding if response.data else []