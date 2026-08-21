import os
import time
import requests

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def ask_gemini(prompt, retries=3, delay=5):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    for attempt in range(retries):
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            try:
                return response.json()["candidates"][0]["content"]["parts"][0]["text"]
            except Exception as e:
                return f"Erreur de lecture : {e}"
        elif response.status_code == 503:
            print(f"Surcharge Google (503), tentative {attempt + 1}/{retries}...")
            time.sleep(delay)
        else:
            return f"Erreur API Gemini ({response.status_code}) : {response.text}"
    return "Erreur : Modèle indisponible."

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    response = requests.post(url, json=payload)
    # On ajoute un log pour voir la réponse de Telegram
    print(f"Statut Telegram : {response.status_code}")
    print(f"Réponse Telegram : {response.text}")

if __name__ == "__main__":
    print("Début analyse...")
    prompt = "Donne une analyse très courte (3 lignes) sur le marché des immeubles de rapport dans le Sud-Ouest."
    analysis = ask_gemini(prompt)
    print(f"Analyse reçue, taille : {len(analysis)} caractères")
    
    message_final = f"🏗️ *Test Robot*\n\n{analysis}"
    send_telegram(message_final)
    print("Fin du script.")
