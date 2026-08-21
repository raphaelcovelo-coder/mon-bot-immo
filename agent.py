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
    print("Génération du rapport d'investissement (Occupation Partielle)...")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    
    prompt = (
        "Agis en tant qu'expert en investissement immobilier et analyste financier redoutable. "
        "Fournis une analyse ultra-concrète et chiffrée pour un immeuble de rapport dans le Sud-Ouest (ex: Agen, Montauban, Périgueux) "
        "en ciblant **exclusivement des immeubles partiellement occupés** (ex: sur 4 lots, 2 sont déjà loués avec baux en cours et 2 sont vacants/bruts à aménager). "
        "Règles strictes : "
        "1. **Jamais 100% loué, jamais 100% vide** : l'occupation partielle est obligatoire pour avoir du cash-flow immédiat sur les lots loués tout en pouvant attaquer les travaux de second œuvre tout de suite sur les lots vacants, sans attendre le départ de locataires. "
        "2. Budget d'acquisition max : 220 000 € (+ notaire). "
        "3. Structure saine, **second œuvre uniquement** (électricité, plomberie, isolation, cloisons sur les plateaux vacants). "
        "4. **Travaux à 0 € pour l'investisseur** (bénéficiant de la décote partielle et de la valeur ajoutée immédiate). "
        "5. **Simulation financière complète** : "
        "   - Prix d'achat + Notaire. "
        "   - Loyers actuels des lots occupés VS potentiel total une fois les plateaux vacants rénovés. "
        "   - Mensualité de crédit (25 ans) et calcul précis du **cash-flow net dès le premier mois**. "
        "6. **Sources pros** : Cite des sites spécialisés (ex: immo-notaires.fr, agorastore.fr, cessions professionnelles). "
        "CONSIGNES DE MISE EN PAGE : Sois percutant, va droit au but, utilise des listes à puces courtes pour tenir en un seul message Telegram (sous les 3800 caractères)."
    )
    
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            analysis = result["candidates"][0]["content"]["parts"][0]["text"]
            message = f"🎯 CHASSE IMMO - OCCUPATION PARTIELLE & CASH-FLOW\n\n{analysis}"
            send_telegram(message)
        elif response.status_code == 429:
            print("Quota journalier atteint (429).")
        else:
            send_telegram(f"Erreur API Gemini ({response.status_code}) : {response.text}")
            
    except Exception as e:
        send_telegram(f"Erreur de connexion : {e}")
        
    print("Fin du script.")
