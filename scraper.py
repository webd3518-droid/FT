<!DOCTYPE html>
<html>
<head>
    <style>
        .game-card { border: 2px solid #333; margin: 20px 0; padding: 15px; border-radius: 10px; font-family: sans-serif; }
        .win { color: green; font-weight: bold; }
        .trend { background: #eee; padding: 5px; }
    </style>
</head>
<body>
    <h1>Multi-Game Analysis</h1>
    <div id="container"></div>

    <script>
        fetch('results.json')
            .then(res => res.json())
            .then(data => {
                const container = document.getElementById('container');
                data.forEach((game, index) => {
                    container.innerHTML += `
                        <div class="game-card">
                            <h2>Game ${index + 1} (Odds: ${game.odds})</h2>
                            <p class="win">Likelihood: Home ${game.stats.H}% | Draw ${game.stats.D}% | Away ${game.stats.A}%</p>
                            <p class="trend">Recent 2 Outcomes: ${game.recent.join(" , ")}</p>
                            <details>
                                <summary>View 10 Match History</summary>
                                <ul>${game.history.map(h => `<li>${h}</li>`).join("")}</ul>
                            </details>
                        </div>
                    `;
                });
            });
    </script>
</body>
</html>
