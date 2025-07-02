# 🚀 Job Scraper Application

An intelligent job scraping and matching application that helps you find the most relevant job opportunities based on your resume. This application leverages AI to analyze job postings and calculate similarity scores between your skills/experience and job requirements.

Read the full report [here](report.md).

## ✨ Features

- **Smart Job Scraping**: Automatically scrape jobs from major job boards (Currently supports Indeed)
- **AI-Powered Analysis**: Use OpenAI's LLM to extract structured information from job postings
- **Resume Matching**: Calculate similarity scores between your resume and job postings using embeddings
- **Interactive CLI**: User-friendly menu-driven interface for easy navigation
- **Persistent Database**: JSON-based storage system that preserves job data and embeddings
- **Export Capabilities**: Export results in multiple formats (JSON, CSV, Excel)
- **Batch Processing**: Efficient handling of large job datasets with rate limiting
- **Duplicate Detection**: Automatic deduplication of job postings

## 🛠 Technology Stack

- **Python 3.11+**: Core programming language
- **JobSpy**: Job scraping from multiple job boards
- **OpenAI API**: LLM processing and embedding generation
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computations for similarity calculations
- **Tenacity**: Retry logic for robust API calls
- **Docker**: Containerization support

## 📋 Prerequisites

Before installing the application, ensure you have:

- Python 3.11 or higher
- pip (Python package installer)
- OpenAI API key (required for AI features)
- At least 2GB of RAM (recommended for processing large job datasets)

## 🔧 Installation

### Option 1: Standard Installation

1. **Clone the repository**:
```bash
git clone https://github.com/LordHerdier/CS325_Project.git
cd CS325_Project
```

2. **Create a virtual environment** (recommended):
```bash
python -m venv job_scraper_env
source job_scraper_env/bin/activate  # On Windows: job_scraper_env\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

### Option 2: Docker Installation

1. **Clone the repository**:
```bash
git clone https://github.com/LordHerdier/CS325_Project.git
cd CS325_Project
```

2. **Build the Docker image**:
```bash
docker build -t job-scraper .
```

3. **Run the Docker container**:
```bash
docker run -it job-scraper
```

## ⚙️ Configuration

### OpenAI API Setup

1. **Get an OpenAI API key**:
   - Visit [OpenAI API](https://platform.openai.com/api-keys)
   - Create an account and generate an API key

2. **Set up environment variables**:

   **Option A: Create a .env file** (recommended):
   ```bash
   # Create .env file in the project root
   echo "OPENAI_API_KEY=your_api_key_here" > .env
   ```

   **Option B: Set environment variable directly**:
   ```bash
   # Linux/Mac
   export OPENAI_API_KEY="your_api_key_here"
   
   # Windows
   set OPENAI_API_KEY=your_api_key_here
   ```

3. **Prepare your resume**:
   - Save your resume as a text file (.txt format works best)
   - Place it in an accessible location (e.g., `./resume.txt`)

## 🚀 Usage

### Interactive Mode (Recommended)

Run the application in interactive mode for the best user experience:

```bash
python main.py
```

This will display a menu with the following options:
1. **Scrape new jobs** - Search and scrape jobs from job boards
2. **Query existing database** - Analyze previously scraped jobs
3. **View top job matches** - See your best job matches
4. **Database statistics** - View database insights
5. **Export results** - Export job data to files
6. **Settings** - Configure application settings
7. **Exit** - Close the application

### Command Line Mode

For automation or scripting, use command line arguments:

#### Scrape Jobs
```bash
python main.py --mode scrape \
    --location "San Francisco, CA" \
    --results-wanted 100 \
    --distance 25 \
    --resume "./resume.txt" \
    --process-jobs-with-llm
```

#### Query Database
```bash
python main.py --mode query \
    --resume "./resume.txt" \
    --show-top 10
```

#### Export Results
```bash
python main.py --mode export
```

### Command Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--mode` | Operation mode: `scrape`, `query`, or `export` | Interactive |
| `--location` | Job search location | Prompted |
| `--results-wanted` | Number of jobs to scrape | 50 |
| `--distance` | Search distance in miles | 25 |
| `--resume` | Path to resume file | Prompted |
| `--show-top` | Number of top matches to display | 10 |
| `--storage-path` | Directory for storing data | `storage` |
| `--process-jobs-with-llm` | Enable advanced LLM processing | False |
| `--debug` | Enable debug mode | False |

## 📁 Project Structure

```
CS-325-project/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── .env                   # Environment variables (create this)
├── src/                   # Source code directory
│   ├── __init__.py        # Package initialization
│   ├── main.py            # Main application logic
│   ├── cli.py             # Command line interface
│   ├── scraper.py         # Job scraping functionality
│   ├── data_processor.py  # Data cleaning and processing
│   ├── storage.py         # Database operations
│   └── llm.py             # OpenAI integration
└── storage/               # Data storage directory (auto-created)
    └── jobs_database.json # Persistent job database
```

## 💡 Usage Examples

### Example 1: First-time Job Search

```bash
# Run interactively
python main.py

# Choose option 1 (Scrape new jobs)
# Enter: location="Seattle, WA", results=50, distance=20
# Provide path to your resume
# Enable LLM processing for better results
```

### Example 2: Analyzing Existing Jobs

```bash
# If you already have jobs in your database
python main.py

# Choose option 2 (Query existing database) 
# Provide your resume path
# View top 10 matches with similarity scores
```

### Example 3: Automated Scraping

```bash
# Scrape 200 jobs from New York area
python main.py --mode scrape \
    --location "New York, NY" \
    --results-wanted 200 \
    --distance 30 \
    --resume "./my_resume.txt" \
    --process-jobs-with-llm \
    --debug
```

## 📊 Understanding Results

The application provides similarity scores between 0.0 and 1.0:
- **0.8-1.0**: Excellent match - highly relevant jobs
- **0.6-0.8**: Good match - worth investigating
- **0.4-0.6**: Moderate match - may require skill development
- **0.0-0.4**: Poor match - likely not suitable

## 🔍 Troubleshooting

### Common Issues

1. **OpenAI API Error**:
   ```
   RuntimeError: OPENAI_API_KEY not set in environment
   ```
   **Solution**: Set up your OpenAI API key as described in the Configuration section.

2. **No jobs scraped**:
   ```
   No jobs were successfully scraped
   ```
   **Solution**: Try a different location, increase distance, or check your internet connection.

3. **Rate limiting errors**:
   **Solution**: The application includes automatic retry logic. If issues persist, reduce `results_wanted`.

4. **Memory issues with large datasets**:
   **Solution**: Process jobs in smaller batches or increase available RAM.

### Debug Mode

Enable debug mode for detailed logging:
```bash
python main.py --debug
```

## 🔒 Privacy and Security

- Your resume data is processed locally and only sent to OpenAI for analysis
- Job data is stored locally in JSON format
- No personal data is shared with job boards beyond what's required for scraping
- OpenAI's data usage policy applies to resume and job description processing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Commit your changes: `git commit -m "Add feature"`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Enable debug mode for more detailed error information
3. Review the OpenAI API documentation for API-related issues
4. Create an issue in the repository with:
   - Error message
   - Steps to reproduce
   - Your environment details (OS, Python version)

## 🔮 Future Enhancements

- Support for additional job boards (LinkedIn, Glassdoor, etc.)
- Web interface for easier interaction
- Advanced filtering options (salary, company size, etc.)
- Job application tracking
- Machine learning model improvements