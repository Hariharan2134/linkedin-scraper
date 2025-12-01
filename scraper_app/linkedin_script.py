import subprocess
import sys

def run_scraper(query, pages, max_profiles):
    cmd = [
        sys.executable,
        "scraper_app/real_scraper.py",  # your main scraper
        query,
        str(pages),
        str(max_profiles)
    ]

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    return result.stdout + "\n" + result.stderr
