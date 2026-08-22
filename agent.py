import os
import time
import requests

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    if len(text) > 4000:
        text = text[:3900] + "\n\n[Rapport tronqué]"
    
    # Pas de parse_mode pour éviter les crashs, Telegram transforme 
    # automatiquement les https:// en liens cliquables.
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    
    try:
        response = requests.post(url, json=payload, timeout=15)
        if response.status_code != 200:
            print(f"Erreur Telegram ({response.status_code}): {response.text}")
    except Exception as e:
        print(f"Erreur réseau Telegram : {e}")

def ask_gemini_with_retry(prompt, retries=3, delay=5):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    for attempt in range(retries):
        try:
            response = requests.post(url, headers=headers, json=data, timeout=60)
            if response.status_code == 200:
                return response.json()["candidates"][0]["content"]["parts"][0]["text"]
            elif response.status_code == 429:
                return "ERREUR_QUOTA"
            time.sleep(delay)
        except Exception as e:
            print(f"Erreur tentative {attempt}: {e}")
            time.sleep(delay)
    return "Erreur : Impossible de contacter Gemini."

if __name__ == "__main__":
    prompt = (
        "Agis en tant qu'expert en investissement immobilier. "
        "Analyse un immeuble de rapport dans le Sud-Ouest (Agen), partiellement occupé. "
        "1. Budget max 220k€. 2. Second œuvre uniquement. 3. Simulation : Prix, travaux 0€, cash-flow net dès le 1er mois. "
        "4. **Liens directs obligatoires** : Fournis les liens URL complets et fonctionnels (ex: https://www.immo-notaires.fr et https://www.agorastore.fr) écrits en entartier brut pour qu'ils soient cliquables. "
        "Sois percutant, concis, liste à puces."
    )
    
    analysis = ask_gemini_with_retry(prompt)
    
    if analysis == "ERREUR_QUOTA":
        send_telegram("⚠️ Quota journalier atteint. Réessai demain.")
    elif analysis.startswith("Erreur"):
        send_telegram(f"⚠️ Erreur Chasse Immo : {analysis}")
    else:
        message = f"🎯 CHASSE IMMO\n\n{analysis}"
        send_telegram(message)
