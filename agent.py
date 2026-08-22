import os
import requests
from duckduckgo_search import DDGS
import google.generativeai as genai

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    if len(text) > 4000:
        text = text[:3900] + "\n\n[Rapport tronqué]"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    try:
        response = requests.post(url, json=payload, timeout=15)
        if response.status_code != 200:
            print(f"Erreur Telegram ({response.status_code}): {response.text}")
    except Exception as e:
        print(f"Erreur réseau Telegram : {e}")

def search_real_estate():
    """Recherche gratuite via DuckDuckGo sans clé API"""
    query = "immeuble de rapport a vendre 220000 grand sud ouest gironde landes dordogne lot et garonne"
    results_text = ""
    try:
        with DDGS() as ddgs:
            # Récupère les 10 premiers résultats web du moment
            results = [r for r in ddgs.text(query, max_results=10)]
            for r in results:
                results_text += f"- Titre: {r.get('title')}\n  Lien: {r.get('href')}\n  Extrait: {r.get('body')}\n\n"
    except Exception as e:
        results_text = f"Erreur de recherche DuckDuckGo: {e}"
    return results_text

def analyze_with_gemini(raw_data):
    if not GEMINI_API_KEY:
        return "⚠️ Erreur : GEMINI_API_KEY introuvable dans les secrets."
    
    genai.configure(api_key=GEMINI_API_KEY)
    # Utilisation du modèle gratuit standard
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    prompt = (
        "Voici des résultats de recherche web brute concernant des immeubles de rapport à vendre "
        "dans le Grand Sud-Ouest (budget max 220 000 €). "
        "Analyse ces données et fournis un topo synthétique et percutant : "
        "1. Liste les biens pertinents trouvés (ville, prix approximatif). "
        "2. Fournis les liens directs vers les annonces s'ils sont présents dans les sources. "
        "3. Mets en avant les opportunités intéressantes.\n\n"
        f"Données brutes :\n{raw_data}"
    )
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Erreur Gemini : {str(e)}"

if __name__ == "__main__":
    raw_data = search_real_estate()
    analysis = analyze_with_gemini(raw_data)
    message = f"🎯 TOPO IMMO GRATUIT - SUD-OUEST\n\n{analysis}"
    send_telegram(message)
