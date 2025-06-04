import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
import os

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    print("Selenium not available, using requests only")
    SELENIUM_AVAILABLE = False

class MLBScraper:
    def __init__(self):
        self.url = "https://www.sportsline.com/mlb/expert-projections/simulation/"
        self.data = []
        self.excluded_columns = ["FP", "FD EXP", "DK EXP", "DK", "FD", "OWNERSHIP"]
        
    def setup_driver(self):
        """Setup Chrome driver with options"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in background
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return driver
        except Exception as e:
            print(f"Error setting up Chrome driver: {e}")
            print("Trying alternative approach with requests...")
            return None
    
    def scrape_with_requests(self):
        """Fallback method using requests and BeautifulSoup"""
        print("Trying to scrape with requests...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        try:
            response = requests.get(self.url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            return self.parse_table_data(soup)
            
        except Exception as e:
            print(f"Error with requests method: {e}")
            return []
    
    def parse_table_data(self, soup):
        """Parse table data from BeautifulSoup object"""
        # Find the table containing player data
        table = soup.find('table')
        
        if not table:
            print("No table found on the page")
            return []
        
        # Extract headers
        headers = []
        header_row = table.find('thead')
        if header_row:
            for th in header_row.find_all('th'):
                headers.append(th.get_text(strip=True))
        else:
            # If no thead, try to get headers from first row
            first_row = table.find('tr')
            if first_row:
                for th in first_row.find_all(['th', 'td']):
                    headers.append(th.get_text(strip=True))
        
        print(f"Found headers: {headers}")
        
        # Filter out excluded columns
        filtered_headers = [h for h in headers if h not in self.excluded_columns]
        print(f"Filtered headers: {filtered_headers}")
        
        # Extract data rows
        rows = table.find('tbody')
        if not rows:
            rows = table  # If no tbody, use the whole table
        
        data = []
        for row in rows.find_all('tr')[1:]:  # Skip header row
            cells = row.find_all(['td', 'th'])
            if len(cells) >= len(headers):
                row_data = {}
                for i, header in enumerate(headers):
                    if header not in self.excluded_columns and i < len(cells):
                        cell_text = cells[i].get_text(strip=True)
                        row_data[header] = cell_text
                
                if row_data:  # Only add if we have data
                    data.append(row_data)
        
        print(f"Scraped {len(data)} player records")
        return data
    
    def scrape_data(self):
        """Scrape MLB player projection data"""
        print("Starting MLB data scraping...")
        
        # First try with Selenium
        driver = self.setup_driver()
        
        if driver:
            try:
                # Navigate to the website
                print(f"Navigating to: {self.url}")
                driver.get(self.url)
                
                # Wait for the page to load
                time.sleep(5)
                
                # Wait for the table to be present
                wait = WebDriverWait(driver, 20)
                table = wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
                
                # Get page source and parse with BeautifulSoup
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                self.data = self.parse_table_data(soup)
                
            except Exception as e:
                print(f"Error during Selenium scraping: {str(e)}")
                print("Falling back to requests method...")
                self.data = self.scrape_with_requests()
                
            finally:
                driver.quit()
        else:
            # Fallback to requests method
            self.data = self.scrape_with_requests()
        
        return self.data
    
    def save_to_csv(self, filename="data/mlb_player_projections.csv"):
        """Save scraped data to CSV file"""
        if not self.data:
            print("No data to save")
            return
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        df = pd.DataFrame(self.data)
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")
        print(f"Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        
    def save_to_json(self, filename="data/mlb_player_projections.json"):
        """Save scraped data to JSON file"""
        if not self.data:
            print("No data to save")
            return
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        print(f"Data saved to {filename}")
    
    def display_sample(self, n=5):
        """Display sample of scraped data"""
        if not self.data:
            print("No data to display")
            return
        
        print(f"\nSample of {min(n, len(self.data))} records:")
        for i, record in enumerate(self.data[:n]):
            print(f"\nRecord {i+1}:")
            for key, value in record.items():
                print(f"  {key}: {value}")

def main():
    """Main function to run the scraper"""
    scraper = MLBScraper()
    
    # Scrape the data
    data = scraper.scrape_data()
    
    if data:
        # Display sample
        scraper.display_sample(3)
        
        # Save to both CSV and JSON
        scraper.save_to_csv()
        scraper.save_to_json()
        
        print("\nScraping completed successfully!")
    else:
        print("No data was scraped. Please check the website structure.")

if __name__ == "__main__":
    main()