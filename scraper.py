import requests
import json
import os
import time

# Security: Pulls from GitHub Secrets
API_KEY = os.getenv("RAPIDAPI_KEY")
API_HOST = "flashlive-sports.p.rapidapi.com"

def get_matches(h, d, a):
    url = f"https://{API_HOST}/v1/results/search-by-odds"
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": API_HOST
    }
    
    # WE WIDEN THE SEARCH: Looking for anything within 0.10 of your odds
    # For 3.15, this looks for 3.05 to 3.25.
    params = {
        "home_min": round(h - 0.10, 2),
        "home_max": round(h + 0.10, 2),
        "draw_min": round(d - 0.10, 2),
        "draw_max": round(d + 0.10, 2),
        "away_min": round(a - 0.10, 2),
        "away_max": round(a + 0.10, 2)
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=20)
        # If the key is wrong, this will show in GitHub Actions logs
        if response.status_code != 200:
            print(f"CRITICAL: API returned status {response.status_code}")
            return []
            
        data = response.json()
        return data.get('data', [])
    except Exception as e:
        print(f"CONNECTION ERROR: {e}")
        return []

# Process target_link.txt
final_results = []
if os.path.exists('target_link.txt'):
    with open('target_link.txt', 'r') as f:
        line = f.readline().strip()
        if line and ',' in line:
            odds = [float(x.strip()) for x in line.split(',')]
            print(f"SEARCHING FOR: {odds}")
            
            matches = get_matches(odds[0], odds[1], odds[2])
            
            if matches:
                total = len(matches)
                h_wins = len([m for m in matches if m.get('result') == 'H'])
                draws = len([m for m in matches if m.get('result') == 'D'])
                a_wins = len([m for m in matches if m.get('result') == 'A'])

                final_results.append({
                    "odds": f"{odds[0]} | {odds[1]} | {odds[2]}",
                    "count": total,
                    "percentage": {
                        "Home": round((h_wins/total)*100),
                        "Draw": round((draws/total)*100),
                        "Away": round((a_wins/total)*100)
                    },
                    "past_games": [f"{m.get('home_team')} vs {m.get('away_team')} ({m.get('result')})" for m in matches[:5]]
                })
            else:
                print("ZERO MATCHES FOUND IN DATABASE.")

# OVERWRITE RESULTS.JSON
with open('results.json', 'w') as f:
    json.dump(final_results, f, indent=4)
