import pandas as pd
import json

# This is our 'Library of History' - thousands of past games and their odds
SOURCES = [
    # 2025/2026 Season
    "https://www.football-data.co.uk/mmz4281/2526/E0.csv", "https://www.football-data.co.uk/mmz4281/2526/SP1.csv",
    # 2024/2025 Season
    "https://www.football-data.co.uk/mmz4281/2425/E0.csv", "https://www.football-data.co.uk/mmz4281/2425/SP1.csv",
    "https://www.football-data.co.uk/mmz4281/2425/D1.csv", "https://www.football-data.co.uk/mmz4281/2425/I1.csv",
    "https://www.football-data.co.uk/mmz4281/2425/F1.csv", "https://www.football-data.co.uk/mmz4281/2425/N1.csv",
    # 2023/2024 Season
    "https://www.football-data.co.uk/mmz4281/2324/E0.csv", "https://www.football-data.co.uk/mmz4281/2324/SP1.csv",
    "https://www.football-data.co.uk/mmz4281/2324/D1.csv", "https://www.football-data.co.uk/mmz4281/2324/I1.csv",
    "https://www.football-data.co.uk/mmz4281/2324/F1.csv", "https://www.football-data.co.uk/mmz4281/2324/B1.csv",
    # 2022/2023 Season
    "https://www.football-data.co.uk/mmz4281/2223/E0.csv", "https://www.football-data.co.uk/mmz4281/2223/SP1.csv"
]

def find_historical_outcomes(h, d, a, db):
    # This hunts for the EXACT numbers you entered
    # We use a tiny tolerance (0.02) because bookies often round 1.33 to 1.34
    exact_matches = db[
        (db['B365H'].between(h-0.02, h+0.02)) & 
        (db['B365D'].between(d-0.02, d+0.02)) & 
        (db['B365A'].between(a-0.02, a+0.02))
    ]
    
    if exact_matches.empty:
        return None

    # Calculate what happened in those past games
    total = len(exact_matches)
    h_wins = len(exact_matches[exact_matches['FTR'] == 'H'])
    draws = len(exact_matches[exact_matches['FTR'] == 'D'])
    a_wins = len(exact_matches[exact_matches['FTR'] == 'A'])

    return {
        "odds": f"{h} - {d} - {a}",
        "count": total,
        "percentage": {
            "Home": round((h_wins/total)*100),
            "Draw": round((draws/total)*100),
            "Away": round((a_wins/total)*100)
        },
        # This shows you the actual names and results of the past games!
        "past_games": [f"{r['HomeTeam']} vs {r['AwayTeam']} ({r['FTR']})" for _, r in exact_matches.tail(5).iterrows()]
    }

# Load all historical data
all_dfs = []
for url in SOURCES:
    try:
        df = pd.read_csv(url)
        all_dfs.append(df[['HomeTeam', 'AwayTeam', 'FTR', 'B365H', 'B365D', 'B365A']])
    except: continue

master_db = pd.concat(all_dfs, ignore_index=True)

# Process your input file
results = []
with open('target_link.txt', 'r') as f:
    for line in f:
        try:
            o = [float(x.strip()) for x in line.split(',')]
            analysis = find_historical_outcomes(o[0], o[1], o[2], master_db)
            if analysis: results.append(analysis)
        except: continue

with open('results.json', 'w') as f:
    json.dump(results, f)
