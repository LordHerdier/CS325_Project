from openai import OpenAI
from dotenv import load_dotenv
import os
import json
from typing import List, Dict

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
        Extract key information from job postings using the LLM.

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
        extracted_info: List[Dict] = []

        system_prompt = (
            "You are a data-extraction agent. Your job is to take a job-posting object and "
            "pull out exactly four pieces of information, then return them as pure JSON—no apologies, no commentary.\n"
            "Requirements:\n"
            "- \"title\": copy it from the posting’s title field\n"
            "- \"company\": copy it from the posting’s company field\n"
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
            # Construct the full prompt by appending the job posting JSON
            user_prompt = system_prompt + "Here’s the job posting to analyze as JSON:\n```json\n" + json.dumps(job, indent=2) + "\n```"

            # print(f"Processing job")
            # Call the OpenAI Chat Completion endpoint
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0,
            )

            content = response.choices[0].message.content.strip()
            content = json.loads(content) if content.startswith('{') else content

            extracted_info.append(content)

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

        user_prompt = system_prompt + "Here’s the resume to analyze:\n" + resume

        # print("Processing resume")
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0,
        )

        content = response.choices[0].message.content.strip()
        return json.loads(content) if content.startswith('{') else content

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