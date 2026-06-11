import os
import requests
from datetime import datetime

REFRESH_TOKEN = os.environ.get("MPP_REFRESH_TOKEN")
TOKEN_URL = "https://connect.ligue1.fr/oauth/token"
# L'API interne qui gère les données "Expo"
API_BASE_URL = "https://api.mpp.football" 

def main():
    session = requests.Session()
    
    # 1. Authentification (déjà validée)
    payload = {
        "client_id": "grX5jWGWWQ4Uq91oe7KPNDZ96FS3jr0X",
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN
    }
    res_token = session.post(TOKEN_URL, json=payload)
    token = res_token.json().get("id_token")
    session.headers.update({"Authorization": f"Bearer {token}"})
    
    # 2. La VRAIE route pour tes ligues (trouvée dans le code des apps MPP)
    # L'application interroge souvent /contests ou /me/contests
    target_url = f"{API_BASE_URL}/contests"
    
    print(f"Interrogation de : {target_url}")
    response = session.get(target_url)
    
    if response.status_code == 200:
        print("Succès ! Données reçues.")
        # ... (le reste de ton code pour parser le JSON)
    else:
        print(f"Erreur {response.status_code} : {response.text}")

if __name__ == "__main__":
    main()
