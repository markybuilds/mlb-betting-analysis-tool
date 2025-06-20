#!/usr/bin/env python3
"""
Daily MLB Pitcher Strikeout Prop Analysis Update

This script automates the daily workflow:
1. Scrape fresh MLB projection data
2. Analyze pitcher strikeout props
3. Generate betting recommendations

Usage: python daily_update.py
"""

import subprocess
import sys
import os
from datetime import datetime

def run_script(script_name, description):
    """Run a Python script and handle errors"""
    print(f"\n{'='*60}")
    print(f"RUNNING: {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, check=True)
        print(result.stdout)
        if result.stderr:
            print(f"Warnings: {result.stderr}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name}:")
        print(f"Exit code: {e.returncode}")
        print(f"Error output: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"Error: {script_name} not found in current directory")
        return False

def main():
    """Main function to run daily update"""
    print(f"MLB Daily Betting Analysis Update - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nThis will update your MLB prop betting analysis with fresh data.")
    print("Includes: Pitcher Strikeouts, Batter Hits & 2+ HHR Analysis")
    
    # Check if we're in the right directory
    required_files = ['mlb_scraper.py', 'pitcher_strikeout_analysis.py', 'batter_hits_analysis.py', 'hits_runs_rbis_analysis.py']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"\nError: Missing required files: {missing_files}")
        print("Please run this script from the mlb-tool directory.")
        return False
    
    success_count = 0
    total_steps = 4
    
    # Step 1: Scrape fresh data
    if run_script('mlb_scraper.py', 'Scraping Fresh MLB Projection Data'):
        success_count += 1
        print("[SUCCESS] Data scraping completed successfully")
    else:
        print("[ERROR] Data scraping failed")
        print("\nTrying to continue with existing data...")
    
    # Step 2: Generate pitcher analysis
    if run_script('pitcher_strikeout_analysis.py', 'Analyzing Pitcher Strikeout Props'):
        success_count += 1
        print("[SUCCESS] Pitcher analysis completed successfully")
    else:
        print("[ERROR] Pitcher analysis failed")
        print("\nContinuing with batter analysis...")
    
    # Step 3: Generate batter analysis
    if run_script('batter_hits_analysis.py', 'Analyzing Batter Hits Props'):
        success_count += 1
        print("[SUCCESS] Batter analysis completed successfully")
    else:
        print("[ERROR] Batter analysis failed")
        print("\nContinuing with 2+ HHR analysis...")
    
    # Step 4: Generate 2+ HHR analysis
    if run_script('hits_runs_rbis_analysis.py', 'Analyzing 2+ Hits+Runs+RBIs Props'):
        success_count += 1
        print("[SUCCESS] 2+ HHR analysis completed successfully")
    else:
        print("[ERROR] 2+ HHR analysis failed")
        return False
    
    # Summary
    print(f"\n{'='*60}")
    print("DAILY UPDATE SUMMARY")
    print(f"{'='*60}")
    print(f"Completed: {success_count}/{total_steps} steps")
    
    if success_count >= 2:  # At least scraping + one analysis
        print("\n[SUCCESS] Your betting analysis is up to date.")
        print("\nGenerated files:")
        print("- data/mlb_player_projections.csv (Raw projection data)")
        print("- data/mlb_player_projections.json (Raw projection data - JSON)")
        
        if success_count >= 2:
            print("\nPITCHER STRIKEOUT ANALYSIS:")
            print("- analysis/pitcher_strikeout_analysis.csv (Detailed analysis)")
            print("- analysis/pitcher_strikeout_analysis.json (JSON format)")
        
        if success_count >= 3:
            print("\nBATTER HITS ANALYSIS:")
            print("- analysis/batter_hits_analysis.csv (Detailed analysis)")
            print("- analysis/batter_hits_analysis.json (JSON format)")
        
        if success_count == 4:
            print("\n2+ HHR ANALYSIS:")
            print("- analysis/hits_runs_rbis_analysis.csv (Detailed analysis)")
            print("- analysis/hits_runs_rbis_analysis.json (JSON format)")
        
        print("\nNext steps:")
        print("1. Review betting recommendations in the summary files")
        print("2. Check FanDuel for current lines and odds")
        print("3. Focus on Medium/High Confidence strikeout props")
        print("4. Consider top edge percentage hits props with smaller units")
        print("5. Review 2+ HHR analysis for combination prop opportunities")
        
        print("\nRemember:")
        print("- Always verify lines are still available on FanDuel")
        print("- Consider additional factors (weather, lineups, matchups)")
        print("- Hits props are more volatile - use smaller unit sizes")
        print("- 2+ HHR props offer higher payouts but require more precision")
        print("- Bet responsibly and within your limits")
        
        return True
    else:
        print("\n[ERROR] Some steps failed. Check the error messages above.")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)