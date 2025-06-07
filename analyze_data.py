import pandas as pd
import json

def analyze_mlb_data():
    """Simple analysis of the scraped MLB data"""
    
    # Load the CSV data
    try:
        df = pd.read_csv('data/mlb_player_projections.csv')
        print("MLB Player Projections Analysis")
        print("=" * 40)
        print(f"Total players: {len(df)}")
        print(f"Columns: {list(df.columns)}")
        
        # Basic statistics
        print("\nBasic Statistics:")
        print("-" * 20)
        
        # Position distribution
        print("\nPosition Distribution:")
        position_counts = df['POS'].value_counts()
        for pos, count in position_counts.items():
            print(f"  {pos}: {count}")
        
        # Team distribution
        print("\nTeam Distribution (Top 10):")
        team_counts = df['TEAM'].value_counts().head(10)
        for team, count in team_counts.items():
            print(f"  {team}: {count}")
        
        # Convert numeric columns for analysis
        numeric_cols = ['RBI', 'R', 'H']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Top performers
        print("\nTop 10 Players by RBI Projection:")
        top_rbi = df.nlargest(10, 'RBI')[['PLAYER', 'TEAM', 'POS', 'RBI']]
        for _, player in top_rbi.iterrows():
            print(f"  {player['PLAYER']} ({player['TEAM']}, {player['POS']}): {player['RBI']:.2f}")
        
        print("\nTop 10 Players by Runs Projection:")
        top_runs = df.nlargest(10, 'R')[['PLAYER', 'TEAM', 'POS', 'R']]
        for _, player in top_runs.iterrows():
            print(f"  {player['PLAYER']} ({player['TEAM']}, {player['POS']}): {player['R']:.2f}")
        
        print("\nTop 10 Players by Hits Projection:")
        top_hits = df.nlargest(10, 'H')[['PLAYER', 'TEAM', 'POS', 'H']]
        for _, player in top_hits.iterrows():
            print(f"  {player['PLAYER']} ({player['TEAM']}, {player['POS']}): {player['H']:.2f}")
        
        # Summary statistics
        print("\nSummary Statistics for Key Metrics:")
        print(df[numeric_cols].describe())
        
    except FileNotFoundError:
        print("Error: mlb_player_projections.csv not found. Please run the scraper first.")
    except Exception as e:
        print(f"Error analyzing data: {e}")

if __name__ == "__main__":
    analyze_mlb_data()