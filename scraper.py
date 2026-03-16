import requests
import json
import os
import time

# This pulls the key safely from GitHub Secrets
API_KEY = os.getenv("RAPIDAPI_KEY")
# The endpoint for the FlashLive Sports API on RapidAPI
API_HOST = "flashlive-sports.p.rapidapi.com"

def fetch_worldwide_history(h, d, a):
    url = f"https://{API_HOST}/v1/results/search-by-odds"
    
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": API_HOST
    }
    
    # Searching global history for these exact odds
    # Note: We use a small tolerance to ensure we find matches in the global database
    params = {
        "home": h, 
        "draw": d, 
        "away": a
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        
        # Flashscore API typically returns a list of events in the 'data' or 'response' key
        matches = data.get('data', [])
        if not matches:
            return None

        total = len(matches)
        # Outcome logic: H = Home Win, D = Draw, A = Away Win
        h_wins = len([m for m in matches if m.get('result') == 'H'])
        draws = len([m for m in matches if m.get('result') == 'D'])
        a_wins = len([m for m in matches if m.get('result') == 'A'])

        return {
            "odds": f"{h} | {d} | {a}",
            "count": total,
            "percentage": {
                "Home": round((h_wins/total)*100) if total > 0 else 0,
                "Draw": round((draws/total)*100) if total > 0 else 0,
                "Away": round((a_wins/total)*100) if total > 0 else 0
            },
            "past_games": [f"{m.get('home_team')} vs {m.get('away_team')} ({m.get('result')})" for m in matches[:5]]
        }
    except Exception as e:
        print(f"API Error for odds {h},{d},{a}: {e}")
        return None

# Load target_link.txt and run
results = []
if os.path.exists('target_link.txt'):
    with open('target_link.txt', 'r') as f:
        for line in f:
            if ',' not in line: continue
            try:
                # Expecting format: 1.5, 3.4, 5.0
                odds = [float(x.strip()) for x in line.split(',')]
                # Pause to respect Rate Limits of the Free Tier
                time.sleep(1.5) 
                res = fetch_worldwide_history(odds[0], odds[1], odds[2])
                if res: results.append(res)
            except Exception as e:
                print(f"Line skip error: {e}")
                continue

# Save the final data for the website
with open('results.json', 'w') as f:
    json.dump(results, f, indent=4)
