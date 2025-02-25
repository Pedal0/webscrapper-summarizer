from bs4 import BeautifulSoup
import requests
import logging
from typing import Dict, Any, Optional

def fetch_page(url: str, headers: Dict[str, str] = None, timeout: int = 10) -> Optional[str]:
    """
    Fetch webpage content from a given URL.
    Args:
        url (str): URL to fetch
        headers (Dict[str, str]): Optional headers for the request
        timeout (int): Request timeout
        
    Returns:
        Optional[str]: Webpage content as string or None if error occurs
    """
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status() 
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching {url}: {str(e)}")
        return None

def parse_html(html_content: str) -> Optional[BeautifulSoup]:
    """
    Parse HTML content using BeautifulSoup.
    Args:
        html_content (str): HTML content as string
        
    Returns:
        Optional[BeautifulSoup]: Parsed HTML content or None if parsing fails
    """
    try:
        return BeautifulSoup(html_content, 'html.parser')
    except Exception as e:
        logging.error(f"Error parsing HTML: {str(e)}")
        return None

def extract_info_by_theme(soup: BeautifulSoup, theme_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract information from parsed HTML based on theme configuration.
    Args:
        soup (BeautifulSoup): Parsed HTML content
        theme_config (Dict[str, Any]): Configuration for the theme, 
                                   including selectors and patterns
        
    Returns:
        Dict[str, Any]: Extracted information according to theme config
    """
    extracted_data = {}
    
    if 'selectors' in theme_config:
        for selector, field in theme_config['selectors'].items():
            elements = soup.select(selector)
            if elements:
                extracted_data[field] = [e.get_text(strip=True) for e in elements]
    
    if 'patterns' in theme_config:
        for pattern in theme_config['patterns']:
            pass
            
    return extracted_data

def clean_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clean and normalize extracted data.
    Args:
        data (Dict[str, Any]): Raw extracted data
        
    Returns:
        Dict[str, Any]: Cleaned and normalized data
    """
    cleaned_data = {}
    for key, value in data.items():
        if isinstance(value, str):
            cleaned_value = value.strip()
            cleaned_data[key] = cleaned_value
        elif isinstance(value, list):
            cleaned_data[key] = [item.strip() for item in value]
    return cleaned_data

def handle_errors(func):
    """
    Decorator to handle exceptions during scraping operations.
    """
    def wrapper(*args, **kwargs):
        try:
            return {'success': True, 'data': func(*args, **kwargs)}
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {str(e)}")
            return {'success': False, 'error': str(e)}
    return wrapper

def validate_url(url: str) -> bool:
    """
    Validate if the URL is valid.
    Args:
        url (str): URL to validate
        
    Returns:
        bool: True if URL is valid, False otherwise
    """
    try:
        result = requests.head(url, timeout=5)
        return result.status_code < 400
    except Exception:
        return False

def create_json_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a standardized JSON response.
    Args:
        data (Dict[str, Any]): Raw data to format
        
    Returns:
        Dict[str, Any]: Standardized JSON response
    """
    return {
        "title": data.get("title", ""),
        "content": data.get("content", []),
        "timestamp": data.get("timestamp", ""),
        "success": data.get("success", False),
        "error": data.get("error", "")
    }