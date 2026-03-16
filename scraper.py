import pandas as pd
import json

# This list covers major leagues across multiple years for a huge database
SOURCES = [
    # 2025/2026
    "https://www.football-data.co.uk/mmz4281/2526/E0.csv", "https://www.football-data.co.uk/mmz4281/2526/SP1.csv",
    # 2024/2025
    "https://www.football-data.co.uk/mmz4281/2425/E0.csv", "https://www.football-data.co.uk/mmz4281/2425/SP1.csv",
    "https://www.football-data.co.uk/mmz4281/2425/D1.csv", "https://www.football-data.co.uk/mmz4281/2425/I1.csv",
    "https://www.football-data.co.uk/mmz4281/2425/F1.csv", "https://www.football-data.co.uk/mmz4281/2425/N1.csv",
    # 2023/2024 
    "https://www.football-data.co.uk/mmz4281/2324/E0.csv", "https://www.football-data.co.uk/mmz4281/2324/SP1.csv",
    "https://www.football-data.co.uk/mmz4281/2324/D1.csv", "https://www.football-data.co.uk/mmz4281/2324/I1.csv",
    "https://www.football-data.co.uk/mmz4281/2324/F1.csv", "https://www.football-data.co.uk/mmz4281/2324/B1.csv"
]

def analyze_game(h, d, a, big_df):
    # If the app is empty, we increase the 'margin' so it finds SIMILAR odds
    # 0.25 means if you enter 1.50, it looks for anything between 1.25 and 1.75
    margin = 0.25
    matches = big_df[
        (big_df['B365H'].between(h - margin, h + margin)) &
        (big_df['B365D'].between(d - margin, d + margin))
    ].tail(10)
    
    if matches.empty: return None
    
    total = len(matches)
    h_wins = len(matches[matches['FTR'] == 'H'])
    draws = len(matches[matches['FTR'] == 'D'])
    a_wins = len(matches[matches['FTR'] == 'A'])
    
    return {
        "target_odds": f"{h}/{d}/{a}",
        "stats": {"home": round((h_wins/total)*100), "draw": round((draws/total)*100), "away": round((a_wins/total)*100)},
        "recent": matches.tail(2)['FTR'].tolist(),
        "history": [f"{r['HomeTeam']} v {r['AwayTeam']} ({r['FTR']})" for _, r in matches.iterrows()]
    }

# 1. Download and merge everything
all_data = []
for url in SOURCES:
    try:
        df = pd.read_csv(url)
        # Standardize columns
        subset = df[['HomeTeam', 'AwayTeam', 'FTR', 'B365H', 'B365D', 'B365A']]
        all_data.append(subset)
    except: continue

mega_df = pd.concat(all_data, ignore_index=True)

# 2. Process target_link.txt
results = []
try:
    with open('target_link.txt', 'r') as f:
        for line in f:
            if ',' not in line: continue
            o = [float(x.strip()) for x in line.split(',')]
            res = analyze_game(o[0], o[1], o[2], mega_df)
            if res: results.append(res)
except: pass

# 3. Save
with open('results.json', 'w') as f:
    json.dump(results, f)
