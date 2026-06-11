import os
import requests
from datetime import datetime

# Utilise ton secret MPP_REFRESH_TOKEN comme avant
REFRESH_TOKEN = os.environ.get("MPP_REFRESH_TOKEN")

# Les URLs réelles extraites de ton navigateur
TOKEN_URL = "https://connect.ligue1.fr/oauth/token"
# On cible l'API principale utilisée par mpp.football
API_BASE_URL = "https://api.mpp.football" 
LEAGUES_URL = f"{API_BASE_URL}/leagues"

def main():
    if not REFRESH_TOKEN:
        print("Erreur : Refresh Token manquant.")
        return

    session = requests.Session()
    
    # Étape 1 : Récupérer le token valide avec ton Refresh Token
    print("Étape 1 : Authentification via Ligue 1...")
    payload = {
        "client_id": "grX5jWGWWQ4Uq91oe7KPNDZ96FS3jr0X",
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN
    }
    
    res_token = session.post(TOKEN_URL, json=payload)
    if res_token.status_code != 200:
        print(f"Erreur Auth : {res_token.status_code} - {res_token.text}")
        return
        
    token = res_token.json().get("id_token")
    session.headers.update({"Authorization": f"Bearer {token}"})
    print("Authentification réussie !")

    # Étape 2 : Récupérer la liste des ligues
    print("Récupération des ligues...")
    # On ajoute un header pour se faire passer pour le site officiel
    headers = {"Origin": "https://mpp.football", "Referer": "https://mpp.football/"}
    leagues_res = session.get(LEAGUES_URL, headers=headers)
    
    if leagues_res.status_code != 200:
        print(f"Erreur Ligues : {leagues_res.status_code} - {leagues_res.text}")
        return

    leagues_data = leagues_res.json().get("leagues", [])
    dashboard_data = []

    # Étape 3 : Scanner le classement
    for lg in leagues_data:
        l_id = lg.get("id")
        # L'URL du ranking est souvent liée à l'ID de la ligue
        rank_res = session.get(f"{API_BASE_URL}/leagues/{l_id}/ranking", headers=headers)
        if rank_res.status_code == 200:
            ranking = rank_res.json().get("ranking", [])
            for pos, user in enumerate(ranking, start=1):
                if user.get("is_me"):
                    dashboard_data.append({
                        "name": lg.get("name"),
                        "rank": pos,
                        "total": len(ranking),
                        "pts": user.get("points", 0)
                    })
                    break

    dashboard_data.sort(key=lambda x: x["rank"])
    generate_html(dashboard_data)

def generate_html(data):
    # (Le reste du code HTML reste identique)
    # Assure-toi de garder la fonction generate_html comme dans le message précédent
    pass

if __name__ == "__main__":
    main()
