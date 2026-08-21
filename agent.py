import os
import requests

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}
    response = requests.post(url, json=payload)
    print(f"Statut Telegram : {response.status_code}")

if __name__ == "__main__":
    print("Génération du rapport 'Immeubles avec Travaux'...")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    
    prompt = (
        "Agis en tant qu'expert en investissement immobilier. "
        "Fournis une analyse stratégique pour l'achat d'un **immeuble de rapport à rénover** "
        "(gros travaux, plateaux à aménager, rafraîchissement lourd) dans le Sud-Ouest (Gironde, Landes, Lot-et-Garonne, Dordogne, etc.). "
        "Rappel stratégique : les travaux sont à coût nul pour l'investisseur, il faut donc chercher des passoires thermiques ou des biens à fort potentiel de transformation pour maximiser la plus-value. "
        "Critères stricts : "
        "1. Budget maximum : 300 000 € (achat + structure). "
        "2. Immeuble résidentiel uniquement (exclure tout local commercial). "
        "3. Orientation : Biens nécessitant des travaux (exclure absolument le clé en main). "
        "Donne 2 ou 3 communes cibles très porteuses pour ce profil et inclus des liens de recherche clairs vers LeBonCoin."
    )
    
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        try:
            result = response.json()
            analysis = result["candidates"][0]["content"]["parts"][0]["text"]
            message = f"🏗️ *Chasse Immo - Spécial Immeubles à Rénover*\n\n{analysis}"
            send_telegram(message)
        except Exception as e:
            send_telegram(f"Erreur de traitement : {e}")
    else:
        send_telegram(f"Erreur API ({response.status_code}) : {response.text}")
