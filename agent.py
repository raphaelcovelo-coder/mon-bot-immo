import os
import requests

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    response = requests.post(url, json=payload)
    print(f"Statut Telegram : {response.status_code}")
    print(f"Réponse Telegram : {response.text}")

if __name__ == "__main__":
    print("Début du script...")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    
    prompt = (
        "Agis en tant qu'expert en investissement immobilier. "
        "Donne une analyse courte des meilleures communes du Sud-Ouest pour un immeuble de rapport (budget max 300 000 €, rénovation à coût nul). "
        "Donne pour chaque commune le lien URL direct vers LeBonCoin sous forme d'adresse brute."
    )
    
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    response = requests.post(url, headers=headers, json=data)
    print(f"Statut Gemini : {response.status_code}")
    
    if response.status_code == 200:
        try:
            result = response.json()
            analysis = result["candidates"][0]["content"]["parts"][0]["text"]
            message = f"🏗️ Opportunités & Liens :\n\n{analysis}"
            send_telegram(message)
        except Exception as e:
            err_msg = f"Erreur de traitement du texte : {e}"
            print(err_msg)
            send_telegram(err_msg)
    else:
        err_msg = f"Erreur Gemini ({response.status_code}) : {response.text}"
        print(err_msg)
        send_telegram(err_msg)
