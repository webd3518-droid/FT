import pandas as pd
import json

# For this "Free" version, we use a historical CSV database
# You can change this URL to different leagues (E0 = EPL, SP1 = La Liga, etc.)
DATA_URL = "https://www.football-data.co.uk/mmz4281/2324/E0.csv"

def analyze_odds(h_odds, d_odds, a_odds):
    df = pd.read_csv(DATA_URL)
    
    # Find matches where odds are close (within 0.10 range)
    match_filter = (
        (df['B365H'].between(h_odds - 0.1, h_odds + 0.1)) &
        (df['B365D'].between(d_odds - 0.1, d_odds + 0.1))
    )
    
    results = df[match_filter].tail(10) # Get last 10
    
    output = []
    for _, row in results.iterrows():
        output.append({
            "match": f"{row['HomeTeam']} vs {row['AwayTeam']}",
            "result": row['FTR'], # H = Home Win, D = Draw, A = Away Win
            "odds": f"{row['B365H']}/{row['B365D']}/{row['B365A']}"
        })
    
    with open('results.json', 'w') as f:
        json.dump(output, f)

# For now, we manually set these. In Step 5, we automate this.
analyze_odds(1.85, 3.50, 4.20)
