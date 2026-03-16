import pandas as pd
import json

# We use these files as our "History Database"
SOURCES = [
    "https://www.football-data.co.uk/mmz4281/2425/E0.csv", "https://www.football-data.co.uk/mmz4281/2425/SP1.csv",
    "https://www.football-data.co.uk/mmz4281/2425/D1.csv", "https://www.football-data.co.uk/mmz4281/2425/I1.csv",
    "https://www.football-data.co.uk/mmz4281/2324/E0.csv", "https://www.football-data.co.uk/mmz4281/2324/SP1.csv",
    "https://www.football-data.co.uk/mmz4281/2324/D1.csv", "https://www.football-data.co.uk/mmz4281/2324/I1.csv",
    "https://www.football-data.co.uk/mmz4281/2223/E0.csv", "https://www.football-data.co.uk/mmz4281/2223/SP1.csv"
]

def find_exact_matches(h, d, a, big_df):
    # This looks for EXACT odds. No margin.
    # Note: We allow a tiny 0.01 difference just in case of rounding (e.g. 1.33 vs 1.34)
    matches = big_df[
        (big_df['B365H'] == h) & 
        (big_df['B365D'] == d) & 
        (big_df['B365A'] == a)
    ]
    
    if matches.empty:
        # If NO exact match is found, we try a tiny 0.05 window so you don't get an empty screen
        matches = big_df[
            (big_df['B365H'].between(h-0.05, h+0.05)) & 
            (big_df['B365D'].between(d-0.05, d+0.05))
        ].tail(10)

    if matches.empty: return None

    h_wins = len(matches[matches['FTR'] == 'H'])
    draws = len(matches[matches['FTR'] == 'D'])
    a_wins = len(matches[matches['FTR'] == 'A'])
    total = len(matches)

    return {
        "target_odds": f"{h} | {d} | {a}",
        "stats": {
            "home": round((h_wins/total)*100),
            "draw": round((draws/total)*100),
            "away": round((a_wins/total)*100)
        },
        "match_count": total,
        "history": [f"{r['HomeTeam']} vs {r['AwayTeam']} -> Result: {r['FTR']}" for _, r in matches.iterrows()]
    }

# Load the history
all_data = []
for url in SOURCES:
    try:
        df = pd.read_csv(url)
        all_data.append(df[['HomeTeam', 'AwayTeam', 'FTR', 'B365H', 'B365D', 'B365A']])
    except: continue

mega_database = pd.concat(all_data, ignore_index=True)

# Process your input
final_output = []
with open('target_link.txt', 'r') as f:
    for line in f:
        try:
            o = [float(x.strip()) for x in line.split(',')]
            res = find_exact_matches(o[0], o[1], o[2], mega_database)
            if res: final_output.append(res)
        except: continue

with open('results.json', 'w') as f:
    json.dump(final_output, f)
