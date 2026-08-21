import os
import requests

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def ask_gemini(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={GEMINI_API_KEY}"
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
    print("L'agent analyse le marché des immeubles de rapport...")
    
    prompt = (
        "Agis en tant qu'expert en investissement immobilier. "
        "Recherche et analyse des opportunités d'immeubles de rapport dans le Sud-Ouest. "
        "Critères stricts : "
        "1. Budget total max : 300 000 €. "
        "2. Typologie : Immeuble résidentiel uniquement (exclure tout local commercial). "
        "3. État : 50% d'occupation actuelle (moitié en activité). "
        "4. Levier financier : Les travaux de rénovation sont à coût zéro (avantage professionnel). "
        "5. Objectif : Crédit sur 25 ans avec cash-flow positif quasi immédiat grâce à l'optimisation des surfaces rénovées gratuitement. "
        "Identifie les secteurs du Sud-Ouest où ce modèle est le plus viable. "
        "Présente une analyse stratégique percutante et les points de vigilance financiers."
    )
    
    analysis = ask_gemini(prompt)
    
    message_final = f"🏗️ *Chasse Immo - Stratégie Optimisée*\n\n{analysis}"
    send_telegram(message_final)
    print("Rapport immeuble envoyé !")
