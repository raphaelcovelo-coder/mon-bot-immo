import os
import requests

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def ask_gemini(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        try:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            return f"Erreur de lecture de la réponse : {e}"
    else:
        return f"Erreur API Gemini ({response.status_code}) : {response.text}"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
        # On retire le parse_mode pour éviter tout blocage
    }
    response = requests.post(url, json=payload)
    print(f"Statut Telegram : {response.status_code} - {response.text}")

if __name__ == "__main__":
    print("L'agent analyse le marché immobilier...")
    
    prompt = (
        "Agis en tant qu'expert en investissement immobilier et chasseur de biens. "
        "Donne une analyse très courte et percutante (5 lignes max) sur le marché de Gujan-Mestras."
    )
    
    analysis = ask_gemini(prompt)
    
    message_final = f"🏡 Rapport Stratégique - Agent Immo\n\n{analysis}"
    send_telegram(message_final)
    print("Script terminé !")
