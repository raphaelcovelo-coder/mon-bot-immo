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
    
    # Requêtes ultra-ciblées pour forcer la remontée de vraies annonces immobilières
    queries = [
        "site:bienici.com immeuble de rapport a vendre dordogne lot-et-garonne 220000",
        "site:seloger.com immeuble a vendre bergerac marmande",
        "immeuble de rapport a vendre bergerac marmande 220000"
    ]
    
    results_text = ""
    for q in queries:
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(q, max_results=4, backend="html"))
                if results:
                    for r in results:
                        title = r.get('title', '')
                        href = r.get('href', '')
                        body = r.get('body', '')
                        results_text += f"- Annonce: {title}\n  Lien: {href}\n  Détails: {body}\n\n"
        except Exception as e:
            print(f"Erreur sur la requête '{q}': {e}")
            continue
            
    if not results_text.strip():
        results_text = "Aucune annonce brute récupérée ce matin, application du modèle d'analyse standard."
        
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
        "Agis en tant qu'expert en investissement immobilier. "
        "Voici des données brutes extraites du web concernant des immeubles de rapport (budget max 220k€) "
        "dans le Grand Sud-Ouest (Bergerac, Marmande, Dordogne, Lot-et-Garonne) :\n\n"
        f"{raw_data}\n\n"
        "Génère un topo ultra-pratique et percutant pour Telegram comprenant :\n"
        "1. **Les annonces réelles identifiées** (Ville, Prix affiché, et **le lien web direct** extrait des sources ci-dessus).\n"
        "2. **Simulation financière type** pour un bien à 180 000 € FAI :\n"
        "   - Emprunt total (achat + notaire ~194 400 €) sur 25 ans à ~3,6% (Mensualité globale ~1 033 €/mois).\n"
        "   - Rappel de l'atout majeur : **Travaux de rénovation à 0 €** pour l'investisseur (pas d'enveloppe travaux à emprunter, valorisation nette instantanée).\n"
        "   - Loyers estimés après optimisation (ex: 3 lots meublés = ~1 850 €/mois).\n"
        "   - **Cash-flow net estimé** et rentabilité brute."
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
    print("Démarrage de la recherche automatisée d'annonces...")
    raw_data = search_web()
    analysis = analyze_with_gemini(raw_data)
    message = f"🎯 TOPO IMMO & RENTABILITÉ - SUD-OUEST\n\n{analysis}"
    send_telegram(message)
    print("Exécution terminée.")
