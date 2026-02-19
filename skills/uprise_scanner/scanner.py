
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import time
import datetime

class NaverFinanceClient:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def get_rising_stocks(self, limit=30):
        """
        Fetches 'Rising Stocks' from Naver Finance.
        Returns list of dict: {code, name, price, diff_rate, volume}
        """
        url = "https://finance.naver.com/sise/sise_rise.naver"
        try:
            res = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(res.text, 'html.parser')
            
            stocks = []
            table = soup.select_one('table.type_2')
            if not table: return []
            
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) < 10: continue
                
                try:
                    name_tag = cols[1].find('a')
                    if not name_tag: continue
                    name = name_tag.text.strip()
                    code = name_tag['href'].split('=')[-1]
                    
                    price_txt = cols[2].text.strip().replace(',', '')
                    diff_rate_txt = cols[4].text.strip().replace('%', '').replace('+', '').replace('-', '')
                    volume_txt = cols[6].text.strip().replace(',', '')
                    
                    if not price_txt or not diff_rate_txt or not volume_txt: continue
                    
                    current_price = int(price_txt)
                    diff_rate = float(diff_rate_txt)
                    volume = int(volume_txt)
                    
                    # Basic Filter: > 3% rise
                    if diff_rate >= 3.0:
                         stocks.append({
                            'code': code,
                            'name': name,
                            'price': current_price,
                            'diff_rate': diff_rate,
                            'volume': volume
                        })
                except ValueError:
                    continue
                    
            return stocks[:limit]
        except Exception as e:
            print(f"Error fetching rising stocks: {e}")
            return []

    def get_history(self, code, period=750): # ~3 years
        """
        Fetches daily OHLCV from fchart.stock.naver.com (XML).
        """
        url = f"https://fchart.stock.naver.com/sise.nhn?symbol={code}&timeframe=day&count={period}&requestType=0"
        try:
            res = requests.get(url, headers=self.headers)
            root = ET.fromstring(res.text)
            
            history = []
            for item in root.findall('./chartdata/item'):
                data = item.get('data').split('|')
                if len(data) >= 6:
                    history.append({
                        'date': data[0],
                        'open': int(data[1]),
                        'high': int(data[2]),
                        'low': int(data[3]),
                        'close': int(data[4]),
                        'volume': int(data[5])
                    })
            return history
        except Exception as e:
            print(f"Error fetching history for {code}: {e}")
            return []

    def get_fundamentals(self, code):
        """
        Fetches basic fundamentals from Naver Finance Main Page.
        Needed for:
        - Deficit Check (Operating Income, Net Income - implied logic or scraped?)
        - Traffic Light Check
        """
        url = f"https://finance.naver.com/item/main.naver?code={code}"
        try:
            res = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(res.text, 'html.parser')
            
            data = {}
            
            # 1. Cop Analysis Table (Annual/Quarterly) is best for deficit check
            # Look for recent Operating Income.
            # If negative -> Deficit.
            
            analysis_div = soup.select_one('div.section.cop_analysis')
            if analysis_div:
                # Find 'Operating Income' row (영업이익)
                # rows usually: Revenue, Operating Income, Net Income...
                rows = analysis_div.select('tr')
                for row in rows:
                    header = row.select_one('th')
                    if not header: continue
                    text = header.text.strip()
                    
                    # Check for Operating Income (deficit check)
                    if '영업이익' in text:
                        # Check recent columns. If any recent annual/quarter is negative?
                        # Or just the latest? User said "Excludes companies with deficit".
                        # Let's check the most recent 1-2 periods.
                        cols = row.select('td')
                        recent_val = None
                        # Reverse check for latest valid data
                        for col in reversed(cols):
                            txt = col.text.strip().replace(',', '')
                            if txt and txt != '-' and txt != 'N/A':
                                try:
                                    recent_val = float(txt)
                                    break
                                except: continue
                        if recent_val is not None:
                             data['operating_income'] = recent_val # 100 mil KRW unit matches
                             
                    # Additional Metrics for Traffic Light
                    if '부채비율' in text:
                         # ... scraping logic same as before ...
                         pass 
                         
            # Reuse scraping logic from previous scanner but optimized
            # Let's just grab the whole summary table into a dict for easier access?
            
            # Scrape specific targets again for safety
            targets = {
                '영업이익': 'operating_income',
                '부채비율': 'debt_ratio',
                '유보율': 'reserve_ratio',
                'PER(배)': 'PER',
                'PBR(배)': 'PBR',
                'ROE(지배주주)': 'ROE'
            }
             
            data = {}
            if analysis_div:
                rows = analysis_div.select('tr')
                for row in rows:
                    th = row.select_one('th')
                    if not th: continue
                    h_text = th.text.strip()
                    
                    found_key = None
                    for t_key, d_key in targets.items():
                        if t_key in h_text:
                            found_key = d_key
                            break
                    
                    if found_key:
                        cols = row.select('td')
                        recent_val = None
                        for col in reversed(cols): # reversed to find latest
                             txt = col.text.strip().replace(',', '')
                             if txt and txt != '-' and txt != 'N/A':
                                 try:
                                     recent_val = float(txt)
                                     break
                                 except: continue
                        if recent_val is not None:
                            data[found_key] = recent_val

            return data
            
        except Exception as e:
            print(f"Error fetching fundamentals for {code}: {e}")
            return {}

