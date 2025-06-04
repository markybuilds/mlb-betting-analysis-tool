import pandas as pd
import json
import math

class PitcherStrikeoutAnalysis:
    def __init__(self):
        self.data = None
        self.pitcher_data = None
        
    def load_data(self, csv_file='data/mlb_player_projections.csv'):
        """Load the scraped MLB data"""
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
    
    def filter_pitchers(self):
        """Filter data to only include pitchers with K projections"""
        if self.data is None:
            print("No data loaded")
            return
        
        # Filter for pitchers (SP, RP, P positions) with valid K projections
        pitcher_positions = ['SP', 'RP', 'P']
        pitchers = self.data[self.data['POS'].isin(pitcher_positions)].copy()
        
        # Convert K column to numeric, filtering out non-numeric values
        pitchers['K_numeric'] = pd.to_numeric(pitchers['K'], errors='coerce')
        
        # Filter out pitchers with no K projection or K projection of 0
        self.pitcher_data = pitchers[pitchers['K_numeric'] > 0].copy()
        
        print(f"Found {len(self.pitcher_data)} pitchers with valid strikeout projections")
        return self.pitcher_data
    
    def calculate_optimal_alt_lines(self):
        """Calculate optimal FanDuel alternative lines for strikeout props"""
        if self.pitcher_data is None or len(self.pitcher_data) == 0:
            print("No pitcher data available")
            return None
        
        analysis_results = []
        
        for _, pitcher in self.pitcher_data.iterrows():
            k_projection = pitcher['K_numeric']
            
            # Calculate optimal alt line based on projection
            # Strategy: Take alt line that's 0.5-1.5 strikeouts below projection
            # but not more than 25% below the projection to avoid being too conservative
            
            min_reduction = 0.5
            max_reduction = min(1.5, k_projection * 0.25)  # Max 25% reduction
            
            # Calculate the optimal alt line (round down to nearest 0.5)
            optimal_reduction = min(max_reduction, max(min_reduction, k_projection * 0.15))
            optimal_alt_line = k_projection - optimal_reduction
            
            # Round to nearest 0.5 (common FanDuel increment)
            optimal_alt_line = math.floor(optimal_alt_line * 2) / 2
            
            # Ensure we don't go below 1.5 strikeouts (minimum reasonable prop)
            optimal_alt_line = max(1.5, optimal_alt_line)
            
            # Calculate edge (how much above the alt line the projection is)
            edge = k_projection - optimal_alt_line
            edge_percentage = (edge / optimal_alt_line) * 100
            
            # Determine confidence level based on edge
            if edge >= 2.0:
                confidence = "High"
            elif edge >= 1.0:
                confidence = "Medium"
            elif edge >= 0.5:
                confidence = "Low"
            else:
                confidence = "Avoid"
            
            analysis_results.append({
                'PLAYER': pitcher['PLAYER'],
                'TEAM': pitcher['TEAM'],
                'GAME': pitcher['GAME'],
                'K_PROJECTION': k_projection,
                'OPTIMAL_ALT_LINE': optimal_alt_line,
                'EDGE': round(edge, 2),
                'EDGE_PERCENTAGE': round(edge_percentage, 1),
                'CONFIDENCE': confidence,
                'RECOMMENDATION': f"Take Over {optimal_alt_line} K's" if confidence != "Avoid" else "Skip"
            })
        
        # Convert to DataFrame and sort by edge (highest first)
        results_df = pd.DataFrame(analysis_results)
        results_df = results_df.sort_values('EDGE', ascending=False)
        
        return results_df
    
    def generate_betting_report(self):
        """Generate a comprehensive betting analysis report"""
        results = self.calculate_optimal_alt_lines()
        
        if results is None or len(results) == 0:
            print("No analysis results available")
            return
        
        print("\n" + "="*80)
        print("MLB PITCHER STRIKEOUT PROP BETTING ANALYSIS")
        print("="*80)
        
        # Summary statistics
        total_pitchers = len(results)
        high_confidence = len(results[results['CONFIDENCE'] == 'High'])
        medium_confidence = len(results[results['CONFIDENCE'] == 'Medium'])
        low_confidence = len(results[results['CONFIDENCE'] == 'Low'])
        avoid = len(results[results['CONFIDENCE'] == 'Avoid'])
        
        print(f"\nSUMMARY:")
        print(f"Total Pitchers Analyzed: {total_pitchers}")
        print(f"High Confidence Bets: {high_confidence}")
        print(f"Medium Confidence Bets: {medium_confidence}")
        print(f"Low Confidence Bets: {low_confidence}")
        print(f"Avoid: {avoid}")
        
        # Top recommendations
        print(f"\nTOP 10 STRIKEOUT PROP RECOMMENDATIONS:")
        print("-" * 80)
        top_10 = results.head(10)
        
        for _, row in top_10.iterrows():
            print(f"{row['PLAYER']} ({row['TEAM']}) - {row['GAME']}")
            print(f"  Projection: {row['K_PROJECTION']:.1f} K's | Recommended: Over {row['OPTIMAL_ALT_LINE']} K's")
            print(f"  Edge: +{row['EDGE']:.1f} K's ({row['EDGE_PERCENTAGE']:.1f}%) | Confidence: {row['CONFIDENCE']}")
            print()
        
        # High confidence bets
        high_conf_bets = results[results['CONFIDENCE'] == 'High']
        if len(high_conf_bets) > 0:
            print(f"\nHIGH CONFIDENCE BETS (Edge ≥ 2.0 K's):")
            print("-" * 50)
            for _, row in high_conf_bets.iterrows():
                print(f"{row['PLAYER']} ({row['TEAM']}): Over {row['OPTIMAL_ALT_LINE']} K's (Edge: +{row['EDGE']:.1f})")
        
        # Medium confidence bets
        medium_conf_bets = results[results['CONFIDENCE'] == 'Medium']
        if len(medium_conf_bets) > 0:
            print(f"\nMEDIUM CONFIDENCE BETS (Edge 1.0-1.9 K's):")
            print("-" * 50)
            for _, row in medium_conf_bets.iterrows():
                print(f"{row['PLAYER']} ({row['TEAM']}): Over {row['OPTIMAL_ALT_LINE']} K's (Edge: +{row['EDGE']:.1f})")
        
        return results
    
    def save_analysis(self, results, filename='analysis/pitcher_strikeout_analysis.csv'):
        """Save analysis results to CSV"""
        if results is not None:
            # Ensure analysis directory exists
            import os
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            results.to_csv(filename, index=False)
            print(f"\nAnalysis saved to {filename}")
            print(f"Columns: {list(results.columns)}")
    
    def run_full_analysis(self):
        """Run the complete analysis pipeline"""
        print("Starting Pitcher Strikeout Prop Analysis...")
        
        # Load data
        if not self.load_data():
            return None
        
        # Filter pitchers
        self.filter_pitchers()
        
        # Generate report
        results = self.generate_betting_report()
        
        # Save results
        if results is not None:
            self.save_analysis(results)
            
            # Also save as JSON for programmatic use
            import os
            json_filename = 'analysis/pitcher_strikeout_analysis.json'
            os.makedirs(os.path.dirname(json_filename), exist_ok=True)
            results.to_json(json_filename, orient='records', indent=2)
            print(f"Analysis also saved to {json_filename}")
        
        return results

def main():
    """Main function to run the pitcher strikeout analysis"""
    analyzer = PitcherStrikeoutAnalysis()
    results = analyzer.run_full_analysis()
    
    if results is not None:
        print("\n" + "="*80)
        print("ANALYSIS COMPLETE!")
        print("="*80)
        print("\nFiles created:")
        print("- analysis/pitcher_strikeout_analysis.csv (Excel-friendly format)")
        print("- analysis/pitcher_strikeout_analysis.json (Programmatic format)")
        print("\nUse these files to make informed FanDuel strikeout prop bets!")
        print("\nStrategy Notes:")
        print("- Focus on High and Medium confidence bets")
        print("- High confidence = 2+ strikeout edge over alt line")
        print("- Medium confidence = 1-1.9 strikeout edge")
        print("- Alt lines are set conservatively to maximize win probability")
    else:
        print("Analysis failed. Please check that mlb_player_projections.csv exists.")

if __name__ == "__main__":
    main()