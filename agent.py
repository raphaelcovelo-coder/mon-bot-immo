import os
import time
import requests

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    if len(text) > 4000:
        text = text[:3900] + "\n\n[Rapport tronqué]"
    # Pas de Markdown pour éviter les erreurs de formatage, Telegram gère les liens auto
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    try:
        response = requests.post(url, json=payload, timeout=15)
        if response.status_code != 200:
            print(f"Erreur Telegram ({response.status_code}): {response.text}")
    except Exception as e:
        print(f"Erreur réseau Telegram : {e}")

def ask_gemini_with_retry(prompt, retries=3, delay=5):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    for attempt in range(retries):
        try:
            response = requests.post(url, headers=headers, json=data, timeout=60)
            if response.status_code == 200:
                return response.json()["candidates"][0]["content"]["parts"][0]["text"]
            elif response.status_code == 429:
                return "ERREUR_QUOTA"
            time.sleep(delay)
        except Exception as e:
            print(f"Erreur tentative {attempt}: {e}")
            time.sleep(delay)
    return "Erreur : Impossible de contacter Gemini."

if __name__ == "__main__":
    # Prompt optimisé pour inclure Analyse + Liens Dynamiques + Script
    prompt = (
        "Agis en tant qu'expert en investissement immobilier. "
        "Analyse un immeuble de rapport (Agen, 220k€ max, partiellement occupé). "
        "STRUCTURE DE RÉPONSE OBLIGATOIRE : "
        "1. ANALYSE FINANCIÈRE : Prix, travaux 0€, cash-flow net immédiat (dès le 1er mois). "
        "2. RADAR DE RECHERCHE (LIENS DYNAMIQUES) : Copie ces liens exacts pour surveiller le marché en temps réel :"
        "- Agences Agen (Google Search) : https://www.google.com/search?q=immeuble+de+rapport+Agen+à+vendre+agence+immobilière "
        "- Leboncoin Pro (Agen) : https://www.leboncoin.fr/recherche?category=9&locations=Agen_47000&price=max-220000&real_estate_type=4 "
        "3. SCRIPT VIP (À copier-coller pour appeler les agences) : "
        "'Bonjour, je suis investisseur sur Agen. Je recherche un immeuble de rapport (budget 220k) avec occupation partielle. "
        "J'ai une capacité de financement validée. Pouvez-vous me mettre en priorité sur vos mandats 'off-market' ?'"
        "Sois percutant, concis, liste à puces."
    )
    
    analysis = ask_gemini_with_retry(prompt)
    
    if analysis == "ERREUR_QUOTA":
        send_telegram("⚠️ Quota journalier atteint.")
    elif analysis.startswith("Erreur"):
        send_telegram(f"⚠️ Erreur Chasse Immo : {analysis}")
    else:
        message = f"🎯 CHASSE IMMO - STRATÉGIE COMPLÈTE\n\n{analysis}"
        send_telegram(message)
