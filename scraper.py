import pandas as pd
import json

# Links to the last 3 years of data for all major European leagues
# This creates a massive pool of historical matches
SOURCES = [
    # 2025/2026 (Current)
    "https://www.football-data.co.uk/mmz4281/2526/E0.csv", "https://www.football-data.co.uk/mmz4281/2526/SP1.csv",
    # 2024/2025
    "https://www.football-data.co.uk/mmz4281/2425/E0.csv", "https://www.football-data.co.uk/mmz4281/2425/SP1.csv",
    "https://www.football-data.co.uk/mmz4281/2425/D1.csv", "https://www.football-data.co.uk/mmz4281/2425/I1.csv",
    # 2023/2024
    "https://www.football-data.co.uk/mmz4281/2324/E0.csv", "https://www.football-data.co.uk/mmz4281/2324/SP1.csv",
    "https://www.football-data.co.uk/mmz4281/2324/D1.csv", "https://www.football-data.co.uk/mmz4281/2324/I1.csv",
    "https://www.football-data.co.uk/mmz4281/2324/F1.csv", "https://www.football-data.co.uk/mmz4281/2324/B1.csv",
    "https://www.football-data.co.uk/mmz4281/2324/N1.csv", "https://www.football-data.co.uk/mmz4281/2324/P1.csv"
]

def analyze_game(h, d, a, big_df):
    # Flexible margin (0.20) helps find matches for rare odds
    margin = 0.20
    matches = big_df[
        (big_df['B365H'].between(h - margin, h + margin)) &
        (big_df['B365D'].between(d - margin, d + margin))
    ].tail(10) # Get the 10 most recent matches with these odds
    
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

# 1. Download and combine all historical files
all_data = []
for url in SOURCES:
    try:
        df = pd.read_csv(url)
        # We only need the team names, the result (FTR), and the Bet365 odds
        all_data.append(df[['HomeTeam', 'AwayTeam', 'FTR', 'B365H', 'B365D', 'B365A']])
    except:
        continue # Skip files that aren't ready yet

mega_df = pd.concat(all_data, ignore_index=True)

# 2. Read your input odds from target_link.txt
results = []
try:
    with open('target_link.txt', 'r') as f:
        for line in f:
            line = line.strip()
            if not line or ',' not in line: continue
            
            o = [float(x.strip()) for x in line.split(',')]
            analysis = analyze_game(o[0], o[1], o[2], mega_df)
            if analysis: results.append(analysis)
except FileNotFoundError:
    print("Error: target_link.txt not found.")

# 3. Save the findings
with open('results.json', 'w') as f:
    json.dump(results, f)
