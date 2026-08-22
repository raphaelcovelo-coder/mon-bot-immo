import os
import requests

GROK_API_KEY = os.environ.get("GROK_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    if len(text) > 4000:
        text = text[:3900] + "\n\n[Rapport tronqué]"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    try:
        requests.post(url, json=payload, timeout=15)
    except Exception as e:
        print(f"Erreur réseau Telegram : {e}")

if __name__ == "__main__":
    if not GROK_API_KEY:
        send_telegram("⚠️ Erreur : GROK_API_KEY introuvable.")
        exit()

    # On demande à l'API xAI la liste des modèles accessibles avec ta clé
    url = "https://api.x.ai/v1/models"
    headers = {"Authorization": f"Bearer {GROK_API_KEY}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Récupère tous les identifiants de modèles disponibles
            models = [m.get("id") for m in data.get("data", [])]
            send_telegram(f"🔍 Modèles xAI disponibles sur ton compte :\n{models}")
        else:
            send_telegram(f"⚠️ Erreur API xAI ({response.status_code}) : {response.text}")
    except Exception as e:
        send_telegram(f"⚠️ Exception technique : {str(e)}")
