import os
import sys
import json
import requests
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import streamlit as st
from dotenv import load_dotenv
from openai_integration.llm_interface import generate_summary
from scrapper.scraper import scrape_the_web

load_dotenv()
RAPID_API_KEY = os.getenv("RAPID_API_KEY")

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
audio_data = None

if selected_theme:
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("Lancer le scraping"):
            with st.spinner("Analyse en cours..."):
                try:
                    scraped_data = scrape_the_web(selected_theme, depth=1)
                    summary = generate_summary(selected_theme, str(scraped_data))
                    
                    with st.spinner("Génération de l'audio en cours..."):
                        try:
                            # Utilisation de l'API Streamlined Edge TTS
                            tts_url = "https://streamlined-edge-tts.p.rapidapi.com/tts"
                            payload = {
                                "text": summary.replace('*', ''),
                                "voice": "fr-FR-RemyMultilingual"  
                            }
                            tts_headers = {
                                "x-rapidapi-key": RAPID_API_KEY,
                                "x-rapidapi-host": "streamlined-edge-tts.p.rapidapi.com",
                                "Content-Type": "application/json"
                            }
                            tts_response = requests.post(tts_url, json=payload, headers=tts_headers)
                            if tts_response.status_code == 200:
                                content_type = tts_response.headers.get("Content-Type", "")
                                if "audio" in content_type:
                                    audio_data = tts_response.content
                                    st.success("Audio généré avec succès!")
                                else:
                                    st.error("La réponse n'est pas un flux audio. Content-Type: " + content_type)
                            else:
                                st.error("Erreur lors de la génération de l'audio: " + tts_response.text)
                        except Exception as e:
                            st.error("Erreur lors de la génération de l'audio: " + str(e))
                            
                except Exception as e:
                    st.error("Erreur lors de l'analyse : " + str(e))
    
    if summary:
        st.subheader("Résultats de l'analyse")
        
        if audio_data:
            st.audio(audio_data, format="audio/mp3")
                    
        if audio_data:
            st.download_button(
                label="Télécharger l'audio (MP3)",
                data=audio_data,
                file_name=f"summary_{selected_theme.lower().replace(' ', '_')}.mp3",
                mime="audio/mp3"
            )

st.markdown('---')
st.info("Applications disponibles :")
for theme in themes:
    st.write(f"- {theme['name']} : {theme['description']}")
