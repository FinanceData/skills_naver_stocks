import requests
from bs4 import BeautifulSoup

def debug_main_page():
    code = "005930" # Samsung Electronics
    url = f"https://finance.naver.com/item/main.naver?code={code}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print(f"Fetching {url}...")
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # Check 'cop_analysis' table
    analysis_div = soup.select_one('div.section.cop_analysis')
    if not analysis_div:
        print("Analysis div not found!")
        return
        
    print("Found Analysis Table. Checking rows...")
    rows = analysis_div.select('tr')
    
    targets = ['영업이익', 'ROE', 'PER', 'PBR', '부채비율', '유보율']
    
    found_data = {}
    
    for row in rows:
        th = row.select_one('th')
        if not th: continue
        text = th.text.strip()
        
        for t in targets:
            if t in text:
                print(f"  -> Found Row: {text}")
                # Get last value
                cols = row.select('td')
                vals = [c.text.strip() for c in cols]
                print(f"     Values: {vals}")
                found_data[t] = True
                
    print("\nMissing Targets:", [t for t in targets if t not in found_data])

if __name__ == "__main__":
    debug_main_page()
