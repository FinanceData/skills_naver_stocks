
import requests
from bs4 import BeautifulSoup

def debug_industry():
    code = "005930"
    url = f"https://finance.naver.com/item/main.naver?code={code}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print(f"Fetching {url}...")
    res = requests.get(url, headers=headers)
    print(f"Status: {res.status_code}")
    
    if '동일업종' not in res.text:
        print("Text '동일업종' NOT found in response.")
        return
    
    print("Found '동일업종'. Printing context...")
    soup = BeautifulSoup(res.text, 'html.parser')
    
    tags = soup.find_all(string=lambda t: t and '동일업종 PER' in t)
    for t in tags:
         parent = t.parent
         print(f"Tag: {parent.name}")
         if parent.name == 'caption':
             table = parent.find_parent('table')
             if table:
                 print(f"Table HTML: {str(table)[:500]}") # Print start of table
                 # Try to find the value in this table
                 # Usually it's in <em> or <td>
                 ems = table.find_all('em')
                 for em in ems:
                     print(f"  Value candidate in table: {em.text}")
             
if __name__ == "__main__":
    debug_industry()
