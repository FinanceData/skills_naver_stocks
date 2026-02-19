
import requests
from bs4 import BeautifulSoup
import urllib.parse

def search_theme(query):
    # Naver Finance doesn't have a direct "Search Theme" API easily accessible.
    # But sise/theme.naver lists all themes.
    # We can fetch all pages (1-7) and search for the name.
    
    base_url = "https://finance.naver.com/sise/theme.naver"
    print(f"Searching for theme '{query}' across all pages...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    
    for page in range(1, 8):
        url = f"{base_url}?&page={page}"
        try:
            res = requests.get(url, headers=headers)
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # Table: type_1 theme
            links = soup.select('table.type_1 .col_type1 a')
            
            for link in links:
                name = link.text.strip()
                if query in name:
                    href = link['href']
                    # href: /sise/sise_group_detail.naver?type=theme&no=144
                    theme_id = href.split('no=')[-1]
                    print(f"Found: '{name}' -> ID: {theme_id}")
                    
        except Exception as e:
            print(f"Error on page {page}: {e}")

if __name__ == "__main__":
    queries = ["육계", "닭고기", "건설기계", "여름", "냉방", "전력", "교육", "게임", "엔터", "미세먼지", "방위"]
    for q in queries:
        search_theme(q)
