#!/usr/bin/env python3
"""
MLB Hits + Runs + RBIs Betting Analysis

This module analyzes MLB player projections to calculate optimal betting recommendations
for the "Hits + Runs + RBIs" prop bet market. It combines individual projections for
hits, runs, and RBIs to determine the best betting opportunities.

Author: MLB Betting Analysis Tool
Created: 2025-01-27
"""

import pandas as pd
import numpy as np
import json
import math
from typing import Dict, List, Tuple, Optional

class HitsRunsRBIsAnalysis:
    """Analyzes MLB player data for Hits + Runs + RBIs betting opportunities."""
    
    def __init__(self):
        """Initialize the analysis class."""
        self.data: Optional[pd.DataFrame] = None
        self.batter_data: Optional[pd.DataFrame] = None
        self.analysis_results: List[Dict] = []
        
    def load_data(self, csv_file: str = 'data/mlb_player_projections.csv') -> bool:
        """Load the scraped MLB data from CSV file.
        
        Args:
            csv_file: Path to the CSV file containing player projections
            
        Returns:
            bool: True if data loaded successfully, False otherwise
        """
        try:
            self.data = pd.read_csv(csv_file)
            print(f"Loaded {len(self.data)} player records")
            return True
        except FileNotFoundError:
            print(f"Error: {csv_file} not found. Please run the scraper first.")
            return False
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def filter_batters(self) -> Optional[pd.DataFrame]:
        """Filter data to only include batters with valid projections.
        
        Returns:
            pd.DataFrame: Filtered batter data or None if no data available
        """
        if self.data is None:
            print("No data loaded")
            return None
        
        # Filter for position players (exclude pitchers: SP, RP, P)
        pitcher_positions = ['SP', 'RP', 'P']
        batters = self.data[~self.data['POS'].isin(pitcher_positions)].copy()
        
        # Convert projection columns to numeric
        numeric_cols = ['H', 'R', 'RBI']
        for col in numeric_cols:
            batters[f'{col}_numeric'] = pd.to_numeric(batters[col], errors='coerce')
        
        # Filter out batters with missing or zero projections in any category
        valid_batters = batters[
            (batters['H_numeric'] > 0) & 
            (batters['R_numeric'] > 0) & 
            (batters['RBI_numeric'] > 0)
        ].copy()
        
        # Calculate combined projection
        valid_batters['HRR_PROJECTION'] = (
            valid_batters['H_numeric'] + 
            valid_batters['R_numeric'] + 
            valid_batters['RBI_numeric']
        )
        
        self.batter_data = valid_batters
        print(f"Found {len(self.batter_data)} batters with valid H+R+RBI projections")
        return self.batter_data
    
    def calculate_poisson_probability(self, projection: float, target: int) -> float:
        """Calculate Poisson probability for a given projection and target.
        
        Args:
            projection: Expected value (lambda parameter)
            target: Target value to calculate probability for
            
        Returns:
            float: Probability of achieving exactly the target value
        """
        if projection <= 0:
            return 0.0
        
        try:
            # P(X = k) = (λ^k * e^(-λ)) / k!
            probability = (projection ** target) * math.exp(-projection) / math.factorial(target)
            return probability
        except (OverflowError, ValueError):
            return 0.0
    
    def calculate_over_probability(self, projection: float, line: float) -> float:
        """Calculate probability of going over a given line.
        
        Args:
            projection: Expected combined H+R+RBI value
            line: Betting line to calculate over probability for
            
        Returns:
            float: Probability of going over the line
        """
        if projection <= 0:
            return 0.0
        
        # Calculate P(X > line) = 1 - P(X <= line)
        cumulative_prob = 0.0
        
        # Sum probabilities from 0 to floor(line)
        for k in range(int(line) + 1):
            cumulative_prob += self.calculate_poisson_probability(projection, k)
        
        return max(0.0, min(1.0, 1 - cumulative_prob))
    
    def find_optimal_line(self, projection: float) -> Tuple[float, float, float]:
        """Calculate betting analysis for fixed line of 2.0.
        
        Args:
            projection: Player's combined H+R+RBI projection
            
        Returns:
            Tuple of (line, edge, over_probability)
        """
        # Use fixed line of 2.0
        line = 2.0
        
        # Calculate over probability for line of 2.0
        over_prob = self.calculate_over_probability(projection, line)
        
        # Calculate edge with typical sportsbook odds around -110 (1.91 decimal)
        if over_prob > 0.01 and over_prob < 0.99:
            typical_payout = 1.91
            edge = (over_prob * typical_payout) - 1
        else:
            edge = 0.0
        
        return line, edge, over_prob
    
    def calculate_confidence_level(self, edge: float, projection: float) -> str:
        """Determine confidence level based on edge and projection strength.
        
        Args:
            edge: Calculated betting edge
            projection: Player's combined projection
            
        Returns:
            str: Confidence level (HIGH, MEDIUM, LOW)
        """
        if edge > 0.15 and projection > 2.5:
            return "HIGH"
        elif edge > 0.08 and projection > 1.8:
            return "MEDIUM"
        elif edge > 0.03:
            return "LOW"
        else:
            return "AVOID"
    
    def get_recommendation(self, edge: float, confidence: str) -> str:
        """Generate betting recommendation based on edge and confidence.
        
        Args:
            edge: Calculated betting edge
            confidence: Confidence level
            
        Returns:
            str: Betting recommendation
        """
        if confidence == "HIGH" and edge > 0.15:
            return "STRONG BET"
        elif confidence == "MEDIUM" and edge > 0.08:
            return "MODERATE BET"
        elif confidence == "LOW" and edge > 0.03:
            return "SMALL BET"
        else:
            return "PASS"
    
    def analyze_all_batters(self) -> List[Dict]:
        """Analyze all batters for H+R+RBI betting opportunities.
        
        Returns:
            List of analysis results for each batter
        """
        if self.batter_data is None or len(self.batter_data) == 0:
            print("No batter data available")
            return []
        
        self.analysis_results = []
        
        for _, batter in self.batter_data.iterrows():
            projection = batter['HRR_PROJECTION']
            
            # Calculate betting analysis for fixed line of 2.0
            line, edge, over_prob = self.find_optimal_line(projection)
            
            # Calculate confidence and recommendation
            confidence = self.calculate_confidence_level(edge, projection)
            recommendation = self.get_recommendation(edge, confidence)
            
            result = {
                'PLAYER': batter['PLAYER'],
                'TEAM': batter['TEAM'],
                'GAME': batter['GAME'],
                'POS': batter['POS'],
                'H_PROJECTION': round(batter['H_numeric'], 2),
                'R_PROJECTION': round(batter['R_numeric'], 2),
                'RBI_PROJECTION': round(batter['RBI_numeric'], 2),
                'HRR_PROJECTION': round(projection, 2),
                'OPTIMAL_LINE': line,
                'OVER_PROBABILITY': round(over_prob, 3),
                'EDGE': round(edge, 4),
                'EDGE_PERCENTAGE': round(edge * 100, 2),
                'CONFIDENCE': confidence,
                'RECOMMENDATION': recommendation
            }
            
            self.analysis_results.append(result)
        
        # Sort by edge (best opportunities first)
        self.analysis_results.sort(key=lambda x: x['EDGE'], reverse=True)
        
        return self.analysis_results
    
    def save_results(self, csv_file: str = 'analysis/hits_runs_rbis_analysis.csv', 
                    json_file: str = 'analysis/hits_runs_rbis_analysis.json') -> None:
        """Save analysis results to CSV and JSON files.
        
        Args:
            csv_file: Path to save CSV results
            json_file: Path to save JSON results
        """
        if not self.analysis_results:
            print("No analysis results to save")
            return
        
        try:
            # Save to CSV
            df = pd.DataFrame(self.analysis_results)
            df.to_csv(csv_file, index=False)
            print(f"Results saved to {csv_file}")
            
            # Save to JSON
            with open(json_file, 'w') as f:
                json.dump(self.analysis_results, f, indent=2)
            print(f"Results saved to {json_file}")
            
        except Exception as e:
            print(f"Error saving results: {e}")
    
    def print_top_opportunities(self, limit: int = 10) -> None:
        """Print the top betting opportunities.
        
        Args:
            limit: Number of top opportunities to display
        """
        if not self.analysis_results:
            print("No analysis results available")
            return
        
        print("\n" + "=" * 80)
        print("TOP HITS + RUNS + RBIs BETTING OPPORTUNITIES")
        print("=" * 80)
        
        print(f"{'Player':<20} {'Team':<6} {'H+R+RBI':<8} {'Line':<6} {'Edge':<8} {'Conf':<6} {'Rec':<12}")
        print("-" * 80)
        
        for i, result in enumerate(self.analysis_results[:limit]):
            print(f"{result['PLAYER']:<20} {result['TEAM']:<6} "
                  f"{result['HRR_PROJECTION']:<8} {result['OPTIMAL_LINE']:<6} "
                  f"{result['EDGE_PERCENTAGE']:<7}% {result['CONFIDENCE']:<6} "
                  f"{result['RECOMMENDATION']:<12}")
        
        print("\n" + "=" * 80)

def main():
    """Main execution function."""
    print("MLB Hits + Runs + RBIs Betting Analysis")
    print("=" * 50)
    
    # Initialize analyzer
    analyzer = HitsRunsRBIsAnalysis()
    
    # Load and process data
    if not analyzer.load_data():
        return
    
    if analyzer.filter_batters() is None:
        return
    
    # Perform analysis
    results = analyzer.analyze_all_batters()
    
    if results:
        # Display top opportunities
        analyzer.print_top_opportunities(15)
        
        # Save results
        analyzer.save_results()
        
        print(f"\nAnalysis complete! Found {len(results)} betting opportunities.")
        print("Results saved to analysis/ directory.")
    else:
        print("No betting opportunities found.")

if __name__ == "__main__":
    main()