
import requests
from bs4 import BeautifulSoup
import argparse
import sys

class FundamentalAnalyzer:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def get_data(self, code):
        url = f"https://finance.naver.com/item/main.naver?code={code}"
        try:
            print(f"Fetching data from {url}...")
            res = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(res.text, 'html.parser')
            
            data = {'code': code}
            
            # 1. Get Stock Name
            name_tag = soup.select_one('.wrap_company h2 a')
            if name_tag:
                data['name'] = name_tag.text.strip()
            else:
                data['name'] = code

            # 2. Cop Analysis (Financials)
            analysis_div = soup.select_one('div.section.cop_analysis')
            if analysis_div:
                rows = analysis_div.select('tr')
                targets = {
                    '영업이익': 'operating_income',
                    '부채비율': 'debt_ratio',
                    '유보율': 'reserve_ratio',
                    'PER(배)': 'PER',
                    'PBR(배)': 'PBR',
                    'ROE(지배주주)': 'ROE'
                }
                
                for row in rows:
                    th = row.select_one('th')
                    if not th: continue
                    text = th.text.strip()
                    
                    found_key = None
                    for t_key, d_key in targets.items():
                        if t_key in text:
                            found_key = d_key
                            break
                    
                    if found_key:
                        cols = row.select('td')
                        # Get latest valid value (annual or quarter)
                        # Naver table structure: Annual (4 cols) | Quarter (6 cols)
                        # We want the most recent actual data. 
                        # We iterate backwards through ALL columns.
                        for col in reversed(cols):
                            txt = col.text.strip().replace(',', '')
                            if txt and txt != '-' and txt != 'N/A':
                                try:
                                    val = float(txt)
                                    data[found_key] = val
                                    break
                                except: continue

            # 3. Industry PER
            # Validated Selector: table[summary="동일업종 PER 정보"] -> em
            
            industry_table = soup.find('table', summary='동일업종 PER 정보')
            if industry_table:
                ems = industry_table.find_all('em')
                for em in ems:
                    # The first number is usually the PER
                    txt = em.text.strip().replace(',', '')
                    try:
                        val = float(txt)
                        data['industry_per'] = val
                        break
                    except: continue
            
            return data
            
        except Exception as e:
            print(f"Error: {e}")
            return {}

    def analyze(self, data):
        if not data:
            print("데이터를 찾을 수 없습니다.")
            return

        print(f"\n[{data.get('code')}] {data.get('name')} 펀더멘털 신호등 분석")
        print("=" * 60)
        
        # 1. Stability (Debt Ratio)
        debt = data.get('debt_ratio')
        stability_color = "GRAY"
        stability_msg = "N/A"
        if debt is not None:
            if debt < 100:
                stability_color = "GREEN"
                stability_msg = "안정 (<100%)"
            elif debt <= 200:
                stability_color = "YELLOW"
                stability_msg = "주의 (100-200%)"
            else:
                stability_color = "RED"
                stability_msg = "위험 (>200%)"
        
        print(f"1. 안정성 (부채비율): {debt}% -> [{stability_color}] {stability_msg}")
        
        # 2. Earnings (Reserve Ratio Proxy)
        reserve = data.get('reserve_ratio')
        earnings_color = "GRAY"
        earnings_msg = "N/A"
        if reserve is not None:
            if reserve >= 500:
                earnings_color = "GREEN"
                earnings_msg = "이익체력 우수 (>500%)"
            elif reserve >= 200:
                earnings_color = "YELLOW"
                earnings_msg = "보통 (>200%)"
            else:
                earnings_color = "RED"
                earnings_msg = "이익체력 부족 (<200%)"
                
        print(f"2. 이익 체력 (유보율): {reserve}% -> [{earnings_color}] {earnings_msg}")
        print("   (참고: 이익잉여금 대신 유보율을 대용 지표로 사용)")
        
        # 3. Valuation (PER & PBR)
        per = data.get('PER', 999)
        pbr = data.get('PBR', 999)
        val_color = "GRAY"
        val_msg = "N/A"
        
        if pbr != 999 and per != 999:
             if pbr <= 1 and per <= 10:
                 val_color = "GREEN"
                 val_msg = "저평가 (PBR<1, PER<10)"
             elif pbr <= 1 or per <= 10:
                 val_color = "YELLOW"
                 val_msg = "판단 보류 (혼조세)"
             else:
                 val_color = "RED"
                 val_msg = "고평가 가능성"
        
        print(f"3. 가치 평가: PER {per}, PBR {pbr} -> [{val_color}] {val_msg}")
        
        # 4. Relative Valuation (Industry PER)
        ind_per = data.get('industry_per')
        rel_color = "GRAY"
        rel_msg = "N/A"
        
        if ind_per and per != 999:
            if per < ind_per:
                rel_color = "GREEN"
                rel_msg = f"업종 대비 저렴 ({ind_per})"
            else:
                rel_color = "RED"
                rel_msg = f"업종 대비 비쌈 ({ind_per})"
                
        print(f"4. 상대 가치: 업종 PER {ind_per} -> [{rel_color}] {rel_msg}")
        print("=" * 60)
        
        # Traffic Light Summary
        score = 0
        if stability_color == "GREEN": score += 1
        if earnings_color == "GREEN": score += 1
        if val_color == "GREEN": score += 1
        
        print(f"종합 점수: 3개 중 {score}개 항목 합격 (초록불)")
        if score == 3:
            print(">>> ⭐ 강력 매수 후보 (전 항목 초록불) ⭐")
        elif score == 0:
             print(">>> ⚠️ 고위험 경고 (초록불 없음) ⚠️")

def main():
    parser = argparse.ArgumentParser(description='Stock Fundamental Dashboard')
    parser.add_argument('--code', type=str, help='Stock Code (e.g. 005930)')
    args = parser.parse_args()
    
    code = args.code
    if not code:
        code = input("Enter Stock Code (e.g., 005930): ").strip()
        
    analyzer = FundamentalAnalyzer()
    data = analyzer.get_data(code)
    analyzer.analyze(data)

if __name__ == "__main__":
    main()
