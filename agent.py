import os
import requests

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        response = requests.post(url, json=payload)
        print(f"Statut Telegram : {response.status_code}")
    except Exception as e:
        print(f"Erreur d'envoi Telegram : {e}")

if __name__ == "__main__":
    print("Génération du rapport d'investissement et des liens...")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    
    prompt = (
        "Agis en tant que chasseur immobilier expert. "
        "Fournis une analyse stratégique pour l'achat d'un immeuble de rapport dans le Sud-Ouest "
        "(Gironde, Landes, Lot-et-Garonne, Dordogne, etc.) avec ces critères stricts : "
        "1. Budget maximum : 300 000 €. "
        "2. Immeuble résidentiel uniquement (exclure tout local commercial). "
        "3. Intègre le fait que les travaux de rénovation sont à coût nul pour viser un cash-flow positif immédiat sur un crédit de 25 ans. "
        "Donne 2 ou 3 communes cibles très porteuses actuellement. "
        "Pour chaque commune, fournis un lien URL direct et fonctionnel vers une recherche pré-filtrée sur les grands portails immobiliers (comme LeBonCoin ou SeLoger) "
        "afin que je puisse voir les annonces en ligne immédiatement."
    )
    
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        result = response.json()
        analysis = result["candidates"][0]["content"]["parts"][0]["text"]
        message_final = f"🏗️ *Chasse Immo - Opportunités & Liens*\n\n{analysis}"
        send_telegram(message_final)
        print("Rapport envoyé avec succès !")
    else:
        error_msg = f"Erreur API Gemini ({response.status_code}) : {response.text}"
        print(error_msg)
        send_telegram(error_msg)
