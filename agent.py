import os
import requests
import google.generativeai as genai

try:
    from duckduckgo_search import DDGS
    HAS_DDG = True
except ImportError:
    HAS_DDG = False

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram(text):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Erreur : Identifiants Telegram manquants.")
        return
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

def search_web():
    if not HAS_DDG:
        return "Erreur : Le module duckduckgo_search n'est pas installé."
    
    query = "immeuble de rapport a vendre 220000 grand sud ouest gironde landes"
    results_text = ""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
            for r in results:
                results_text += f"- Titre: {r.get('title')}\n  Lien: {r.get('href')}\n  Extrait: {r.get('body')}\n\n"
    except Exception as e:
        results_text = f"Erreur lors de la recherche web : {str(e)}"
    return results_text

def analyze_with_gemini(raw_data):
    if not GEMINI_API_KEY:
        return "⚠️ Erreur : La clé GEMINI_API_KEY est introuvable dans les Secrets GitHub."
    
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Détection automatique d'un modèle disponible pour éviter les erreurs 404
        chosen_model = "gemini-1.5-flash"
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    chosen_model = m.name
                    break
        except Exception:
            pass

        model = genai.GenerativeModel(chosen_model)
        
        prompt = (
            "Analyse ces résultats de recherche web brute concernant des immeubles de rapport "
            "à vendre dans le Sud-Ouest (budget max 220 000 €). "
            "Fais un topo court, propre et synthétique avec les liens disponibles :\n\n" + raw_data
        )
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Erreur Gemini : {str(e)}"

if __name__ == "__main__":
    print("Démarrage de la recherche...")
    raw_data = search_web()
    analysis = analyze_with_gemini(raw_data)
    message = f"🎯 TOPO IMMO - SUD-OUEST\n\n{analysis}"
    send_telegram(message)
    print("Exécution terminée.")
