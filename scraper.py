import requests
import json
import os
import time

API_KEY = os.getenv("RAPIDAPI_KEY")
API_HOST = "flashlive-sports.p.rapidapi.com"

def fetch_worldwide_history(h, d, a):
    url = f"https://{API_HOST}/v1/results/search-by-odds"
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": API_HOST
    }
    
    # NEW: We use a small range (tolerance) because exact 18.09 is rare.
    # We ask the API for anything similar to these odds.
    params = {
        "home": h,
        "draw": d,
        "away": a,
        "tolerance": 0.05 # Look for matches within 5% of these odds
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        data = response.json()
        
        # Check if 'data' exists and has content
        matches = data.get('data', [])
        
        if not matches:
            # If still nothing, we try one more time with a wider range for high odds
            if h > 10 or a > 10:
                params["tolerance"] = 0.10
                response = requests.get(url, headers=headers, params=params, timeout=15)
                matches = response.json().get('data', [])
            
        if not matches: return None

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
        print(f"API Error: {e}")
        return None

# Standard Execution Logic
results = []
if os.path.exists('target_link.txt'):
    with open('target_link.txt', 'r') as f:
        for line in f:
            if ',' not in line: continue
            try:
                odds = [float(x.strip()) for x in line.split(',')]
                time.sleep(1.5) 
                res = fetch_worldwide_history(odds[0], odds[1], odds[2])
                if res: results.append(res)
            except: continue

with open('results.json', 'w') as f:
    json.dump(results, f, indent=4)
