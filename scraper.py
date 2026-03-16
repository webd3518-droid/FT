import pandas as pd
import json

# We now check 5 major leagues to find more historical matches
LEAGUES = [
    "https://www.football-data.co.uk/mmz4281/2324/E0.csv", # England
    "https://www.football-data.co.uk/mmz4281/2324/SP1.csv", # Spain
    "https://www.football-data.co.uk/mmz4281/2324/D1.csv", # Germany
    "https://www.football-data.co.uk/mmz4281/2324/I1.csv", # Italy
    "https://www.football-data.co.uk/mmz4281/2324/F1.csv"  # France
]

def analyze_game(h_odds, d_odds, a_odds, df):
    # Search with a slightly wider margin (0.15) to ensure we find games
    match_filter = (
        (df['B365H'].between(h_odds - 0.15, h_odds + 0.15)) &
        (df['B365D'].between(d_odds - 0.15, d_odds + 0.15))
    )
    matched_games = df[match_filter].tail(10)
    
    if matched_games.empty:
        return None

    total = len(matched_games)
    h_wins = len(matched_games[matched_games['FTR'] == 'H'])
    draws = len(matched_games[matched_games['FTR'] == 'D'])
    a_wins = len(matched_games[matched_games['FTR'] == 'A'])

    return {
        "target_odds": f"{h_odds}/{d_odds}/{a_odds}",
        "stats": {"home": round((h_wins/total)*100), "draw": round((draws/total)*100), "away": round((a_wins/total)*100)},
        "recent": matched_games.tail(2)['FTR'].tolist(),
        "history": [f"{r['HomeTeam']} v {r['AwayTeam']} ({r['FTR']})" for _, r in matched_games.iterrows()]
    }

# Combine all leagues into one big database
all_dfs = []
for url in LEAGUES:
    try:
        all_dfs.append(pd.read_csv(url))
    except:
        continue

df_historical = pd.concat(all_dfs, ignore_index=True)

all_results = []
with open('target_link.txt', 'r') as f:
    for line in f:
        try:
            line = line.strip()
            if not line: continue
            odds = [float(x.strip()) for x in line.split(',')]
            res = analyze_game(odds[0], odds[1], odds[2], df_historical)
            if res: 
                all_results.append(res)
        except Exception as e:
            print(f"Skipping line due to error: {line}")

with open('results.json', 'w') as f:
    json.dump(all_results, f)
