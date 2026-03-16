import pandas as pd
import json

DATA_URL = "https://www.football-data.co.uk/mmz4281/2324/E0.csv"

def get_analysis(h, d, a, df):
    # Search logic
    match_filter = (df['B365H'].between(h-0.1, h+0.1)) & (df['B365D'].between(d-0.1, d+0.1))
    matched = df[match_filter].tail(10)
    
    if matched.empty: return None
    
    total = len(matched)
    return {
        "odds": f"{h}/{d}/{a}",
        "stats": {
            "H": round((len(matched[matched['FTR']=='H'])/total)*100),
            "D": round((len(matched[matched['FTR']=='D'])/total)*100),
            "A": round((len(matched[matched['FTR']=='A'])/total)*100)
        },
        "recent": matched.tail(2)['FTR'].tolist(),
        "history": [f"{r['HomeTeam']} vs {r['AwayTeam']} ({r['FTR']})" for _, r in matched.iterrows()]
    }

# Read multiple lines from your text file
df_hist = pd.read_csv(DATA_URL)
all_results = []

with open('target_link.txt', 'r') as f:
    for line in f:
        if ',' in line:
            h, d, a = map(float, line.split(','))
            res = get_analysis(h, d, a, df_hist)
            if res: all_results.append(res)

with open('results.json', 'w') as f:
    json.dump(all_results, f)
