import os
import sys
import json
from elevenlabs import ElevenLabs
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import streamlit as st
from dotenv import load_dotenv
from openai_integration.llm_interface import generate_summary
from scrapper.scraper import scrape_the_web

load_dotenv()
ELEVEN_LABS_API_KEY = os.getenv("ELEVEN_LABS_API_KEY")

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
alignment_data = None

if selected_theme:
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("Lancer le scraping"):
            with st.spinner("Analyse en cours..."):
                try:
                    scraped_data = scrape_the_web(selected_theme, depth=1) 
                    
                    summary = generate_summary(selected_theme, str(scraped_data))
                    # summary = "Bonjour ceci est un test du text to speech"
                    
                    if ELEVEN_LABS_API_KEY:
                        try:
                            with st.spinner("Génération de l'audio en cours..."):
                                client = ElevenLabs(api_key=ELEVEN_LABS_API_KEY)
                                voice_id = "CwhRBWXzGAHq8TQ4Fs17"
                                
                                audio_stream = client.text_to_speech.convert_as_stream(
                                    voice_id=voice_id,
                                    output_format="mp3_44100_128",
                                    text=summary,
                                    model_id="eleven_multilingual_v2"
                                )
                                
                                # Convert generator to bytes by consuming all chunks
                                if hasattr(audio_stream, '__iter__'):
                                    audio_chunks = list(audio_stream)  
                                    audio_data = b"".join(audio_chunks)  
                                else:
                                    audio_data = audio_stream
                                    
                                st.success("Audio généré avec succès!")
                                
                        except Exception as e:
                            st.error(f"Erreur lors de la génération de l'audio : {str(e)}")
                            audio_data = None
                    else:
                        st.warning("Clé API ElevenLabs non configurée. L'audio ne sera pas généré.")
                        
                except Exception as e:
                    st.error("Erreur lors de l'analyse : " + str(e))
    
    if summary:
        st.subheader("Résultats de l'analyse")
        
        if audio_data:
            st.audio(audio_data, format="audio/mp3")
            
            speed = st.slider("Vitesse de lecture", min_value=0.5, max_value=2.0, value=1.0, step=0.1)
            st.markdown(f"""
            <script>
            document.addEventListener('DOMContentLoaded', function() {{
                const audioElement = document.querySelector('audio');
                if (audioElement) {{
                    audioElement.playbackRate = {speed};
                }}
            }});
            </script>
            """, unsafe_allow_html=True)
            
        st.markdown(summary)
        
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