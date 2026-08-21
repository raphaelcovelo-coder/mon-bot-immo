import os
import requests

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    if len(text > 4000):
        text = text[:3950] + "\n\n[Rapport tronqué]"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    try:
        response = requests.post(url, json=payload, timeout=15)
        print(f"Statut Telegram : {response.status_code}")
    except Exception as e:
        print(f"Erreur d'envoi Telegram : {e}")

if __name__ == "__main__":
    print("Génération du rapport d'investissement chiffré...")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    
    prompt = (
        "Agis en tant qu'expert en investissement immobilier et analyste financier redoutable. "
        "Fournis une analyse ultra-concrète pour un immeuble de rapport dans le Sud-Ouest (ex: Agen, Montauban, ou Périgueux) "
        "avec ces contraintes strictes : "
        "1. Budget d'acquisition max : 220 000 € (+ frais de notaire). "
        "2. Structure saine, **second œuvre uniquement** (électricité, plomberie, isolation, cloisons, finitions). "
        "3. **Travaux à 0 € pour l'investisseur** (mais intègre leur valeur théorique de marché dans le calcul de création de valeur / plus-value latente). "
        "4. **Simulation financière complète et chiffrée** : "
        "   - Prix d'achat + Notaire + Valeur des travaux de second œuvre. "
        "   - Valeur vénale estimée post-rénovation (création de fonds propres immédiats). "
        "   - Recettes locatives détaillées (ex: nombre de lots, loyer par lot, total mensuel et annuel). "
        "   - Mensualité de crédit estimée (sur 25 ans à taux actuel). "
        "   - **Cash-flow net mensuel** calculé. "
        "5. **Sites professionnels ciblés** : donne les liens URL exacts ou noms de plateformes spécifiques non grand public (ex: immo-notaires.fr, agorastore.fr, cession-commerce.com, ou sections 'professionnels/murs' des réseaux locaux) où trouver ce type de bien."
    )
    
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            analysis = result["candidates"][0]["content"]["parts"][0]["text"]
            message = f"🎯 CHASSE IMMO - SIMULATION & PÉPITE\n\n{analysis}"
            send_telegram(message)
        else:
            send_telegram(f"Erreur API Gemini ({response.status_code}) : {response.text}")
    except Exception as e:
        send_telegram(f"Erreur de connexion : {e}")
        
    print("Fin du script.")
