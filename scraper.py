import requests
import json
import os
import time

API_KEY = os.getenv("RAPIDAPI_KEY")
API_HOST = "flashlive-sports.p.rapidapi.com"

def fetch_worldwide_history(h, d, a):
    # We broaden the search to find 'Similar' matches
    # This ensures we get results even if the exact decimal is slightly off
    url = f"https://{API_HOST}/v1/results/search-by-odds"
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": API_HOST
    }
    
    # We create a 5% 'Fuzzy Window' around your odds
    params = {
        "home_min": round(h * 0.95, 2),
        "home_max": round(h * 1.05, 2),
        "draw_min": round(d * 0.95, 2),
        "draw_max": round(d * 1.05, 2),
        "away_min": round(a * 0.95, 2),
        "away_max": round(a * 1.05, 2),
        "limit": 20
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        # DEBUG: Print the status to GitHub logs so we can see if the API is blocking us
        print(f"API Status: {response.status_code}") 
        
        data = response.json()
        matches = data.get('data', [])
        
        if not matches:
            return None

        total = len(matches)
        h_wins = len([m for m in matches if m.get('result') == 'H'])
        draws = len([m for m in matches if m.get('result') == 'D'])
        a_wins = len([m for m in matches if m.get('result') == 'A'])

        return {
            "odds": f"{h} | {d} | {a}",
            "count": total,
            "percentage": {
                "Home": round((h_wins/total)*100),
                "Draw": round((draws/total)*100),
                "Away": round((a_wins/total)*100)
            },
            "past_games": [f"{m.get('home_team')} vs {m.get('away_team')} ({m.get('result')})" for m in matches[:5]]
        }
    except Exception as e:
        print(f"Connection Error: {e}")
        return None

# Process ONLY the first game in target_link.txt
results = []
if os.path.exists('target_link.txt'):
    with open('target_link.txt', 'r') as f:
        line = f.readline()
        if line and ',' in line:
            try:
                o = [float(x.strip()) for x in line.split(',')]
                res = fetch_worldwide_history(o[0], o[1], o[2])
                if res: results.append(res)
            except: pass

with open('results.json', 'w') as f:
    json.dump(results, f, indent=4)
