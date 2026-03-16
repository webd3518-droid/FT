import requests
import json
import os
import time

# Pulls the key from GitHub Secrets
API_KEY = os.getenv("RAPIDAPI_KEY")
API_HOST = "flashlive-sports.p.rapidapi.com"

def fetch_history(h, d, a, margin):
    url = f"https://{API_HOST}/v1/results/search-by-odds"
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": API_HOST
    }
    
    # Define the range based on the margin provided
    params = {
        "home_min": round(h - margin, 2),
        "home_max": round(h + margin, 2),
        "draw_min": round(d - margin, 2),
        "draw_max": round(d + margin, 2),
        "away_min": round(a - margin, 2),
        "away_max": round(a + margin, 2),
        "limit": 50  # Get more matches for better data
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=20)
        if response.status_code != 200:
            print(f"API Error: Status {response.status_code}")
            return None
            
        data = response.json()
        return data.get('data', [])
    except Exception as e:
        print(f"Connection Error: {e}")
        return None

def process_game(h, d, a):
    # STEP 1: Try a very tight search (0.02 margin)
    matches = fetch_history(h, d, a, 0.02)
    
    # STEP 2: If nothing, try a 0.05 margin
    if not matches:
        print(f"No exact matches for {h}, {d}, {a}. Widening search...")
        matches = fetch_history(h, d, a, 0.05)
        
    # STEP 3: Final attempt with a 0.10 margin (Guaranteed to find common odds)
    if not matches:
        print(f"Still nothing. Using wide 0.10 margin...")
        matches = fetch_history(h, d, a, 0.10)

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
        "past_games": [f"{m.get('home_team')} vs {m.get('away_team')} ({m.get('result')})" for m in matches[:8]]
    }

# Execute for the first game in target_link.txt
results = []
if os.path.exists('target_link.txt'):
    with open('target_link.txt', 'r') as f:
        line = f.readline()
        if line and ',' in line:
            try:
                odds = [float(x.strip()) for x in line.split(',')]
                res = process_game(odds[0], odds[1], odds[2])
                if res: results.append(res)
            except Exception as e:
                print(f"Parsing error: {e}")

with open('results.json', 'w') as f:
    json.dump(results, f, indent=4)
