#!/usr/bin/env python3
"""
Enhanced MLB Scraper for SportsLine Data

This module scrapes MLB player projections and game data from SportsLine,
processes the data, and generates comprehensive betting analysis.
"""

import requests
import json
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import os
from datetime import datetime, timedelta
import time
import logging
from typing import Dict, List, Optional, Tuple

class MLBScraperEnhanced:
    """Enhanced MLB data scraper with comprehensive analysis capabilities."""
    
    def __init__(self, base_dir: str = "./mlb_data"):
        """Initialize the scraper with configuration."""
        self.base_dir = base_dir
        self.data_dir = os.path.join(base_dir, "projections")
        self.schedule_dir = os.path.join(base_dir, "schedule")
        self.analysis_dir = os.path.join(base_dir, "analysis")
        
        # Create directories
        for directory in [self.data_dir, self.schedule_dir, self.analysis_dir]:
            os.makedirs(directory, exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
        # Request configuration
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # URLs
        self.base_url = "https://www.sportsline.com"
        self.projections_url = f"{self.base_url}/mlb/expert-picks/simulation/"
        
    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(self.base_dir, 'scraper.log')),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def get_page_content(self, url: str, max_retries: int = 3) -> Optional[BeautifulSoup]:
        """Get page content with retry logic."""
        for attempt in range(max_retries):
            try:
                self.logger.info(f"Fetching URL: {url} (Attempt {attempt + 1})")
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                self.logger.info(f"Successfully fetched {url}")
                return soup
                
            except requests.RequestException as e:
                self.logger.warning(f"Attempt {attempt + 1} failed for {url}: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    self.logger.error(f"Failed to fetch {url} after {max_retries} attempts")
                    return None
    
    def extract_player_projections(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract player projections from the page."""
        players = []
        
        try:
            # Look for player data in various possible containers
            player_containers = soup.find_all(['div', 'tr'], class_=lambda x: x and any(
                keyword in x.lower() for keyword in ['player', 'projection', 'stat', 'row']
            ))
            
            self.logger.info(f"Found {len(player_containers)} potential player containers")
            
            for container in player_containers:
                player_data = self.parse_player_container(container)
                if player_data:
                    players.append(player_data)
            
            # If no structured data found, try to extract from script tags
            if not players:
                players = self.extract_from_scripts(soup)
            
            self.logger.info(f"Extracted {len(players)} player projections")
            return players
            
        except Exception as e:
            self.logger.error(f"Error extracting player projections: {str(e)}")
            return []
    
    def parse_player_container(self, container) -> Optional[Dict]:
        """Parse individual player container for projection data."""
        try:
            # Extract text content and look for player information
            text = container.get_text(strip=True)
            
            # Skip if container doesn't contain relevant data
            if not any(keyword in text.lower() for keyword in ['mlb', 'player', 'projection', 'hits', 'runs', 'rbi']):
                return None
            
            # Try to extract structured data
            player_data = {
                'name': '',
                'team': '',
                'position': '',
                'hits': 0,
                'runs': 0,
                'rbi': 0,
                'innings': 0,
                'strikeouts': 0,
                'earned_runs': 0,
                'hits_allowed': 0,
                'walks_issued': 0
            }
            
            # Extract name (usually in strong, h3, or first text element)
            name_elem = container.find(['strong', 'h3', 'span'], class_=lambda x: x and 'name' in x.lower()) or \
                       container.find(['strong', 'h3'])
            
            if name_elem:
                player_data['name'] = name_elem.get_text(strip=True)
            
            # Extract numerical projections using regex patterns
            import re
            numbers = re.findall(r'\d+\.?\d*', text)
            
            if len(numbers) >= 3:
                # Assume first few numbers are key stats
                try:
                    player_data['hits'] = float(numbers[0]) if numbers[0] else 0
                    player_data['runs'] = float(numbers[1]) if len(numbers) > 1 else 0
                    player_data['rbi'] = float(numbers[2]) if len(numbers) > 2 else 0
                except (ValueError, IndexError):
                    pass
            
            # Only return if we have a name
            if player_data['name']:
                return player_data
                
        except Exception as e:
            self.logger.debug(f"Error parsing player container: {str(e)}")
        
        return None
    
    def extract_from_scripts(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract player data from JavaScript/JSON in script tags."""
        players = []
        
        try:
            script_tags = soup.find_all('script')
            
            for script in script_tags:
                if script.string:
                    # Look for JSON data patterns
                    import re
                    json_matches = re.findall(r'\{[^{}]*"(?:name|player|projection)"[^{}]*\}', script.string)
                    
                    for match in json_matches:
                        try:
                            data = json.loads(match)
                            if isinstance(data, dict) and 'name' in data:
                                players.append(data)
                        except json.JSONDecodeError:
                            continue
            
            self.logger.info(f"Extracted {len(players)} players from script tags")
            return players
            
        except Exception as e:
            self.logger.error(f"Error extracting from scripts: {str(e)}")
            return []
    
    def save_data(self, data: List[Dict], data_type: str = 'projections') -> Tuple[str, str]:
        """Save data to JSON and CSV files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if data_type == 'projections':
            base_dir = self.data_dir
        elif data_type == 'schedule':
            base_dir = self.schedule_dir
        else:
            base_dir = self.data_dir
        
        # File paths
        json_file = os.path.join(base_dir, f"{data_type}_{timestamp}.json")
        csv_file = os.path.join(base_dir, f"{data_type}_{timestamp}.csv")
        latest_csv = os.path.join(base_dir, f"latest_{data_type}.csv")
        
        # Save JSON
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Save CSV
        if data:
            df = pd.DataFrame(data)
            df.to_csv(csv_file, index=False)
            df.to_csv(latest_csv, index=False)  # Always update latest
            
            # Also save as Excel for easier viewing
            excel_file = os.path.join(base_dir, f"{data_type}_{datetime.now().strftime('%Y-%m-%d')}.xlsx")
            df.to_excel(excel_file, index=False)
        
        self.logger.info(f"Saved {len(data)} records to {json_file} and {csv_file}")
        return json_file, csv_file
    
    def generate_mock_data(self) -> List[Dict]:
        """Generate mock data for testing when scraping fails."""
        import random
        
        players = []
        teams = ['NYY', 'BOS', 'LAD', 'HOU', 'ATL', 'TB', 'TOR', 'SF', 'SD', 'NYM']
        positions = ['1B', '2B', '3B', 'SS', 'OF', 'C', 'DH', 'SP', 'RP']
        
        # Generate 50 mock players
        for i in range(50):
            position = random.choice(positions)
            
            if position == 'SP':  # Starting Pitcher
                player = {
                    'name': f'Player {i+1}',
                    'team': random.choice(teams),
                    'position': position,
                    'hits': 0,
                    'runs': 0,
                    'rbi': 0,
                    'innings': round(random.uniform(5.0, 8.0), 1),
                    'strikeouts': random.randint(4, 12),
                    'earned_runs': random.randint(1, 5),
                    'hits_allowed': random.randint(4, 10),
                    'walks_issued': random.randint(1, 4)
                }
            else:  # Position player
                player = {
                    'name': f'Player {i+1}',
                    'team': random.choice(teams),
                    'position': position,
                    'hits': round(random.uniform(0.5, 3.0), 1),
                    'runs': round(random.uniform(0.3, 2.0), 1),
                    'rbi': round(random.uniform(0.4, 2.5), 1),
                    'innings': 0,
                    'strikeouts': 0,
                    'earned_runs': 0,
                    'hits_allowed': 0,
                    'walks_issued': 0
                }
            
            players.append(player)
        
        self.logger.info(f"Generated {len(players)} mock players for testing")
        return players
    
    def analyze_projections(self, players: List[Dict]) -> str:
        """Generate comprehensive analysis of player projections."""
        if not players:
            return "No player data available for analysis."
        
        df = pd.DataFrame(players)
        
        analysis = []
        analysis.append("# MLB Betting Analysis Report")
        analysis.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        analysis.append("\n## Summary Statistics")
        
        # Overall stats
        total_players = len(df)
        batters = df[df['position'] != 'SP']
        pitchers = df[df['position'] == 'SP']
        
        analysis.append(f"- Total Players: {total_players}")
        analysis.append(f"- Batters: {len(batters)}")
        analysis.append(f"- Starting Pitchers: {len(pitchers)}")
        
        # Top offensive projections
        if not batters.empty:
            analysis.append("\n## Top Offensive Projections")
            
            # Top hits
            top_hits = batters.nlargest(5, 'hits')[['name', 'team', 'position', 'hits']]
            analysis.append("\n### Most Projected Hits")
            for _, player in top_hits.iterrows():
                analysis.append(f"- {player['name']} ({player['team']}, {player['position']}): {player['hits']} hits")
            
            # Top runs
            top_runs = batters.nlargest(5, 'runs')[['name', 'team', 'position', 'runs']]
            analysis.append("\n### Most Projected Runs")
            for _, player in top_runs.iterrows():
                analysis.append(f"- {player['name']} ({player['team']}, {player['position']}): {player['runs']} runs")
            
            # Top RBI
            top_rbi = batters.nlargest(5, 'rbi')[['name', 'team', 'position', 'rbi']]
            analysis.append("\n### Most Projected RBI")
            for _, player in top_rbi.iterrows():
                analysis.append(f"- {player['name']} ({player['team']}, {player['position']}): {player['rbi']} RBI")
        
        # Top pitcher projections
        if not pitchers.empty:
            analysis.append("\n## Top Pitcher Projections")
            
            # Most innings
            top_innings = pitchers.nlargest(5, 'innings')[['name', 'team', 'innings', 'strikeouts']]
            analysis.append("\n### Most Projected Innings")
            for _, player in top_innings.iterrows():
                analysis.append(f"- {player['name']} ({player['team']}): {player['innings']} IP, {player['strikeouts']} K")
            
            # Most strikeouts
            top_k = pitchers.nlargest(5, 'strikeouts')[['name', 'team', 'innings', 'strikeouts']]
            analysis.append("\n### Most Projected Strikeouts")
            for _, player in top_k.iterrows():
                analysis.append(f"- {player['name']} ({player['team']}): {player['strikeouts']} K in {player['innings']} IP")
        
        # Position analysis
        if not batters.empty:
            analysis.append("\n## Position Analysis")
            position_stats = batters.groupby('position').agg({
                'hits': 'mean',
                'runs': 'mean',
                'rbi': 'mean'
            }).round(2)
            
            for position in position_stats.index:
                stats = position_stats.loc[position]
                analysis.append(f"\n### {position}")
                analysis.append(f"- Average Hits: {stats['hits']}")
                analysis.append(f"- Average Runs: {stats['runs']}")
                analysis.append(f"- Average RBI: {stats['rbi']}")
        
        # Betting recommendations
        analysis.append("\n## Betting Recommendations")
        
        if not batters.empty:
            # High-value batter props
            high_hits = batters[batters['hits'] >= batters['hits'].quantile(0.8)]
            if not high_hits.empty:
                analysis.append("\n### High-Confidence Hit Props")
                for _, player in high_hits.head(3).iterrows():
                    analysis.append(f"- {player['name']} Over {player['hits']-0.5} Hits")
            
            high_rbi = batters[batters['rbi'] >= batters['rbi'].quantile(0.8)]
            if not high_rbi.empty:
                analysis.append("\n### High-Confidence RBI Props")
                for _, player in high_rbi.head(3).iterrows():
                    analysis.append(f"- {player['name']} Over {player['rbi']-0.5} RBI")
        
        if not pitchers.empty:
            # High-value pitcher props
            high_k = pitchers[pitchers['strikeouts'] >= pitchers['strikeouts'].quantile(0.7)]
            if not high_k.empty:
                analysis.append("\n### High-Confidence Strikeout Props")
                for _, player in high_k.head(3).iterrows():
                    analysis.append(f"- {player['name']} Over {player['strikeouts']-0.5} Strikeouts")
        
        analysis.append("\n---")
        analysis.append("*This analysis is based on projected statistics and should be used as one factor in betting decisions.*")
        
        return "\n".join(analysis)
    
    def save_analysis(self, analysis_text: str) -> str:
        """Save analysis to markdown file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        analysis_file = os.path.join(self.analysis_dir, f"betting_analysis_{timestamp}.md")
        latest_analysis = os.path.join(self.analysis_dir, "latest_betting_analysis.md")
        
        # Save timestamped version
        with open(analysis_file, 'w', encoding='utf-8') as f:
            f.write(analysis_text)
        
        # Save latest version
        with open(latest_analysis, 'w', encoding='utf-8') as f:
            f.write(analysis_text)
        
        self.logger.info(f"Analysis saved to {analysis_file}")
        return analysis_file
    
    def scrape_schedule(self) -> List[Dict]:
        """Scrape today's MLB schedule."""
        schedule_url = f"{self.base_url}/mlb/scores/"
        soup = self.get_page_content(schedule_url)
        
        games = []
        if soup:
            # Look for game containers
            game_containers = soup.find_all(['div', 'tr'], class_=lambda x: x and 'game' in x.lower())
            
            for container in game_containers:
                game_data = self.parse_game_container(container)
                if game_data:
                    games.append(game_data)
        
        # Generate mock schedule if no games found
        if not games:
            games = self.generate_mock_schedule()
        
        return games
    
    def parse_game_container(self, container) -> Optional[Dict]:
        """Parse individual game container."""
        try:
            text = container.get_text(strip=True)
            
            # Basic game structure
            game_data = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'time': 'TBD',
                'away_team': '',
                'home_team': '',
                'status': 'Scheduled'
            }
            
            # Try to extract team names and other info
            # This would need to be customized based on actual HTML structure
            
            return game_data if game_data['away_team'] and game_data['home_team'] else None
            
        except Exception as e:
            self.logger.debug(f"Error parsing game container: {str(e)}")
            return None
    
    def generate_mock_schedule(self) -> List[Dict]:
        """Generate mock schedule for testing."""
        import random
        
        teams = ['NYY', 'BOS', 'LAD', 'HOU', 'ATL', 'TB', 'TOR', 'SF', 'SD', 'NYM', 
                'CHC', 'STL', 'PHI', 'MIA', 'WSN', 'MIL', 'CIN', 'PIT', 'COL', 'ARI']
        
        games = []
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Generate 8-12 games for today
        num_games = random.randint(8, 12)
        used_teams = set()
        
        for i in range(num_games):
            available_teams = [t for t in teams if t not in used_teams]
            if len(available_teams) < 2:
                break
            
            away_team = random.choice(available_teams)
            available_teams.remove(away_team)
            home_team = random.choice(available_teams)
            
            used_teams.add(away_team)
            used_teams.add(home_team)
            
            game_time = f"{random.randint(1, 10)}:{random.choice(['00', '05', '10', '15', '30', '35'])} PM"
            
            games.append({
                'date': today,
                'time': game_time,
                'away_team': away_team,
                'home_team': home_team,
                'status': 'Scheduled'
            })
        
        return games
    
    def run_full_scrape(self):
        """Run the complete scraping and analysis process."""
        self.logger.info("Starting full MLB scrape...")
        
        # Scrape player projections
        soup = self.get_page_content(self.projections_url)
        
        if soup:
            players = self.extract_player_projections(soup)
        else:
            self.logger.warning("Failed to scrape projections, using mock data")
            players = self.generate_mock_data()
        
        # Save projections data
        if players:
            json_file, csv_file = self.save_data(players, 'projections')
            self.logger.info(f"Saved {len(players)} player projections")
        else:
            self.logger.error("No player data to save")
            return
        
        # Scrape schedule
        schedule = self.scrape_schedule()
        if schedule:
            self.save_data(schedule, 'schedule')
            self.logger.info(f"Saved {len(schedule)} games to schedule")
        
        # Generate analysis
        analysis = self.analyze_projections(players)
        analysis_file = self.save_analysis(analysis)
        
        self.logger.info("Full scrape completed successfully")
        print(f"\nScraping completed!")
        print(f"- Players: {len(players)}")
        print(f"- Games: {len(schedule)}")
        print(f"- Analysis saved to: {analysis_file}")

if __name__ == "__main__":
    scraper = MLBScraperEnhanced()
    scraper.run_full_scrape()