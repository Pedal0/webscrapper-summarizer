import os
import sys
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import streamlit as st
from dotenv import load_dotenv
from openai_integration.llm_interface import generate_summary
from scrapper.scraper import scrape_the_web

load_dotenv()

# Charger la configuration des thèmes
def load_themes():
    themes_path = os.path.join('data', 'themes.json')
    if not os.path.exists(themes_path):
        default_themes = {
            "themes": [
                {"name": "Actualité", "description": "Actualités générales"},
                {"name": "Technologie", "description": "Nouvelles technologies et innovations"},
                {"name": "Science", "description": "Découvertes scientifiques récentes"}
            ]
        }
        with open(themes_path, 'w', encoding='utf-8') as f:
            json.dump(default_themes, f, indent=2, ensure_ascii=False)
    with open(themes_path, 'r', encoding='utf-8') as f:
        return json.load(f)

st.set_page_config(page_title="Web Scraper & OpenAI", layout="wide")

themes_data = load_themes()
themes = themes_data.get('themes', [])

st.title("Web Scraper & OpenRouter Analysis")

selected_theme = st.selectbox("Sélectionnez un thème", [theme['name'] for theme in themes])

if not selected_theme:
    st.warning("Veuillez sélectionner un thème pour continuer")

summary = ""

if selected_theme:
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("Lancer le scraping"):
            with st.spinner("Analyse en cours..."):
                try:
                    scraped_data = scrape_the_web(selected_theme, depth=2) 
                    
                    summary = generate_summary(selected_theme, str(scraped_data))
                    
                except Exception as e:
                    st.error("Erreur lors de l'analyse : " + str(e))
    if not summary=="":
        st.subheader("Résultats de l'analyse")
        st.markdown(summary)

st.markdown('---')
st.info("Applications disponibles :")
for theme in themes:
    st.write(f"- {theme['name']} : {theme['description']}")