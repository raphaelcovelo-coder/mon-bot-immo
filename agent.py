import os
import requests

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    if len(text) > 4000:
        text = text[:3950] + "\n\n[Rapport tronqué]"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    try:
        response = requests.post(url, json=payload, timeout=15)
        print(f"Statut Telegram : {response.status_code}")
    except Exception as e:
        print(f"Erreur d'envoi Telegram : {e}")

if __name__ == "__main__":
    print("Lancement de l'agent (Agences Pro & Second Œuvre)...")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    
    prompt = (
        "Agis en tant qu'expert en investissement immobilier. "
        "Donne 2 communes stratégiques dans le Sud-Ouest pour l'achat d'un immeuble de rapport "
        "avec un budget max de 300 000 €. "
        "Règles strictes : "
        "1. **Second œuvre uniquement** : le gros œuvre, la toiture et la structure doivent être sains (pas de travaux lourds de charpente ou de fondation). Rénovation intérieure uniquement (électricité, plomberie, isolation, agencement des lots, cuisines, salles de bains). "
        "2. **Sources alternatives à LeBonCoin et SeLoger** : indique explicitement **quels réseaux d'agences immobilières, portails professionnels ou sites d'agences locales** (ex: Century 21 Entreprise et Commerce, Orpi Pro, Bien'ici, réseaux FNAIM, cabinets d'affaires régionaux) consulter en priorité dans ces secteurs pour trouver ce type de bien, avec la méthode exacte pour y filtrer les immeubles. "
        "Sois précis, direct et structuré (maximum 30 lignes)."
    )
    
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            analysis = result["candidates"][0]["content"]["parts"][0]["text"]
            message = f"CHASSE IMMO - AGENCE PRO & SECOND OEUVRE\n\n{analysis}"
            send_telegram(message)
        else:
            send_telegram(f"Erreur API Gemini ({response.status_code}) : {response.text}")
    except Exception as e:
        send_telegram(f"Erreur de connexion : {e}")
        
    print("Fin du script.")
