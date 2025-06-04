# MLB Betting Scraper 🏟️⚾

A comprehensive MLB player projections and betting analysis tool that scrapes data from SportsLine and generates detailed reports for informed betting decisions.

## 🚀 Features

- **Real-time Data Scraping**: Automatically scrapes MLB player projections from SportsLine
- **Comprehensive Analysis**: Generates detailed betting analysis with player comparisons
- **Multiple Output Formats**: CSV, JSON, Excel, and Markdown reports
- **Position-Specific Insights**: Tailored analysis for pitchers vs. position players
- **Automated Scheduling**: Easy setup for regular data updates
- **Clean Data Structure**: Organized output with timestamped files

## 📋 Requirements

- Python 3.8+
- Chrome/Chromium browser (for Selenium)
- Internet connection

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/markybuilds/mlb-betting-scraper.git
   cd mlb-betting-scraper
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   ```

3. **Activate the virtual environment**:
   - Windows: `.venv\Scripts\activate`
   - macOS/Linux: `source .venv/bin/activate`

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🎯 Quick Start

### Basic Usage

Run the main scraper to get today's projections and analysis:

```bash
python run_scraper.py
```

This will:
- Scrape current MLB projections from SportsLine
- Generate comprehensive betting analysis
- Save data in multiple formats (CSV, JSON, Excel, Markdown)
- Create timestamped files for historical tracking

### Output Files

After running, you'll find organized data in the `mlb_data/` directory:

```
mlb_data/
├── projections/
│   ├── projections_YYYYMMDD_HHMMSS.csv
│   ├── projections_YYYYMMDD_HHMMSS.json
│   ├── projections_YYYY-MM-DD.xlsx
│   └── latest_projections.csv
├── schedule/
│   ├── schedule_YYYYMMDD_HHMMSS.csv
│   ├── schedule_YYYYMMDD_HHMMSS.json
│   ├── schedule_YYYY-MM-DD.xlsx
│   └── latest_schedule.csv
└── analysis/
    ├── betting_analysis_YYYYMMDD_HHMMSS.md
    └── latest_betting_analysis.md
```

## 📊 Data Fields

### Player Projections
- **Batters**: Hits, Runs, RBI, Position
- **Pitchers**: Innings Pitched, Strikeouts, Earned Runs, Hits Allowed, Walks

### Analysis Metrics
- Position-specific averages and comparisons
- Top performers identification
- Value betting opportunities
- Risk assessment indicators

## 🔧 Configuration

### Customizing the Scraper

Edit `mlb_scraper_enhanced.py` to modify:
- Scraping intervals
- Data processing logic
- Output formats
- Analysis parameters

### Advanced Usage

For custom scraping or analysis:

```python
from mlb_scraper_enhanced import MLBScraper

scraper = MLBScraper()
data = scraper.scrape_projections()
analysis = scraper.generate_analysis(data)
```

## 📈 Analysis Features

### Betting Insights
- **Value Identification**: Spots players with projections significantly above/below market expectations
- **Position Comparisons**: Analyzes performance relative to position averages
- **Risk Assessment**: Identifies high-variance vs. consistent performers
- **Trend Analysis**: Historical performance patterns

### Report Sections
1. **Executive Summary**: Key insights and top opportunities
2. **Top Performers**: Highest projected players by category
3. **Position Analysis**: Detailed breakdowns by position
4. **Value Plays**: Potential betting opportunities
5. **Risk Factors**: Important considerations

## 🤖 Automation

### Scheduled Runs

Set up automated daily runs using:

**Windows (Task Scheduler)**:
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger for daily execution
4. Action: Start Program → `python run_scraper.py`

**macOS/Linux (Cron)**:
```bash
# Run daily at 9 AM
0 9 * * * /path/to/python /path/to/run_scraper.py
```

## 🛡️ Error Handling

The scraper includes robust error handling for:
- Network connectivity issues
- Website structure changes
- Data parsing errors
- File system permissions

## 📝 Logging

Detailed logs are generated for:
- Scraping progress
- Data processing steps
- Error diagnostics
- Performance metrics

## 🔍 Troubleshooting

### Common Issues

1. **Chrome Driver Issues**:
   - Ensure Chrome is installed and up-to-date
   - Check ChromeDriver compatibility

2. **Scraping Failures**:
   - Verify internet connection
   - Check if SportsLine website structure changed
   - Review error logs for specific issues

3. **Data Processing Errors**:
   - Ensure all dependencies are installed
   - Check file permissions in output directory

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

**Important**: This tool is for informational and educational purposes only. 

- **Not Financial Advice**: The analysis and projections provided are not financial or betting advice
- **Use Responsibly**: Always conduct your own research and bet responsibly
- **Risk Awareness**: Sports betting involves risk of loss
- **Legal Compliance**: Ensure sports betting is legal in your jurisdiction
- **Data Accuracy**: While we strive for accuracy, always verify data independently

## 🎯 Next Steps

After installation:

1. **Run Initial Test**: Execute `python run_scraper.py` to verify setup
2. **Review Output**: Check generated files in `mlb_data/` directory
3. **Customize Analysis**: Modify parameters based on your betting strategy
4. **Set Up Automation**: Configure scheduled runs for regular updates
5. **Monitor Performance**: Track accuracy and adjust as needed

---

**Happy Betting! 🎲⚾**

Remember: The house always has an edge, but informed decisions can improve your odds. Use this tool as part of a comprehensive research strategy, never as your sole decision-making factor.
