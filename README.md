# MLB FanDuel Prop Betting Analysis Tool

A comprehensive tool for scraping MLB player projections and analyzing optimal FanDuel prop betting opportunities for pitcher strikeouts and batter hits.

## 📁 Project Structure

```
mlb-tool/
├── 📂 data/                           # Raw scraped data
│   ├── mlb_player_projections.csv     # Player projections (CSV)
│   └── mlb_player_projections.json    # Player projections (JSON)
├── 📂 analysis/                       # Analysis results
│   ├── pitcher_strikeout_analysis.csv # Pitcher K prop analysis
│   ├── pitcher_strikeout_analysis.json
│   ├── batter_hits_analysis.csv       # Batter hits prop analysis
│   └── batter_hits_analysis.json
├── 📂 reports/                        # Summary reports (future use)
├── 📂 .venv/                          # Virtual environment
├── 📄 mlb_scraper.py                  # Core scraping script
├── 📄 pitcher_strikeout_analysis.py   # Pitcher K analysis
├── 📄 batter_hits_analysis.py         # Batter hits analysis
├── 📄 daily_update.py                 # Automated daily workflow
├── 📄 analyze_data.py                 # Basic data analysis
├── 📄 requirements.txt                # Python dependencies
├── 📄 setup.bat                       # Windows setup script
└── 📄 README.md                       # This file
```

## 🚀 Quick Start

### Initial Setup
1. Run the setup script:
   ```bash
   setup.bat
   ```

### Daily Usage
1. Run the daily update (recommended):
   ```bash
   python daily_update.py
   ```
   This will:
   - Scrape fresh MLB projection data → `data/`
   - Analyze pitcher strikeout props → `analysis/`
   - Analyze batter hits props → `analysis/`

### Manual Usage
1. **Scrape Data:**
   ```bash
   python mlb_scraper.py
   ```
   Output: `data/mlb_player_projections.csv` and `.json`

2. **Analyze Pitcher Strikeouts:**
   ```bash
   python pitcher_strikeout_analysis.py
   ```
   Output: `analysis/pitcher_strikeout_analysis.csv` and `.json`

3. **Analyze Batter Hits:**
   ```bash
   python batter_hits_analysis.py
   ```
   Output: `analysis/batter_hits_analysis.csv` and `.json`

## 📊 Output Files

### Data Files (`data/` folder)
- **mlb_player_projections.csv**: Raw scraped player projections
- **mlb_player_projections.json**: Same data in JSON format

### Analysis Files (`analysis/` folder)
- **pitcher_strikeout_analysis.csv**: Optimal strikeout prop lines with confidence levels
- **batter_hits_analysis.csv**: Optimal hits prop lines with edge calculations
- **JSON versions**: Machine-readable formats for programmatic use

## 🎯 Betting Strategy

### Pitcher Strikeouts
- **High Confidence**: 2+ strikeout edge over alternative line
- **Medium Confidence**: 1-1.9 strikeout edge
- **Focus**: Medium/High confidence bets for best ROI

### Batter Hits
- **Strategy**: Conservative "Over 0.5 Hits" props
- **Edge-based**: Sort by highest edge percentage
- **Risk Management**: Use smaller unit sizes (hits are more volatile)

## 🔧 Features

- **Automated Scraping**: Selenium + BeautifulSoup with fallback
- **Smart Analysis**: Conservative line calculations for higher win rates
- **Organized Output**: Clean folder structure for easy file management
- **Error Handling**: Robust error handling and logging
- **Daily Automation**: Single command for complete daily workflow
- **Multiple Formats**: CSV for Excel, JSON for programming

## 📋 Requirements

- Python 3.7+
- Chrome browser (for Selenium)
- Internet connection
- Dependencies in `requirements.txt`

## ⚠️ Important Notes

1. **Verify Lines**: Always check that suggested lines are available on FanDuel
2. **Additional Factors**: Consider weather, lineups, matchups, and ballpark factors
3. **Responsible Betting**: Bet within your limits and bankroll management
4. **Data Freshness**: Run daily updates for most current projections
5. **File Organization**: All output files are automatically organized into appropriate folders

## 🔄 Daily Workflow

1. Run `python daily_update.py`
2. Check `analysis/` folder for new recommendations
3. Review FanDuel for available lines
4. Place bets based on confidence levels and edge calculations
5. Track results and adjust strategy as needed

## 📈 Success Tips

- Focus on high-confidence pitcher strikeout props
- Use smaller units for hits props due to higher variance
- Track your results to refine the strategy
- Consider line shopping across multiple sportsbooks
- Stay updated with MLB news that might affect projections

---

*This tool is for educational and analytical purposes. Always gamble responsibly.*