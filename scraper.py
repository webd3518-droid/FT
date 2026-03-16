import requests
import json
import os
import time

# Security: Pulls the key from GitHub Secrets
API_KEY = os.getenv("RAPIDAPI_KEY")
API_HOST = "flashlive-sports.p.rapidapi.com"

def fetch_worldwide_history(h, d, a):
    url = f"https://{API_HOST}/v1/results/search-by-odds"
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": API_HOST
    }
    
    # Using a 0.05 tolerance to ensure we find similar matches globally
    params = {
        "home": h,
        "draw": d,
        "away": a,
        "tolerance": 0.05 
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        data = response.json()
        matches = data.get('data', [])
        
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

# Single Game Logic
results = []
if os.path.exists('target_link.txt'):
    with open('target_link.txt', 'r') as f:
        # We only look at the first line
        first_line = f.readline()
        if first_line and ',' in first_line:
            try:
                odds = [float(x.strip()) for x in first_line.split(',')]
                res = fetch_worldwide_history(odds[0], odds[1], odds[2])
                if res:
                    results.append(res)
            except Exception as e:
                print(f"Error parsing odds: {e}")

# Save only the one result
with open('results.json', 'w') as f:
    json.dump(results, f, indent=4)
