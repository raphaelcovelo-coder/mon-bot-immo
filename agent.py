import os
import requests

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        response = requests.post(url, json=payload)
        print(f"Statut Telegram : {response.status_code}")
        print(f"Réponse Telegram : {response.text}")
    except Exception as e:
        print(f"Erreur d'envoi Telegram : {e}")

if __name__ == "__main__":
    print("Début du script d'analyse...")
    
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        
        prompt = (
            "Agis en tant qu'expert immobilier. "
            "Donne une analyse très courte (3 lignes max) des meilleures zones dans le Sud-Ouest "
            "pour un immeuble de rapport (budget 300 000 € max), en tenant compte de la rénovation à coût nul."
        )
        
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        
        response = requests.post(url, headers=headers, json=data)
        print(f"Statut API Gemini : {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            analysis = result["candidates"][0]["content"]["parts"][0]["text"]
            message_final = f"🏗️ *Chasse Immo - Test Diagnostic*\n\n{analysis}"
            send_telegram(message_final)
        else:
            error_msg = f"⚠️ Erreur API Gemini ({response.status_code}) : {response.text}"
            print(error_msg)
            send_telegram(error_msg)
            
    except Exception as e:
        error_critique = f"❌ Erreur critique Python : {str(e)}"
        print(error_critique)
        send_telegram(error_critique)
        
    print("Fin du script.")
