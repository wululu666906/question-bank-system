import requests
import re
from bs4 import BeautifulSoup

def test_ddg_search():
    query = "明朝是如何灭亡的 核心考点"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
    }
    url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
    
    try:
        print(f"Requesting URL: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            html = response.text
            # Use regex to extract snippet text from duckduckgo html
            snippets = re.findall(r'<a class="result__snippet[^>]+>(.*?)</a>', html, re.IGNORECASE | re.DOTALL)
            
            if snippets:
                # Clean up HTML tags in snippets
                cleaned_snippets = []
                for s in snippets[:5]:
                    clean_s = re.sub(r'<[^>]+>', '', s)
                    cleaned_snippets.append(clean_s.strip())
                
                print("Extracted Snippets:")
                for i, text in enumerate(cleaned_snippets):
                    print(f"{i+1}. {text}")
            else:
                print("No snippets found. DuckDuckGo might have blocked the request or changed HTML structure.")
        else:
            print(f"Error HTML: {response.text[:200]}")
    except Exception as e:
        print(f"Network Error: {e}")

if __name__ == "__main__":
    test_ddg_search()
