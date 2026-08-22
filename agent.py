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
    
    genai.configure(api_key=GEMINI_API_KEY)
    
    # Liste actualisée des modèles récents de Google
    models_to_try = [
        "gemini-3.7-flash",
        "gemini-3.6-flash",
        "gemini-3.5-flash",
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash"
    ]
    
    prompt = (
        "Analyse ces résultats de recherche web brute concernant des immeubles de rapport "
        "à vendre dans le Sud-Ouest (budget max 220 000 €). "
        "Fais un topo court, propre et synthétique avec les liens disponibles :\n\n" + raw_data
    )
    
    # 1. Test des modèles connus de la liste
    for model_name in models_to_try:
        try:
            print(f"Tentative avec le modèle : {model_name}")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            if response and response.text:
                return response.text
        except Exception as e:
            print(f"Modèle {model_name} échoué : {e}")
            continue
            
    # 2. Si aucun de la liste ne passe, on interroge dynamiquement l'API pour trouver n'importe quel modèle compatible
    try:
        print("Interrogation dynamique des modèles disponibles...")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                clean_name = m.name.replace("models/", "")
                print(f"Test du modèle découvert dynamiquement : {clean_name}")
                try:
                    model = genai.GenerativeModel(clean_name)
                    response = model.generate_content(prompt)
                    if response and response.text:
                        return response.text
                except Exception:
                    continue
    except Exception as ex:
        print(f"Erreur lors du listage dynamique : {ex}")

    return "⚠️ Erreur Gemini : Aucun modèle compatible n'a pu être exécuté avec cette clé."

if __name__ == "__main__":
    print("Démarrage de la recherche...")
    raw_data = search_web()
    analysis = analyze_with_gemini(raw_data)
    message = f"🎯 TOPO IMMO - SUD-OUEST\n\n{analysis}"
    send_telegram(message)
    print("Exécution terminée.")
