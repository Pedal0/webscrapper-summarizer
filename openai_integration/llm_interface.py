import os
import json
from typing import Dict, Any
from openai import OpenAI 
from dotenv import load_dotenv

load_dotenv()

def initialize_openai_client() -> OpenAI:
    """Initialiser le client OpenRouter avec les clés d'accès"""
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    if not openrouter_api_key:
        raise ValueError("OPENROUTER_API_KEY non trouvé")
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=openrouter_api_key,
    )
    return client

def format_prompt(theme: str, instructions: str = None, examples: list = None) -> str:
    """Formater la question pour le modèle de langage"""
    prompt = f"Theme: {theme}"
    if instructions:
        prompt += f"\nInstructions: {instructions}"
    if examples:
        prompt += f"\nExamples: {', '.join(examples)}"
    return prompt

def send_request_to_openai(prompt: str, model: str = "nvidia/llama-3.1-nemotron-70b-instruct:free") -> Dict[str, Any]:
    """Envoyer une requête via OpenRouter au modèle de langage"""
    client = initialize_openai_client()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Tu es un assistant spécialisé dans l'analyse de données. Réponds uniquement en JSON ou en texte structuré."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=500,
        top_p=1
    )
    return response

def process_openai_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """Traiter la réponse du modèle de langage"""
    try:
        if response and 'choices' in response and len(response['choices']) > 0:
            content = response['choices'][0]['message']['content']
            return {
                "success": True,
                "data": content,
                "message": "Successfuly got response from OpenRouter"
            }
        else:
            return {
                "success": False,
                "data": None,
                "message": "No content found in response"
            }
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "message": str(e)
        }

def get_themes_from_config() -> list:
    """Récupérer la liste des thèmes disponibles depuis le fichier de config"""
    with open('data/themes.json', 'r', encoding="utf-8") as f:
        themes = json.load(f)
    return themes.get('themes', [])

def generate_summary(theme: str, scraped_data: str, 
                     model: str = "nvidia/llama-3.1-nemotron-70b-instruct:free",
                     temperature: float = 0.7) -> str:
    """
    Formate le prompt avec le thème et les données scrappées,
    puis appelle le LLM via OpenRouter pour générer un résumé en texte clair.
    """
    prompt = (
        f"Tu as analysé des articles pour le thème '{theme}'. Voici les informations extraites :\n\n"
        f"{scraped_data}\n\n"
        "À partir de ces informations, rédige un résumé clair, concis et structuré destiné à un utilisateur. "
        "Le résumé doit être exclusivement du texte explicatif, sans aucun formatage JSON, sans code, et sans autres balises."
        "Le résumé doit contenir les points saillants des articles, les tendances principales et un aperçu global des informations apprises."
        "Le résumer doit contenir les sources des articles analysés avec leurs liens."
    )
    client = initialize_openai_client()
    response = client.chat.completions.create(
         model=model,
         messages=[
             {"role": "system", "content": (
                 "Tu es un assistant expert en synthèse d'informations et en analyse de données. "
                 "Rédige un texte explicatif concis, clair et structuré en langage naturel."
             )},
             {"role": "user", "content": prompt}
         ],
         temperature=temperature,
    )
    return response.choices[0].message.content
