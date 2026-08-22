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

if not GROK_API_KEY:
    # Diagnostic : on liste ce que GitHub envoie vraiment au script
    env_keys = list(os.environ.keys())
    debug_msg = f"⚠️ ERREUR : GROK_API_KEY introuvable.\n\nVariables reçues de GitHub :\n{env_keys}"
    send_telegram(debug_msg)
    exit()

def ask_grok(prompt):
    url = "https://api.x.ai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROK_API_KEY}"
    }
    
    data = {
        "model": "grok-2",
        "messages": [
            {"role": "system", "content": "Tu es un expert en investissement immobilier pragmatique."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            return f"⚠️ Erreur API xAI ({response.status_code}) : {response.text}"
    except Exception as e:
        return f"⚠️ Exception technique : {str(e)}"

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
    
    analysis = ask_grok(prompt)
    message = f"🎯 TOPO GROK - SUD-OUEST\n\n{analysis}"
    send_telegram(message)
