
import requests
from bs4 import BeautifulSoup

def debug_wisereport():
    code = "005930"
    
    # 1. Balance Sheet for Retained Earnings (c1010003.aspx)
    url_bs = f"https://navercomp.wisereport.co.kr/v2/company/c1010003.aspx?cmp_cd={code}"
    
    # 2. Investment Indicators for PCR, PSR, EV/EBITDA (c1010004.aspx)
    url_ii = f"https://navercomp.wisereport.co.kr/v2/company/c1010004.aspx?cmp_cd={code}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
    
    print(f"Fetching Balance Sheet from {url_bs}...")
    res_bs = requests.get(url_bs, headers=headers)
    print(f"Status: {res_bs.status_code}")
    print(f"Preview: {res_bs.text[:1000]}")
    soup_bs = BeautifulSoup(res_bs.text, 'html.parser')
    
    targets_bs = ['자본총계', '부채총계', '이익잉여금']
    found_bs = {}
    
    # Table usually has headers. Rows might be 'th' or 'td'
    # WiseReport tables are often in div.section > table
    
    rows = soup_bs.select('tr')
    for row in rows:
        cells = row.select('th, td') # Both header and data cells might contain the label? No, usually label in first cell.
        if not cells: continue
        label = cells[0].text.strip()
        
        for t in targets_bs:
            if t in label:
                # Found the row. Get the most recent value.
                # Usually columns are [Annual... | Quarter...] or just recent annual.
                # Let's grab all values and pick the last valid one.
                vals = [c.text.strip().replace(',', '') for c in cells[1:]]
                valid_vals = []
                for v in vals:
                    try:
                        f = float(v)
                        valid_vals.append(f)
                    except: pass
                if valid_vals:
                    found_bs[t] = valid_vals[-1] # Most recent
                    print(f"  -> Found {t}: {valid_vals[-1]}")

    print("\nFetching Investment Indicators from {url_ii}...")
    res_ii = requests.get(url_ii, headers=headers)
    print(f"Status: {res_ii.status_code}")
    soup_ii = BeautifulSoup(res_ii.text, 'html.parser')
    
    targets_ii = ['PCR', 'PSR', 'EV/EBITDA']
    found_ii = {}
    
    rows = soup_ii.select('tr')
    for row in rows:
        cells = row.select('th, td')
        if not cells: continue
        label = cells[0].text.strip()
        
        # Exact match or contained?
        found_key = None
        for t in targets_ii:
            if t ==Label or t in label: # "PCR(배)" etc.
                found_key = t
                break
        
        if found_key:
             vals = [c.text.strip().replace(',', '') for c in cells[1:]]
             valid_vals = []
             for v in vals:
                try:
                    f = float(v)
                    valid_vals.append(f)
                except: pass
             if valid_vals:
                found_ii[found_key] = valid_vals[-1]
                print(f"  -> Found {found_key}: {valid_vals[-1]}")

if __name__ == "__main__":
    debug_wisereport()
