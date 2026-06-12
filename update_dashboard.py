import os
import requests
from datetime import datetime

REFRESH_TOKEN = os.environ.get("MPP_REFRESH_TOKEN")
TOKEN_URL = "https://connect.ligue1.fr/oauth/token"
API_BASE_URL = "https://api.mpp.football"

def main():
    if not REFRESH_TOKEN:
        print("Erreur : Refresh Token manquant.")
        return

    session = requests.Session()
    
    print("Étape 1 : Authentification...")
    payload = {
        "client_id": "grX5jWGWWQ4Uq91oe7KPNDZ96FS3jr0X",
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN
    }
    
    res_token = session.post(TOKEN_URL, json=payload)
    if res_token.status_code != 200:
        print(f"Erreur d'authentification : {res_token.status_code}")
        return
        
    token = res_token.json().get("access_token")

    session.headers.update({
        "Authorization": f"Bearer {token}",
        "Origin": "https://mpp.football",
        "Referer": "https://mpp.football/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json"
    })
    
    print("Étape 2 : Récupération de tes ligues...")
    res_contests = session.get(f"{API_BASE_URL}/user-contests")
    
    if res_contests.status_code != 200:
        print("Impossible de charger les ligues.")
        return

    contests = res_contests.json().get("contestsCards", [])
    dashboard_data = []

    print(f"Extraction des scores en cours...")
    for c in contests:
        c_id = c.get("contestId")
        
        if not c_id:
            continue
            
        rank_url = f"{API_BASE_URL}/challenge/{c_id}"
        rank_res = session.get(rank_url)
        
        if rank_res.status_code == 200:
            challenge_data = rank_res.json()
            
            c_name = challenge_data.get("name", "Ligue Inconnue")
            
            # --- 1. Ignorer la ligue "GLS Tournefeuille" ---
            if c_name == "GLS Tournefeuille":
                continue

            user_rank = challenge_data.get("currentUserRank")
            total_players = challenge_data.get("usersQuantity", "?")
            
            # --- 2. Chasse aux points ---
            # On tente toutes les clés possibles utilisées par l'API
            user_points = (
                challenge_data.get("currentUserScore") or 
                challenge_data.get("currentUserPoints") or 
                challenge_data.get("score") or 
                challenge_data.get("points")
            )
            
            # Si toujours vide, on fouille dans userDetails si ça existe
            if user_points is None and isinstance(challenge_data.get("userDetails"), dict):
                user_points = challenge_data.get("userDetails").get("points") or challenge_data.get("userDetails").get("score")
                
            # Si vraiment rien n'est trouvé
            if user_points is None:
                user_points = "-"
            
            if user_rank is not None:
                dashboard_data.append({
                    "name": c_name,
                    "rank": user_rank,
                    "total": total_players,
                    "pts": user_points
                })

    # --- 3. Tri sur-mesure ---
    # x["name"] != "GLS Tournefeuille CDM2026" renvoie False (0) pour la ligue favorite, et True (1) pour les autres.
    # Ainsi, la ligue favorite se retrouve tout en haut (position 0), et le reste est trié par le rang (x["rank"]).
    dashboard_data.sort(key=lambda x: (x["name"] != "GLS Tournefeuille CDM2026", x["rank"]))
    
    generate_html(dashboard_data)

def generate_html(data):
    now = datetime.now().strftime("%d/%m/%Y à %H:%M")
    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard MPP - Mes Pronos</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f4f7f6; padding: 20px; margin: 0; }}
        table {{ width: 100%; max-width: 800px; margin: auto; border-collapse: collapse; background: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden; }}
        th, td {{ padding: 15px; border-bottom: 1px solid #eee; text-align: left; }}
        th {{ background: #11b374; color: white; text-transform: uppercase; font-size: 14px; letter-spacing: 0.5px; }}
        tr:hover {{ background-color: #f9f9f9; }}
        .badge {{ background: #11b374; color: white; padding: 5px 10px; border-radius: 20px; font-weight: bold; font-size: 14px; }}
        .top-3 {{ background: #ffd700; color: #333; }}
        .favorite {{ background-color: #e8f7f1; }} /* Légère couleur de fond pour la ligue favorite */
        .pts {{ font-weight: bold; color: #444; }}
    </style>
</head>
<body>
    <div style="max-width: 800px; margin: auto;">
        <h1 style="color: #11b374; text-align: center;">🏆 Mon Suivi MPP - Coupe du Monde 2026</h1>
        <p style="text-align: center; color: #666; font-size: 13px; margin-bottom: 30px;">Dernière mise à jour : {now}</p>
        <table>
            <tr><th>Ligue</th><th>Rang</th><th>Points</th></tr>"""
            
    for r in data:
        badge = "badge top-3" if r['rank'] <= 3 else "badge"
        row_class = "favorite" if r['name'] == "GLS Tournefeuille CDM2026" else ""
        
        html += f"<tr class='{row_class}'><td><b>{r['name']}</b></td><td><span class='{badge}'>{r['rank']} / {r['total']}</span></td><td class='pts'>{r['pts']}</td></tr>"
        
    html += "</table></div></body></html>"
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Fichier index.html généré avec succès ! ({len(data)} ligues intégrées au tableau)")

if __name__ == "__main__":
    main()
