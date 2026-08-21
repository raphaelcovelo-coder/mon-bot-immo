import os
import requests

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_debug_telegram(message):
    print("Tentative d'envoi Telegram...")
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        response = requests.post(url, json=payload)
        print(f"Statut HTTP Telegram : {response.status_code}")
        print(f"Réponse Telegram : {response.text}")
    except Exception as e:
        print(f"ERREUR CRITIQUE DANS L'ENVOI TELEGRAM : {e}")

if __name__ == "__main__":
    print("--- DÉBUT DU SCRIPT ---")
    
    # 1. Vérification des secrets (sans les afficher en entier pour la sécurité)
    print(f"Clé Gemini présente : {bool(GEMINI_API_KEY)}")
    print(f"Token Telegram présent : {bool(TELEGRAM_TOKEN)}")
    print(f"Chat ID présent : {bool(TELEGRAM_CHAT_ID)}")

    # 2. Test ultra-simple sans Gemini pour vérifier la connexion Telegram
    test_message = "🤖 Test de connexion robot : OK"
    print("Envoi du message de test...")
    send_debug_telegram(test_message)
    
    print("--- FIN DU SCRIPT ---")
