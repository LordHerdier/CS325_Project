# main.py
# Entrypoint for the application

import click
from src.app import App
from src.config import config

@click.command()
@click.option(
    '--location', 
    type=str, 
    help='User location for job search (overrides config)'
)
@click.option(
    '--max-jobs', 
    type=int, 
    help='Maximum number of jobs to process (overrides config)'
)
@click.option(
    '--job-boards', 
    type=str, 
    help='Comma-separated list of job boards to search (overrides config)'
)
@click.option(
    '--debug', 
    is_flag=True, 
    help='Enable debug mode (overrides config)'
)
@click.option(
    '--storage-path',
    type=click.Path(),
    help='Path for storing data files (overrides config)'
)
def main(location, max_jobs, job_boards, debug, storage_path):
    try:
        args = {
            'user_location': location,
            'max_jobs': max_jobs,
            'job_boards': job_boards.split(',') if job_boards else None,
            'debug': debug if debug else None,  # Only override if flag was used
        }

        # Initialize and run the application
        app = App()
        app.run(**args)
        
    except ValueError as e:
        click.echo(f"Configuration error: {e}", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"Application error: {e}", err=True)
        raise click.Abort()

if __name__ == "__main__":
    main()