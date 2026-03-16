import requests
import json
import os
import time

API_KEY = os.getenv("RAPIDAPI_KEY")
API_HOST = "flashlive-sports.p.rapidapi.com"

def fetch_data(h, d, a):
    url = f"https://{API_HOST}/v1/results/search-by-odds"
    headers = {"X-RapidAPI-Key": API_KEY, "X-RapidAPI-Host": API_HOST}
    
    # ULTRA-WIDE MARGIN (0.20)
    # This captures 2.95 to 3.35 if you enter 3.15.
    params = {
        "home_min": round(h - 0.20, 2), "home_max": round(h + 0.20, 2),
        "draw_min": round(d - 0.20, 2), "draw_max": round(d + 0.20, 2),
        "away_min": round(a - 0.20, 2), "away_max": round(a + 0.20, 2)
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=20)
        print(f"DEBUG: Status {response.status_code}")
        data = response.json()
        return data.get('data', [])
    except:
        return []

results = []
if os.path.exists('target_link.txt'):
    with open('target_link.txt', 'r') as f:
        line = f.readline().strip()
        if line and ',' in line:
            o = [float(x.strip()) for x in line.split(',')]
            matches = fetch_data(o[0], o[1], o[2])
            if matches:
                total = len(matches)
                h_w = len([m for m in matches if m.get('result') == 'H'])
                d_w = len([m for m in matches if m.get('result') == 'D'])
                a_w = len([m for m in matches if m.get('result') == 'A'])
                results.append({
                    "odds": f"{o[0]} | {o[1]} | {o[2]}",
                    "count": total,
                    "percentage": {"Home": round((h_w/total)*100), "Draw": round((d_w/total)*100), "Away": round((a_w/total)*100)},
                    "past_games": [f"{m.get('home_team')} vs {m.get('away_team')} ({m.get('result')})" for m in matches[:5]]
                })

with open('results.json', 'w') as f:
    json.dump(results, f, indent=4)
