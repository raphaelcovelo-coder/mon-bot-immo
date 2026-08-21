import os
import time
import requests

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def ask_gemini(prompt, retries=3, delay=5):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "tools": [{"google_search": {}}]
    }
    
    for attempt in range(retries):
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            try:
                result_json = response.json()
                return result_json["candidates"][0]["content"]["parts"][0]["text"]
            except Exception as e:
                return f"Erreur de lecture : {e}"
        elif response.status_code == 503:
            print(f"Surcharge Google (503), tentative {attempt + 1}/{retries}...")
            time.sleep(delay)
        else:
            return f"Erreur API Gemini ({response.status_code}) : {response.text}"
            
    return "Erreur : Modèle indisponible après plusieurs tentatives."

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    response = requests.post(url, json=payload)
    print(f"Statut Telegram : {response.status_code}")

if __name__ == "__main__":
    print("Recherche des meilleures opportunités en ligne...")
    
    prompt = (
        "Agis en tant que chasseur immobilier expert. "
        "Recherche sur le web les **3 meilleures opportunités actuelles d'immeubles de rapport** "
        "à vendre dans le Sud-Ouest (Gironde, Landes, Lot-et-Garonne, Dordogne, etc.), "
        "qu'elles soient fraîchement publiées ou déjà en ligne depuis un moment sur les portails. "
        "Critères stricts : "
        "1. Budget maximum de 300 000 €. "
        "2. Immeuble résidentiel uniquement (exclure tout local commercial). "
        "3. Fournis obligatoirement les liens URL directs des annonces, la ville, le prix affiché, "
        "et une analyse rapide du potentiel (en intégrant le fait que les travaux de rénovation sont à coût nul "
        "pour viser un cash-flow positif sur 25 ans)."
    )
    
    analysis = ask_gemini(prompt)
    
    message_final = f"🏗️ *Top 3 Immeubles - Actuellement en Ligne*\n\n{analysis}"
    send_telegram(message_final)
    print("Rapport envoyé !")
