import os
import requests
from datetime import datetime

EMAIL = os.environ.get("MPP_EMAIL")
PASSWORD = os.environ.get("MPP_PASSWORD")

API_BASE_URL = "https://api.mpg.football"
LOGIN_URL = f"{API_BASE_URL}/users/sign_in"
LEAGUES_URL = f"{API_BASE_URL}/leagues"

def main():
    if not EMAIL or not PASSWORD:
        print("Erreur : Identifiants manquants.")
        return

    session = requests.Session()
    
    # 1. Connexion
    response = session.post(LOGIN_URL, json={"email": EMAIL, "password": PASSWORD}, headers={"Content-Type": "application/json"})
    if response.status_code != 200:
        print("Échec de connexion.")
        return
        
    token = response.headers.get("Authorization") or response.json().get("token")
    session.headers.update({"Authorization": token})

    # 2. Récupération des ligues
    leagues_response = session.get(LEAGUES_URL) 
    if leagues_response.status_code != 200:
        return
        
    leagues_data = leagues_response.json().get("leagues", [])
    dashboard_data = []

    # 3. Extraction des classements
    for lg in leagues_data:
        rank_res = session.get(f"{API_BASE_URL}/leagues/{lg.get('id')}/ranking")
        if rank_res.status_code == 200:
            ranking_list = rank_res.json().get("ranking", [])
            for position, user in enumerate(ranking_list, start=1):
                if user.get("email") == EMAIL or user.get("is_me") is True:
                    dashboard_data.append({
                        "name": lg.get("name"),
                        "rank": position,
                        "total_players": len(ranking_list),
                        "points": user.get("points", 0)
                    })
                    break

    dashboard_data.sort(key=lambda x: x["rank"])
    generate_html(dashboard_data)

def generate_html(data):
    now = datetime.now().strftime("%d/%m/%Y à %H:%M")
    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard MPP</title>
    <style>
        body {{ font-family: sans-serif; background: #f4f7f6; padding: 20px; }}
        table {{ width: 100%; border-collapse: collapse; background: white; }}
        th, td {{ padding: 12px; border-bottom: 1px solid #eee; text-align: left; }}
        th {{ background: #11b374; color: white; }}
        .badge {{ background: #11b374; color: white; padding: 4px 8px; border-radius: 12px; font-weight: bold; }}
        .top-3 {{ background: #ffd700; color: #333; }}
    </style>
</head>
<body>
    <div style="max-width: 800px; margin: auto;">
        <h1 style="color: #11b374; text-align: center;">🏆 Mes Ligues MPP</h1>
        <p style="text-align: center; color: #666; font-size: 12px;">MAJ : {now}</p>
        <table>
            <tr><th>Ligue</th><th>Rang</th><th>Points</th></tr>"""
            
    for r in data:
        badge = "badge top-3" if r['rank'] <= 3 else "badge"
        html += f"<tr><td><b>{r['name']}</b></td><td><span class='{badge}'>{r['rank']} / {r['total_players']}</span></td><td>{r['points']} pts</td></tr>"
        
    html += "</table></div></body></html>"
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    main()