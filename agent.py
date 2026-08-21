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
        "Agis en tant qu'expert en investissement immobilier et chasseur de biens spécialisé dans les "
        "immeubles de rapport et les opérations à fort potentiel de valorisation. "
        "Analyse les opportunités, les critères de sélection et les secteurs porteurs (Bassin d'Arcachon et périphérie proche) "
        "pour l'achat d'immeubles de rapport à rénover. "
        "Concentre-toi sur : 1) La création de valeur par la rénovation lourde et l'optimisation des espaces, "
        "2) Le mix locatif intelligent (combinant longue durée et meublé/touristique), "
        "3) Les pièges réglementaires et urbanistiques à éviter dans cette zone. "
        "Rédige un rapport percutant, structuré et directement exploitable."
    )
    
    analysis = ask_gemini(prompt)
    
    message_final = f"🏢 *Chasse Immeuble - Rapport Stratégique*\n\n{analysis}"
    send_telegram(message_final)
    print("Rapport immeuble envoyé !")
