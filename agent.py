import os
import requests

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def ask_gemini(prompt):
    # Utilisation du modèle standard (quota de texte très large, sans blocage 429)
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
    response = requests.post(url, json=payload)
    print(f"Statut Telegram : {response.status_code}")

if __name__ == "__main__":
    print("Génération de l'analyse stratégique et des liens de recherche...")
    
    prompt = (
        "Agis en tant que chasseur immobilier expert. "
        "Fournis une analyse stratégique pour l'achat d'un immeuble de rapport dans le Sud-Ouest "
        "(Gironde, Landes, Lot-et-Garonne, Dordogne) avec ces critères stricts : "
        "1. Budget maximum : 300 000 €. "
        "2. Immeuble résidentiel uniquement (exclure tout local commercial). "
        "3. Intègre le fait que les travaux de rénovation sont à coût nul pour viser un cash-flow positif immédiat sur un crédit de 25 ans. "
        "Donne 3 secteurs géographiques précis (villes moyennes) très porteurs pour ce profil, "
        "et inclus les liens URL directs vers les recherches pré-filtrées sur LeBonCoin pour ces zones."
    )
    
    analysis = ask_gemini(prompt)
    
    message_final = f"🏗️ *Chasse Immo - Stratégie & Accès Direct*\n\n{analysis}"
    send_telegram(message_final)
    print("Rapport envoyé sur Telegram !")
