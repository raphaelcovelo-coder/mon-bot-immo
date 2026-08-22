import os
import time
import requests

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    if len(text) > 4000:
        text = text[:3950] + "\n\n[Rapport tronqué]"
    
    # Utilisation du mode Markdown pour rendre les liens cliquables
    payload = {
        "chat_id": TELEGRAM_CHAT_ID, 
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False # Laisse un aperçu propre si disponible
    }
    
    try:
        response = requests.post(url, json=payload, timeout=15)
        print(f"Statut Telegram : {response.status_code}")
    except Exception as e:
        print(f"Erreur d'envoi Telegram : {e}")

def ask_gemini_with_retry(prompt, retries=5, delay=5):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    for attempt in range(retries):
        try:
            response = requests.post(url, headers=headers, json=data, timeout=60)
            if response.status_code == 200:
                return response.json()["candidates"][0]["content"]["parts"][0]["text"]
            elif response.status_code == 503:
                print(f"Surcharge Google (503), tentative {attempt + 1}/{retries} dans {delay}s...")
                time.sleep(delay)
                delay *= 2
            elif response.status_code == 429:
                return "QUOTA_EXCEEDED"
            else:
                return f"Erreur API ({response.status_code}) : {response.text}"
        except Exception as e:
            print(f"Erreur réseau tentative {attempt + 1}: {e}")
            time.sleep(delay)
            
    return "Erreur : Le modèle est temporairement surchargé (503)."

if __name__ == "__main__":
    print("Génération du rapport avec liens de recherche ciblés...")
    
    prompt = (
        "Agis en tant qu'expert en investissement immobilier et analyste financier redoutable. "
        "Fournis une analyse ultra-concrète et chiffrée pour un immeuble de rapport dans le Sud-Ouest (ex: Agen) "
        "en ciblant **exclusivement des immeubles partiellement occupés** (ex: sur 4 lots, 2 loués et 2 vacants/bruts). "
        "Règles strictes : "
        "1. Budget d'acquisition max : 220 000 € (+ notaire). "
        "2. Structure saine, **second œuvre uniquement** (électricité, plomberie, isolation sur les plateaux vacants). "
        "3. Simulation financière complète : Prix d'achat, notaire, travaux à 0€, loyers actuels vs futurs, mensualité de crédit (25 ans), et **cash-flow net dès le premier mois**. "
        "4. **LIENS WEB STABLES OBLIGATOIRES** : Fournis 2 liens Markdown cliquables vers des plateformes de recherche spécifiques et fonctionnelles (ex: [Recherche Immo-Notaires Agen](https://www.immo-notaires.fr) ou [Agorastore Nouvelle-Aquitaine](https://www.agorastore.fr)). Les liens doivent utiliser le format Markdown [Nom du site](URL) pour être cliquables sur Telegram. "
        "CONSIGNES DE MISE EN PAGE : Sois percutant, utilise des listes à puces courtes pour tenir en un seul message Telegram (sous les 3800 caractères)."
    )
    
    analysis = ask_gemini_with_retry(prompt)
    
    if analysis == "QUOTA_EXCEEDED":
        print("Quota journalier atteint (429).")
    elif analysis.startswith("Erreur"):
        send_telegram(f"⚠️ *Chasse Immo* : {analysis}")
    else:
        message = f"🎯 *CHASSE IMMO - OCCUPATION PARTIELLE & LIENS*\n\n{analysis}"
        send_telegram(message)
        
    print("Fin du script.")