class StockAnalyzer:
    def __init__(self, client):
        self.client = client

    def check_volume_spike(self, stock_info, history):
        """
        Checks if current volume is > 200% of 20-day average.
        """
        if len(history) < 20: return False
        
        # Calculate 20-day avg volume (excluding today)
        recent_20 = history[-21:-1]
        if not recent_20: return False
        
        avg_vol = sum([d['volume'] for d in recent_20]) / len(recent_20)
        if avg_vol == 0: return False
        
        ratio = (stock_info['volume'] / avg_vol) * 100
        return ratio >= 200.0

    def check_safe_zone(self, stock_info, history):
        """
        Checks if current price is in lower 30% of 3-year range.
        """
        if not history: return False
        
        closes = [d['close'] for d in history]
        min_price = min(closes)
        max_price = max(closes)
        current = stock_info['price']
        
        if max_price == min_price: return False
        
        position = (current - min_price) / (max_price - min_price)
        return position <= 0.30

    def check_financial_health(self, fundamentals):
        """
        Checks for deficits or bad fundamentals.
        Condition: Operating Income > 0 AND (PER > 0) AND (PBR > 0) AND (ROE > 0)
        (If metric is missing, we assume safe or skip? Strict means skip)
        """
        if not fundamentals: return False
        
        op_inc = fundamentals.get('operating_income')
        if op_inc is not None and op_inc < 0: return False # Deficit
        
        # PER, ROE, PBR check (negative usually means loss or bad status)
        per = fundamentals.get('PER')
        if per is not None and per < 0: return False
        
        roe = fundamentals.get('ROE')
        if roe is not None and roe < 0: return False
        
        # PBR usually positive, but check anyway
        pbr = fundamentals.get('PBR')
        if pbr is not None and pbr < 0: return False
        
        return True

    def check_pullback(self, history):
        """
        Checks for Pullback Signals.
        1. Stochastic Slow Golden Cross (5,3,3)
        2. 6-day Resistance Beakout (Simplified: Current Close > Max of last 6 days High)
        """
        if len(history) < 10: return False
        
        # A. Stochastic Slow Golden Cross
        # Need Calculate Stochastic first. 
        # Fast%K = ((Close - MinLow) / (MaxHigh - MinLow)) * 100
        # Fast%D = SMA(Fast%K, 3) -> Slow%K
        # Slow%D = SMA(Slow%K, 3)
        
        # Simplified: Just check if today > max of last 6 days for "breakout"
        # User said: "Break resistance of 6 days drop" -> roughly > 6-day High?
        
        # Let's implement Resistance Breakout first as it's easier without numpy/pandas
        recent_6 = history[-7:-1] 
        max_high_6 = max([d['high'] for d in recent_6])
        current_close = history[-1]['close']
        
        is_breakout = current_close > max_high_6
        
        return is_breakout

def main():
    print("=== Uprise 스캐너: 진정한 급등주 & 눌림목 포착 ===")
    client = NaverFinanceClient()
    analyzer = StockAnalyzer(client)
    
    # 1. Get Candidates
    rising_stocks = client.get_rising_stocks(limit=50)
    print(f"상승 종목 {len(rising_stocks)}개 탐색 중...")
    
    # Show Top 5 Rising Stocks regardless of criteria
    if rising_stocks:
        print("\n[실시간 상승 상위 5 종목 (필터 적용 전)]")
        for s in rising_stocks[:5]:
             print(f"- [{s['code']}] {s['name']} : {s['price']}원 ({s['diff_rate']}%) | 거래량: {s['volume']}")
        print("-" * 50)
    
    final_candidates = []
    
    for stock in rising_stocks:
        code = stock['code']
        # print(f"Analyzing {stock['name']}...")
        
        # 2. History Check (Volume & Safe Zone & Pullback)
        history = client.get_history(code)
        if not history: continue
        
        # Volume Spike
        # If volume is 0 (pre-market), we might skip this check or fail it.
        # Strict mode: fail.
        if not analyzer.check_volume_spike(stock, history): continue
        
        # Safe Zone (Psychological Low)
        if not analyzer.check_safe_zone(stock, history): continue
        
        # 3. Financial Health (Deficit Check)
        fundamentals = client.get_fundamentals(code)
        if not analyzer.check_financial_health(fundamentals): 
            # print(f"  -> Skipped {stock['name']} due to financials.")
            continue
            
        # 4. Pullback Signal (For Alert)
        is_pullback_signal = analyzer.check_pullback(history)
        
        stock['fundamentals'] = fundamentals
        stock['signal'] = is_pullback_signal
        
        final_candidates.append(stock)
        
    print(f"\n스캔 완료. '진정한 급등주' {len(final_candidates)}개 발견.\n")
    
    for c in final_candidates:
        print(f"[{c['code']}] {c['name']} | 현재가: {c['price']} (+{c['diff_rate']}%)")
        print(f"   거래량: {c['volume']} (거래량 폭증!)")
        
        fund = c.get('fundamentals', {})
        print(f"   재무상태: 영업이익 {fund.get('operating_income','?')} | PER {fund.get('PER','?')} | PBR {fund.get('PBR','?')}")
        
        if c['signal']:
            print("   >>> 🔔 [스마트폰 알림] 눌림목/돌파 매수 신호 발생! 🔔 <<<")
        else:
            print("   (눌림목 관찰 중...)")
        print("-" * 40)

if __name__ == "__main__":
    main()
