name: Immo Search Agent

on:
  workflow_dispatch: # Permet de déclencher un envoi immédiat quand tu cliques sur "Run workflow"
  schedule:
    - cron: '0 8 * * *'   # Premier envoi de la journée (8h00)
    - cron: '0 14 * * *'  # Deuxième envoi de la journée (14h00)

jobs:
  run-agent:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: pip install requests

      - name: Run agent
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          TELEGRAM_TOKEN: ${{ secrets.TELEGRAM_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
        run: python agent.py
