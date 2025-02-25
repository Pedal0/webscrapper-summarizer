from openai import OpenAI
import json
from dotenv import load_dotenv

load_dotenv()

def format_prompt(user_input, theme):
    """Formatte le prompt pour l'envoyer au modèle via OpenRouter en demandant un résumé textuel."""
    prompt = f"""
    Tu as analysé plusieurs textes d'articles traitant du thème : {theme}.
    
    Voici les informations extraites :
    {user_input}
    
    En te basant sur ces informations, rédige un résumé clair et concis sous forme de mini newsletter qui présente :
    - Les points saillants des articles
    - Les tendances principales
    - Un aperçu global des informations apprises
    
    Le résumé doit être facile à lire par un utilisateur et ne contenir aucun formatage JSON.
    """
    return prompt

def send_openai_request(api_key, prompt, temperature=0.7):
    """Envoie une requête à OpenRouter pour récupérer le résumé du LLM"""
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        response = client.chats.create(
            model="nvidia/llama-3.1-nemotron-70b-instruct:free",
            messages=[
                {"role": "system", "content": (
                    "Tu es un assistant expert en synthèse d'informations. "
                    "Génère un résumé clair, concis et compréhensible par un humain. "
                    "La réponse doit être exclusivement du texte explicatif, sans aucun formatage JSON, sans code, et sans autre type de balisage."
                )},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
        )
        # Retourne directement le texte du résumé
        return response.choices[0].message.content
    except Exception as e:
        return f"Erreur lors de la requête OpenRouter : {str(e)}"

def format_openai_response(response):
    """Formate la réponse pour un meilleur affichage"""
    try:
        cleaned_response = response.replace("\\n", "\n").replace("\\\"", "\"")
        return json.loads(cleaned_response)
    except json.JSONDecodeError:
        return response
    except Exception as e:
        return f"Erreur lors du formatage de la réponse : {str(e)}"

def load_themes_from_json():
    """Charge les thèmes disponibles depuis themes.json"""
    try:
        with open('data/themes.json', 'r', encoding="utf-8") as f:
            themes = json.load(f)
            return themes
    except Exception:
        return []

def prepare_context(theme, depth=2):
    """Prépare un contexte pour le modèle en fonction du thème"""
    context = {
        "theme": theme,
        "domain_depth": depth,
        "language": "fr",
        "format": "analytical"
    }
    return context