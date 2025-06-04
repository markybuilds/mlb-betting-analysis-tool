#!/usr/bin/env python3
"""
MLB Betting Scraper Runner

This script runs the enhanced MLB scraper to collect player projections
and generate betting analysis.
"""

import sys
import os
from datetime import datetime

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mlb_scraper_enhanced import MLBScraperEnhanced

def main():
    """Main function to run the MLB scraper."""
    print(f"Starting MLB scraper at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Initialize the scraper
        scraper = MLBScraperEnhanced()
        
        # Run the scraper
        scraper.run_full_scrape()
        
        print("\nScraper completed successfully!")
        print(f"Data saved to: {scraper.data_dir}")
        
    except Exception as e:
        print(f"Error running scraper: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()