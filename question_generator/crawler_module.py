import logging
import re
from curl_cffi import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

def fetch_and_clean_url(url: str, timeout: int = 15) -> str:
    """
    Fetch the content of a URL using curl_cffi to bypass basic anti-scraping mechanisms,
    then clean the HTML to extract only the main text content.
    """
    logger.info(f"Fetching URL: {url}")
    try:
        # Use impersonate to simulate a real browser fingerprint (e.g., chrome110)
        # This helps in bypassing Cloudflare and other basic protections.
        response = requests.get(
            url, 
            impersonate="chrome110", 
            timeout=timeout,
            headers={"Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6"}
        )
        response.raise_for_status()
        
        # Parse HTML using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script, style, nav, footer, header, aside elements
        for element in soup(["script", "style", "nav", "footer", "header", "aside", "noscript", "meta"]):
            element.decompose()
            
        # Extract text
        text = soup.get_text(separator=' ', strip=True)
        
        # Basic cleanup: remove multiple spaces and newlines
        text = re.sub(r'\s+', ' ', text).strip()
        
        logger.info(f"Successfully fetched and cleaned {len(text)} characters from {url}")
        return text
    except Exception as e:
        logger.error(f"Error fetching URL {url}: {e}")
        return ""

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Test with a Wikipedia page that usually works well and might block simple requests
    content = fetch_and_clean_url("https://zh.wikipedia.org/wiki/%E7%89%9B%E9%A1%BF%E8%BF%90%E5%8A%A8%E5%AE%9A%E5%BE%8B")
    print(f"Content length: {len(content)}")
    print(content[:500] + "...")
