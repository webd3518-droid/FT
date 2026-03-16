import pandas as pd
import json

# Expanding the database to multiple seasons and multiple leagues
# E0 = England, SP1 = Spain, D1 = Germany, I1 = Italy, F1 = France
SEASON_FILES = [
    # 2024/2025 (Current)
    "https://www.football-data.co.uk/mmz4281/2425/E0.csv",
    "https://www.football-data.co.uk/mmz4281/2425/SP1.csv",
    # 2023/2024 (Last Season)
    "https://www.football-data.co.uk/mmz4281/2324/E0.csv",
    "https://www.football-data.co.uk/mmz4281/2324/SP1.csv",
    "https://www.football-data.co.uk/mmz4281/2324/D1.csv",
    "https://www.football-data.co.uk/mmz4281/2324/I1.csv",
    # 2022/2023 (Two Seasons Ago)
    "https://www.football-data.co.uk/mmz4281/2223/E0.csv",
    "https://www.football-data.co.uk/mmz4281/2223/SP1.csv"
]

def analyze_game(h, d, a, big_df):
    # Margin of 0.20 allows for more historical matches to be found
    margin = 0.20
    matches = big_df[
        (big_df['B365H'].between(h - margin, h + margin)) &
        (big_df['B365D'].between(d - margin, d + margin))
    ].tail(10)
    
    if matches.empty: return None
    
    # Calculate stats
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

# 1. Download and combine all files into one "Mega Database"
all_data = []
for url in SEASON_FILES:
    try:
        df = pd.read_csv(url)
        # Only keep columns we need to save memory
        all_data.append(df[['HomeTeam', 'AwayTeam', 'FTR', 'B365H', 'B365D', 'B365A']])
    except:
        continue

mega_df = pd.concat(all_data, ignore_index=True)

# 2. Process your target_link.txt
results = []
with open('target_link.txt', 'r') as f:
    for line in f:
        try:
            o = [float(x.strip()) for x in line.split(',')]
            analysis = analyze_game(o[0], o[1], o[2], mega_df)
            if analysis: results.append(analysis)
        except: continue

# 3. Save
with open('results.json', 'w') as f:
    json.dump(results, f)
