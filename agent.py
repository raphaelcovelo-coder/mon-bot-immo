import os
import requests

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    # Sécurité anti-dépassement de la limite Telegram (4096 caractères max)
    if len(text) > 4000:
        text = text[:3950] + "\n\n[Rapport tronqué pour respecter la limite Telegram]"
        
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    try:
        response = requests.post(url, json=payload, timeout=15)
        print(f"Statut Telegram : {response.status_code}")
        print(f"Réponse Telegram : {response.text}")
    except Exception as e:
        print(f"Erreur d'envoi Telegram : {e}")

if __name__ == "__main__":
    print("Lancement de l'agent (Second Œuvre & Sécurité Taille)...")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    
    prompt = (
        "Agis en tant qu'expert en investissement immobilier. "
        "Donne 2 communes stratégiques dans le Sud-Ouest pour l'achat d'un immeuble de rapport "
        "avec un budget max de 300 000 €. "
        "Règles strictes : "
        "1. **Second œuvre uniquement** : le gros œuvre, la toiture et la structure doivent être sains. Pas de travaux lourds de charpente ou de murs porteurs. "
        "2. Rénovation intérieure ciblée : électricité, plomberie, isolation, agencement des lots, cuisines, salles de bains, peintures. (Exclure le clé en main). "
        "3. Ne mets pas de liens URL (ils ne fonctionnent pas). À la place, donne les **mots-clés exacts et les filtres précis** à appliquer sur LeBonCoin pour trouver ces biens rapidement. "
        "Sois concis, direct et va droit au but (maximum 25 lignes)."
    )
    
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        print(f"Statut Gemini : {response.status_code}")
        
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
