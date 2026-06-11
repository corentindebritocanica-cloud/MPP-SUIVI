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
        print("Erreur : Identifiants manquants (Secrets non trouvés).")
        return

    session = requests.Session()
    
    # On ajoute des "Headers" pour faire croire à MPP que l'on est un vrai navigateur Chrome
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://mpp.football",
        "Referer": "https://mpp.football/"
    }
    
    print("Tentative de connexion à MPP...")
    
    # 1. Connexion
    response = session.post(LOGIN_URL, json={"email": EMAIL, "password": PASSWORD}, headers=headers)
    
    if response.status_code != 200:
        print(f"Échec de connexion. Code HTTP : {response.status_code}")
        print(f"Message de l'API : {response.text}")
        return
        
    print("Connexion réussie ! Récupération du Token...")
    token = response.headers.get("Authorization") or response.json().get("token")
    session.headers.update({"Authorization": token})

    # 2. Récupération des ligues
    print("Récupération des ligues...")
    leagues_response = session.get(LEAGUES_URL) 
    if leagues_response.status_code != 200:
        print(f"Impossible de récupérer les ligues. Code: {leagues_response.status_code}")
        return
        
    leagues_data = leagues_response.json().get("leagues", [])
    dashboard_data = []

    # 3. Extraction des classements
    print(f"{len(leagues_data)} ligues trouvées. Scan en cours...")
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
        body {{ font-family: sans-serif; background: #f4f7f6; padding: 20px; margin: 0; }}
        table {{ width: 100%; border-collapse: collapse; background: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden; }}
        th, td {{ padding: 12px; border-bottom: 1px solid #eee; text-align: left; }}
        th {{ background: #11b374; color: white; }}
        .badge {{ background: #11b374; color: white; padding: 4px 8px; border-radius: 12px; font-weight: bold; }}
        .top-3 {{ background: #ffd700; color: #333; }}
    </style>
</head>
<body>
    <div style="max-width: 800px; margin: auto;">
        <h1 style="color: #11b374; text-align: center;">🏆 Mes Ligues MPP 2026</h1>
        <p style="text-align: center; color: #666; font-size: 12px;">Dernière mise à jour : {now}</p>
        <table>
            <tr><th>Ligue</th><th>Rang</th><th>Points</th></tr>"""
            
    for r in data:
        badge = "badge top-3" if r['rank'] <= 3 else "badge"
        html += f"<tr><td><b>{r['name']}</b></td><td><span class='{badge}'>{r['rank']} / {r['total_players']}</span></td><td>{r['points']} pts</td></tr>"
        
    html += "</table></div></body></html>"
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Fichier index.html généré avec succès !")

if __name__ == "__main__":
    main()
