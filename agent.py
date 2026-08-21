import os
import requests

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"Statut Telegram : {response.status_code}")
        print(f"Réponse Telegram : {response.text}")
    except Exception as e:
        print(f"Erreur d'envoi Telegram : {e}")

if __name__ == "__main__":
    print("Début de la recherche d'immeubles à rénover...")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    
    prompt = (
        "Agis en tant qu'expert en investissement immobilier. "
        "Donne 2 communes dans le Sud-Ouest idéales pour acheter un immeuble de rapport **à rénover** "
        "(budget max 300 000 €, recherche de passoires thermiques ou de gros œuvre, exclure absolument le clé en main). "
        "Précise pourquoi c'est intéressant avec tes travaux à coût nul, et inclus des liens URL bruts vers LeBonCoin pour ces recherches."
    )
    
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        # Timeout de 30 secondes pour éviter que le script ne bloqué
        response = requests.post(url, headers=headers, json=data, timeout=30)
        print(f"Statut Gemini : {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            analysis = result["candidates"][0]["content"]["parts"][0]["text"]
            message = f"CHASSE IMMO - SPECIAL RENOVATION\n\n{analysis}"
            send_telegram(message)
        else:
            err_msg = f"Erreur API Gemini ({response.status_code}) : {response.text}"
            print(err_msg)
            send_telegram(err_msg)
            
    except Exception as e:
        err_msg = f"Erreur de connexion : {e}"
        print(err_msg)
        send_telegram(err_msg)
        
    print("Fin du script.")
