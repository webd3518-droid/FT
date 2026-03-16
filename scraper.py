import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def get_flashscore_data(h_target, d_target, a_target):
    chrome_options = Options()
    chrome_options.add_argument("--headless") # Runs without a visible window
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # We point to the 'Results' archive which covers worldwide games
    # Flashscore structure requires specific URL patterns for niche leagues
    archive_url = "https://www.flashscore.com/football/world/results/" 
    
    try:
        driver.get(archive_url)
        # The script would here 'scroll' and 'scrape' the odds elements
        # Note: This is a simplified logic for your GitHub Action structure
        
        # We will simulate the finding of 10 matches for your specific odds
        matches_found = [] 
        
        # Closing driver
        driver.quit()
        
        return {
            "odds": f"{h_target} | {d_target} | {a_target}",
            "count": 12, # Example count
            "percentage": {"Home": 50, "Draw": 20, "Away": 30},
            "past_games": ["Kazakhstan vs Armenia (H)", "Myanmar vs Thailand (D)"]
        }
    except Exception as e:
        print(f"Error scraping Flashscore: {e}")
        return None

# Main execution logic
results = []
with open('target_link.txt', 'r') as f:
    for line in f:
        if ',' not in line: continue
        o = [float(x.strip()) for x in line.split(',')]
        res = get_flashscore_data(o[0], o[1], o[2])
        if res: results.append(res)

with open('results.json', 'w') as f:
    json.dump(results, f)
