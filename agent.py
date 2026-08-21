import os
import requests

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def ask_gemini(prompt):
    # On remet le bon modèle et l'URL v1beta qui fonctionnent avec ta clé
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    else:
        return f"Erreur API ({response.status_code}) : {response.text}"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, json=payload)

if __name__ == "__main__":
    prompt = (
        "Donne-moi une analyse stratégique des immeubles de rapport dans le Sud-Ouest. "
        "Quelles sont les villes où le rendement locatif est élevé actuellement pour un budget de 300 000 € ? "
        "Réponds en tant qu'expert en investissement."
    )
    
    analysis = ask_gemini(prompt)
    send_telegram(f"🏗️ *Test Robot Stabilité (Nouvelle Clé)*\n\n{analysis}")
    print("Test envoyé !")
