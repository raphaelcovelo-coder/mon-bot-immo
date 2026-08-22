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
        return "Module de recherche non disponible."
    
    queries = [
        "immeuble de rapport a vendre gironde landes dordogne 220000",
        "immobilier immeuble de rapport sud ouest pas cher",
        "annonce immeuble a vendre lot et garonne dordogne"
    ]
    
    results_text = ""
    for q in queries:
        try:
            with DDGS() as ddgs:
                # Utilisation de backend="html" pour éviter les blocages de serveurs GitHub
                results = list(ddgs.text(q, max_results=3, backend="html"))
                if results:
                    for r in results:
                        results_text += f"- Titre: {r.get('title')}\n  Lien: {r.get('href')}\n  Extrait: {r.get('body')}\n\n"
                    break
        except Exception as e:
            print(f"Tentative échouée pour '{q}': {e}")
            continue
            
    # Fallback intelligent si le web est bloqué, pour ne jamais renvoyer de texte vide
    if not results_text.strip():
        results_text = (
            "Recherche en direct restreinte par le réseau. "
            "Cible la veille active d'immeubles de rapport dans le Grand Sud-Ouest "
            "(Lot-et-Garonne, Dordogne, Tarn-et-Garonne, Gironde, Landes) avec un budget max de 220 000 €, "
            "en ciblant des biens à rénover (potentiel de second œuvre, appartements de 2 à 3 lots)."
        )
    return results_text

def analyze_with_gemini(raw_data):
    if not GEMINI_API_KEY:
        return "⚠️ Erreur : La clé GEMINI_API_KEY est introuvable dans les Secrets GitHub."
    
    genai.configure(api_key=GEMINI_API_KEY)
    
    models_to_try = [
        "gemini-3.7-flash",
        "gemini-3.6-flash",
        "gemini-3.5-flash",
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash"
    ]
    
    prompt = (
        "Agis en tant qu'expert en investissement immobilier pragmatique. "
        "À partir des éléments suivants, fournis un topo synthétique, percutant et structuré "
        "pour la recherche d'immeubles de rapport dans le Grand Sud-Ouest (budget max 220 000 €) :\n\n"
        f"{raw_data}\n\n"
        "Structure ta réponse exactement sous ce format :\n"
        "* **Localisation & Prix FAI ciblés**\n"
        "* **Composition type** (nombre de lots, surfaces, potentiel)\n"
        "* **Stratégie & Rentabilité brute estimée**\n"
        "* **Points d'attention** (travaux, second œuvre)\n"
        "* **Liens utiles / Plateformes de veille**"
    )
    
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            if response and response.text:
                return response.text
        except Exception:
            continue
            
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                clean_name = m.name.replace("models/", "")
                try:
                    model = genai.GenerativeModel(clean_name)
                    response = model.generate_content(prompt)
                    if response and response.text:
                        return response.text
                except Exception:
                    continue
    except Exception:
        pass

    return "⚠️ Erreur Gemini : Aucun modèle compatible n'a pu être exécuté."

if __name__ == "__main__":
    print("Démarrage de la recherche...")
    raw_data = search_web()
    analysis = analyze_with_gemini(raw_data)
    message = f"🎯 TOPO IMMO - SUD-OUEST\n\n{analysis}"
    send_telegram(message)
    print("Exécution terminée.")
