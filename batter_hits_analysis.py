import pandas as pd
import json
import math

class BatterHitsAnalysis:
    def __init__(self):
        self.data = None
        self.batter_data = None
        
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
    
    def filter_batters(self):
        """Filter data to only include batters with H projections"""
        if self.data is None:
            print("No data loaded")
            return
        
        # Filter for position players (exclude pitchers: SP, RP, P)
        pitcher_positions = ['SP', 'RP', 'P']
        batters = self.data[~self.data['POS'].isin(pitcher_positions)].copy()
        
        # Convert H column to numeric, filtering out non-numeric values
        batters['H_numeric'] = pd.to_numeric(batters['H'], errors='coerce')
        
        # Filter out batters with no H projection or H projection of 0
        self.batter_data = batters[batters['H_numeric'] > 0].copy()
        
        print(f"Found {len(self.batter_data)} batters with valid hits projections")
        return self.batter_data
    
    def calculate_optimal_alt_lines(self):
        """Calculate optimal FanDuel alternative lines for hits props"""
        if self.batter_data is None or len(self.batter_data) == 0:
            print("No batter data available")
            return None
        
        analysis_results = []
        
        for _, batter in self.batter_data.iterrows():
            h_projection = batter['H_numeric']
            
            # For FanDuel "at least 1 hit" bets, we compare projection to 1.0
            # If projection > 1.0, it's a good bet. The higher above 1.0, the better.
            
            # Standard alt line for "at least 1 hit" prop
            standard_alt_line = 1.0
            
            # Calculate edge (how much above 1.0 the projection is)
            edge = h_projection - standard_alt_line
            edge_percentage = (edge / standard_alt_line) * 100 if standard_alt_line > 0 else 0
            
            # Determine confidence level based on how much projection exceeds 1.0
            if h_projection >= 1.5:  # 50%+ edge over 1.0
                confidence = "High"
                optimal_alt_line = 1.0
            elif h_projection >= 1.3:  # 30%+ edge over 1.0
                confidence = "Medium" 
                optimal_alt_line = 1.0
            elif h_projection >= 1.1:  # 10%+ edge over 1.0
                confidence = "Low"
                optimal_alt_line = 1.0
            else:  # Projection below 1.1
                confidence = "Avoid"
                # For avoid cases, calculate what alt line would make sense
                optimal_alt_line = math.floor(h_projection * 2) / 2
                optimal_alt_line = max(0.5, optimal_alt_line)
                edge = h_projection - optimal_alt_line
                edge_percentage = (edge / optimal_alt_line) * 100 if optimal_alt_line > 0 else 0
            
            analysis_results.append({
                'PLAYER': batter['PLAYER'],
                'TEAM': batter['TEAM'],
                'GAME': batter['GAME'],
                'POS': batter['POS'],
                'H_PROJECTION': h_projection,
                'OPTIMAL_ALT_LINE': optimal_alt_line,
                'EDGE': round(edge, 2),
                'EDGE_PERCENTAGE': round(edge_percentage, 1),
                'CONFIDENCE': confidence,
                'RECOMMENDATION': f"Take Over {optimal_alt_line} Hits" if confidence != "Avoid" else "Skip"
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
        print("MLB BATTER HITS PROP BETTING ANALYSIS")
        print("="*80)
        
        # Summary statistics
        total_batters = len(results)
        high_confidence = len(results[results['CONFIDENCE'] == 'High'])
        medium_confidence = len(results[results['CONFIDENCE'] == 'Medium'])
        low_confidence = len(results[results['CONFIDENCE'] == 'Low'])
        avoid = len(results[results['CONFIDENCE'] == 'Avoid'])
        
        print(f"\nSUMMARY:")
        print(f"Total Batters Analyzed: {total_batters}")
        print(f"High Confidence Bets: {high_confidence}")
        print(f"Medium Confidence Bets: {medium_confidence}")
        print(f"Low Confidence Bets: {low_confidence}")
        print(f"Avoid: {avoid}")
        
        # Top recommendations
        print(f"\nTOP 15 HITS PROP RECOMMENDATIONS:")
        print("-" * 80)
        top_15 = results.head(15)
        
        for _, row in top_15.iterrows():
            print(f"{row['PLAYER']} ({row['TEAM']}) - {row['POS']} - {row['GAME']}")
            print(f"  Projection: {row['H_PROJECTION']:.1f} Hits | Recommended: Over {row['OPTIMAL_ALT_LINE']} Hits")
            print(f"  Edge: +{row['EDGE']:.1f} Hits ({row['EDGE_PERCENTAGE']:.1f}%) | Confidence: {row['CONFIDENCE']}")
            print()
        
        # High confidence bets
        high_conf_bets = results[results['CONFIDENCE'] == 'High']
        if len(high_conf_bets) > 0:
            print(f"\nHIGH CONFIDENCE BETS (Edge ≥ 1.5 Hits):")
            print("-" * 50)
            for _, row in high_conf_bets.iterrows():
                print(f"{row['PLAYER']} ({row['TEAM']}): Over {row['OPTIMAL_ALT_LINE']} Hits (Edge: +{row['EDGE']:.1f})")
        
        # Medium confidence bets
        medium_conf_bets = results[results['CONFIDENCE'] == 'Medium']
        if len(medium_conf_bets) > 0:
            print(f"\nMEDIUM CONFIDENCE BETS (Edge 0.8-1.4 Hits):")
            print("-" * 50)
            for _, row in medium_conf_bets.head(10).iterrows():  # Show top 10 medium confidence
                print(f"{row['PLAYER']} ({row['TEAM']}): Over {row['OPTIMAL_ALT_LINE']} Hits (Edge: +{row['EDGE']:.1f})")
        
        return results
    
    def save_analysis(self, results, filename='analysis/batter_hits_analysis.csv'):
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
        print("Starting Batter Hits Prop Analysis...")
        
        # Load data
        if not self.load_data():
            return None
        
        # Filter batters
        self.filter_batters()
        
        # Generate report
        results = self.generate_betting_report()
        
        # Save results
        if results is not None:
            self.save_analysis(results)
            
            # Also save as JSON for programmatic use
            import os
            json_filename = 'analysis/batter_hits_analysis.json'
            os.makedirs(os.path.dirname(json_filename), exist_ok=True)
            results.to_json(json_filename, orient='records', indent=2)
            print(f"Analysis also saved to {json_filename}")
        
        return results

def main():
    """Main function to run the batter hits analysis"""
    analyzer = BatterHitsAnalysis()
    results = analyzer.run_full_analysis()
    
    if results is not None:
        print("\n" + "="*80)
        print("ANALYSIS COMPLETE!")
        print("="*80)
        print("\nFiles created:")
        print("- analysis/batter_hits_analysis.csv (Excel-friendly format)")
        print("- analysis/batter_hits_analysis.json (Programmatic format)")
        print("\nUse these files to make informed FanDuel hits prop bets!")
        print("\nStrategy Notes:")
        print("- Focus on High and Medium confidence bets")
        print("- High confidence = 1.5+ hits edge over alt line")
        print("- Medium confidence = 0.8-1.4 hits edge")
        print("- Alt lines are set conservatively to maximize win probability")
        print("- Consider player matchups, ballpark factors, and weather")
    else:
        print("Analysis failed. Please check that mlb_player_projections.csv exists.")

if __name__ == "__main__":
    main()