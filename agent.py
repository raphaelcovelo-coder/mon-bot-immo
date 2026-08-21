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
    except Exception as e:
        print(f"Erreur d'envoi Telegram : {e}")

if __name__ == "__main__":
    print("Lancement de l'agent (Ciblage Second Œuvre)...")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    
    prompt = (
        "Agis en tant qu'expert en investissement immobilier. "
        "Donne 2 communes porteuses dans le Sud-Ouest pour l'achat d'un immeuble de rapport "
        "avec un budget maximum de 300 000 €. "
        "Règles strictes sur les travaux : "
        "- **Second œuvre uniquement** : le gros œuvre (toiture, charpente, structure) doit être sain. "
        "- Les travaux se concentrent sur l'intérieur : électricité, plomberie, isolation, création de cloisons/lots, salles de bains, cuisines, peintures et sols. "
        "- Exclure le clé en main (il faut de la création de valeur par l'intérieur) et exclure les chantiers de gros œuvre lourd. "
        "Fournis une analyse claire, le profil des biens recherchés, et des liens de recherche web fonctionnels et stables pour consulter les annonces."
    )
    
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            analysis = result["candidates"][0]["content"]["parts"][0]["text"]
            message = f"CHASSE IMMO - SECOND OEUVRE\n\n{analysis}"
            send_telegram(message)
        else:
            send_telegram(f"Erreur API Gemini ({response.status_code}) : {response.text}")
    except Exception as e:
        send_telegram(f"Erreur de connexion : {e}")
        
    print("Fin du script.")
