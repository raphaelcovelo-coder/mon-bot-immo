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
    
    # Recherche web en direct activée pour scanner le web
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "tools": [{"googleSearch": {}}]
    }
    
    for attempt in range(retries):
        try:
            response = requests.post(url, headers=headers, json=data, timeout=60)
            if response.status_code == 200:
                result = response.json()
                return result["candidates"][0]["content"]["parts"][0]["text"]
            elif response.status_code == 429:
                return "ERREUR_QUOTA"
            time.sleep(delay)
        except Exception as e:
            print(f"Erreur tentative {attempt}: {e}")
            time.sleep(delay)
    return "Erreur : Impossible de contacter Gemini."

if __name__ == "__main__":
    prompt = (
        "Effectue une recherche sur le web en temps réel pour trouver des annonces actuelles "
        "d'immeubles de rapport à vendre dans le **Grand Sud-Ouest** (ex: Lot-et-Garonne, Dordogne, Tarn-et-Garonne, Gironde, Landes) "
        "avec un budget maximum de 220 000 €. "
        "FOURNIS UN TOPO SYNTHÉTIQUE : "
        "1. Liste les biens actuellement visibles sur le web correspondant à ces critères (ville, département, prix). "
        "2. Pour chaque bien trouvé : indique une brève description (surface, état, potentiel d'occupation partielle) et le **lien web direct** vers l'annonce. "
        "3. Mets en avant les opportunités avec du potentiel de second œuvre ou partiellement louées. "
        "Sois direct, percutant et va à l'essentiel pour me simplifier la veille."
    )
    
    analysis = ask_gemini_with_retry(prompt)
    
    if analysis == "ERREUR_QUOTA":
        send_telegram("⚠️ Quota journalier atteint.")
    elif analysis.startswith("Erreur"):
        send_telegram(f"⚠️ Erreur Chasse Immo : {analysis}")
    else:
        message = f"🎯 TOPO ANNONCES LIVE - SUD-OUEST\n\n{analysis}"
        send_telegram(message)
