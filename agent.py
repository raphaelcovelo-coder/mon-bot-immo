import os
import requests

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def ask_gemini(prompt):
    # Changement ici : v1beta devient v1
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        try:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            return f"Erreur de lecture : {e}"
    else:
        return f"Erreur API Gemini ({response.status_code}) : {response.text}"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    requests.post(url, json=payload)

if __name__ == "__main__":
    prompt = (
        "Agis en tant qu'expert en investissement immobilier. "
        "Donne une analyse très courte (5 lignes max) sur le potentiel locatif à Gujan-Mestras."
    )
    analysis = ask_gemini(prompt)
    message_final = f"🏡 Rapport Stratégique - Agent Immo\n\n{analysis}"
    send_telegram(message_final)
