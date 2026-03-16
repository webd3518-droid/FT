import pandas as pd
import json

# Using a 5-year database to find as many 'Exact' matches as possible
SOURCES = [
    "https://www.football-data.co.uk/mmz4281/2425/E0.csv", "https://www.football-data.co.uk/mmz4281/2425/SP1.csv",
    "https://www.football-data.co.uk/mmz4281/2425/D1.csv", "https://www.football-data.co.uk/mmz4281/2425/I1.csv",
    "https://www.football-data.co.uk/mmz4281/2324/E0.csv", "https://www.football-data.co.uk/mmz4281/2324/SP1.csv",
    "https://www.football-data.co.uk/mmz4281/2223/E0.csv", "https://www.football-data.co.uk/mmz4281/2223/SP1.csv",
    "https://www.football-data.co.uk/mmz4281/2122/E0.csv", "https://www.football-data.co.uk/mmz4281/2122/SP1.csv"
]

def find_historical_outcomes(h, d, a, db):
    # STEP 1: Try to find the EXACT match (100% identical numbers)
    matches = db[(db['B365H'] == h) & (db['B365D'] == d) & (db['B365A'] == a)]
    
    # STEP 2: If no exact match, search for the closest Home/Draw numbers
    if matches.empty:
        # Search for games where Home and Draw odds are within 0.10 of your entry
        matches = db[
            (db['B365H'].between(h - 0.10, h + 0.10)) & 
            (db['B365D'].between(d - 0.10, d + 0.10))
        ].tail(15)

    if matches.empty: return None

    total = len(matches)
    h_wins = len(matches[matches['FTR'] == 'H'])
    draws = len(matches[matches['FTR'] == 'D'])
    a_wins = len(matches[matches['FTR'] == 'A'])

    return {
        "odds": f"{h} | {d} | {a}",
        "count": total,
        "percentage": {
            "Home": round((h_wins/total)*100),
            "Draw": round((draws/total)*100),
            "Away": round((a_wins/total)*100)
        },
        # This gives you the raw outcome of the games that had these numbers
        "past_games": [f"Outcome: {r['FTR']} ({r['HomeTeam']} v {r['AwayTeam']})" for _, r in matches.iterrows()]
    }

# Combine all history into one 'Odds Library'
all_dfs = []
for url in SOURCES:
    try:
        df = pd.read_csv(url)
        all_dfs.append(df[['HomeTeam', 'AwayTeam', 'FTR', 'B365H', 'B365D', 'B365A']])
    except: continue

master_db = pd.concat(all_dfs, ignore_index=True)

# Scan target_link.txt
results = []
try:
    with open('target_link.txt', 'r') as f:
        for line in f:
            if ',' not in line: continue
            o = [float(x.strip()) for x in line.split(',')]
            res = find_historical_outcomes(o[0], o[1], o[2], master_db)
            if res: results.append(res)
except: pass

with open('results.json', 'w') as f:
    json.dump(results, f)
