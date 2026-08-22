import os
import time
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
        response = requests.post(url, json=payload, timeout=15)
        if response.status_code != 200:
            print(f"Erreur Telegram ({response.status_code}): {response.text}")
    except Exception as e:
        print(f"Erreur réseau Telegram : {e}")

def ask_grok_with_retry(prompt, retries=3, delay=5):
    url = "https://api.x.ai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROK_API_KEY}"
    }
    
    data = {
        "model": "grok-4.6",  # Modèle officiel à jour
        "messages": [
            {
                "role": "system",
                "content": "Tu es un expert en investissement immobilier ultra-précis et pragmatique."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3
    }
    
    for attempt in range(retries):
        try:
            response = requests.post(url, headers=headers, json=data, timeout=60)
            if response.status_code == 200:
                result = response.json()
                # Correction du chemin d'accès (ajout de [0] pour cibler le premier choix)
                return result["choices"][0]["message"]["content"]
            elif response.status_code == 429:
                return "ERREUR_QUOTA"
            else:
                print(f"Erreur API xAI ({response.status_code}): {response.text}")
            time.sleep(delay)
        except Exception as e:
            print(f"Erreur tentative {attempt}: {e}")
            time.sleep(delay)
            
    return "Erreur : Impossible de contacter Grok."

if __name__ == "__main__":
    prompt = (
        "Effectue une recherche sur le web en temps réel pour trouver des annonces actuelles "
        "d'immeubles de rapport à vendre dans le **Grand Sud-Ouest** (Lot-et-Garonne, Dordogne, Tarn-et-Garonne, Gironde, Landes) "
        "avec un budget maximum de 220 000 €. "
        "FOURNIS UN TOPO SYNTHÉTIQUE : "
        "1. Liste les biens actuellement visibles sur le web correspondant à ces critères (ville, département, prix). "
        "2. Pour chaque bien trouvé : indique une brève description (surface, état, potentiel d'occupation partielle) et le **lien web direct** vers l'annonce. "
        "3. Mets en avant les opportunités avec du potentiel de second œuvre ou partiellement louées. "
        "Sois direct, percutant et va à l'essentiel pour me simplifier la veille."
    )
    
    analysis = ask_grok_with_retry(prompt)
    
    if analysis == "ERREUR_QUOTA":
        send_telegram("⚠️ Quota journalier Grok atteint.")
    elif analysis.startswith("Erreur"):
        send_telegram(f"⚠️ Erreur Chasse Immo : {analysis}")
    else:
        message = f"🎯 TOPO GROK - SUD-OUEST\n\n{analysis}"
        send_telegram(message)
