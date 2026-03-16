import pandas as pd
import json

# Using the English Premier League database as an example
DATA_URL = "https://www.football-data.co.uk/mmz4281/2324/E0.csv"

def analyze_odds(h_odds, d_odds, a_odds):
    df = pd.read_csv(DATA_URL)
    
    # Filter matches with similar odds (0.1 range)
    match_filter = (
        (df['B365H'].between(h_odds - 0.1, h_odds + 0.1)) &
        (df['B365D'].between(d_odds - 0.1, d_odds + 0.1))
    )
    
    matched_games = df[match_filter].tail(10)
    
    if matched_games.empty:
        analysis = {"error": "No historical matches found for these odds."}
    else:
        # Calculate Percentages
        total = len(matched_games)
        h_wins = len(matched_games[matched_games['FTR'] == 'H'])
        draws = len(matched_games[matched_games['FTR'] == 'D'])
        a_wins = len(matched_games[matched_games['FTR'] == 'A'])

        # Get the 2 most recent outcomes
        recent = matched_games.tail(2)['FTR'].tolist()

        analysis = {
            "stats": {
                "home_win_pct": round((h_wins / total) * 100),
                "draw_pct": round((draws / total) * 100),
                "away_win_pct": round((a_wins / total) * 100)
            },
            "recent_outcomes": recent,
            "history": []
        }

        for _, row in matched_games.iterrows():
            analysis["history"].append({
                "match": f"{row['HomeTeam']} vs {row['AwayTeam']}",
                "result": row['FTR'],
                "odds": f"{row['B365H']}/{row['B365D']}/{row['B365A']}"
            })
    
    with open('results.json', 'w') as f:
        json.dump(analysis, f)

# Update these numbers to test a new game!
analyze_odds(2.10, 3.20, 3.60)
