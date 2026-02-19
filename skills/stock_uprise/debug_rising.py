
import requests
from bs4 import BeautifulSoup

def debug_rising():
    url = "https://finance.naver.com/sise/sise_rise.naver"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print(f"Fetching {url}...")
    res = requests.get(url, headers=headers)
    print(f"Status: {res.status_code}")
    
    soup = BeautifulSoup(res.text, 'html.parser')
    
    table = soup.select_one('table.type_2')
    if not table:
        print("Table 'table.type_2' NOT found!")
        return
    
    print("Table found. checking rows...")
    rows = table.find_all('tr')
    print(f"Total rows: {len(rows)}")
    
    count = 0
    for i, row in enumerate(rows):
        cols = row.find_all('td')
        if len(cols) < 10: 
            # Separator rows or headers often have fewer columns
            continue
            
        try:
            name_tag = cols[1].find('a')
            if not name_tag: continue
            name = name_tag.text.strip()
            
            price_txt = cols[2].text.strip().replace(',', '')
            diff_rate_txt = cols[4].text.strip().replace('%', '').replace('+', '').replace('-', '')
            volume_txt = cols[6].text.strip().replace(',', '')
            
            print(f"Row {i}: {name} | Price: {price_txt} | Rate: {diff_rate_txt} | Vol: {volume_txt}")
            count += 1
            if count >= 5: break
        except Exception as e:
            print(f"Row {i} parse error: {e}")

if __name__ == "__main__":
    debug_rising()
