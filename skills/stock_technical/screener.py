
import sys
import argparse
import requests
import pandas as pd
import xml.etree.ElementTree as ET
import datetime

class TechnicalScreener:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def fetch_ohlcv(self, code, count=500):
        """
        Fetch OHLCV from Naver XML API.
        URL: https://fchart.stock.naver.com/sise.nhn?symbol={code}&timeframe=day&count={count}&requestType=0
        """
        url = f"https://fchart.stock.naver.com/sise.nhn?symbol={code}&timeframe=day&count={count}&requestType=0"
        try:
            res = requests.get(url, headers=self.headers)
            root = ET.fromstring(res.text)
            
            items = root.findall('./chartdata/item')
            data = []
            for item in items:
                # Format: "20231025|58100|59100|57100|58100|17327734"
                # Date|Open|High|Low|Close|Volume
                parts = item.attrib['data'].split('|')
                if len(parts) < 6: continue
                
                data.append({
                    'date': pd.to_datetime(parts[0], format='%Y%m%d'),
                    'open': float(parts[1]),
                    'high': float(parts[2]),
                    'low': float(parts[3]),
                    'close': float(parts[4]),
                    'volume': float(parts[5])
                })
                
            df = pd.DataFrame(data)
            return df
        except Exception as e:
            print(f"Error fetching data for {code}: {e}")
            return pd.DataFrame()

    def calculate_indicators(self, df):
        if df.empty: return df
        
        # 1. MACD (12, 26, 9)
        # EMA(12)
        ema12 = df['close'].ewm(span=12, adjust=False).mean()
        # EMA(26)
        ema26 = df['close'].ewm(span=26, adjust=False).mean()
        # MACD Line
        df['MACD_Line'] = ema12 - ema26
        # Signal Line (9)
        df['MACD_Signal'] = df['MACD_Line'].ewm(span=9, adjust=False).mean()
        # Histogram
        df['MACD_Hist'] = df['MACD_Line'] - df['MACD_Signal']

        # 2. RSI (14)
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Note: Standard RSI uses Wilder's Smoothing, but SMA (rolling) is often used for simplicity.
        # Let's improve RSI calculation to Wilder's if possible, but rolling is acceptable for demo.
        # Better: use ewm(alpha=1/14) for Wilder approximation.
        gain = (delta.where(delta > 0, 0)).ewm(alpha=1/14, adjust=False).mean()
        loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/14, adjust=False).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # 3. Stochastic Slow (5, 3, 3)
        # Fast %K = (Current Close - Lowest Low) / (Highest High - Lowest Low) * 100
        # Lowest Low over 5 days
        low_min = df['low'].rolling(window=5).min()
        high_max = df['high'].rolling(window=5).max()
        
        df['Fast_K'] = ((df['close'] - low_min) / (high_max - low_min)) * 100
        # Slow %K = SMA(Fast %K, 3)
        df['Slow_K'] = df['Fast_K'].rolling(window=3).mean()
        # Slow %D = SMA(Slow %K, 3)
        df['Slow_D'] = df['Slow_K'].rolling(window=3).mean()

        # 4. OBV
        # If Close > Prev Close: +Volume
        # If Close < Prev Close: -Volume
        # Else: 0
        df['OBV'] = 0.0
        # Iterative calculation is slow in Python, utilize vectorized operations
        # Direction
        direction = df['close'].diff().apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))
        # Cumulative Sum
        df['OBV'] = (direction * df['volume']).cumsum()
        
        return df

    def analyze(self, df):
        if df.empty: return

        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        print("\n=== 기술적 지표 크로스체크 보고서 ===")
        print(f"기준일: {latest['date'].strftime('%Y-%m-%d')} | 종가: {int(latest['close'])}원")
        print("-" * 40)
        
        score = 0
        
        # 1. MACD
        macd_val = latest['MACD_Line']
        sig_val = latest['MACD_Signal']
        hist_val = latest['MACD_Hist']
        
        macd_status = "중립"
        if macd_val > sig_val:
            if macd_val > 0:
                macd_status = "상승 추세 (강세)"
                score += 1
            else:
                macd_status = "반등 시도 (약세 구간)"
        else:
            macd_status = "하락 추세"
            
        print(f"1. MACD (추세): {macd_val:.2f} / Sig {sig_val:.2f} -> [{macd_status}]")
        
        # 2. Stochastic Slow
        # Conditions: Cross above 20? Gold Cross?
        k = latest['Slow_K']
        d = latest['Slow_D']
        prev_k = prev['Slow_K']
        prev_d = prev['Slow_D']
        
        stoch_status = "관망"
        # Golden Cross Check (Recently crossed)
        if k > d and prev_k <= prev_d:
             if k < 40: # Low zone cross is best
                 stoch_status = "⭐ 골든크로스 (매수 타점)"
                 score += 2 # Strong signal
             else:
                 stoch_status = "골든크로스 (일반)"
                 score += 1
        elif k > d:
            if k > 80:
                stoch_status = "과매수 (조정 주의)"
            else:
                stoch_status = "상승 유지"
                score += 0.5
        elif k < d:
            stoch_status = "하락/조정 중"
            
        print(f"2. 스토캐스틱 (타점): K {k:.2f} / D {d:.2f} -> [{stoch_status}]")
        
        # 3. RSI
        rsi = latest['RSI']
        rsi_status = "중립"
        if rsi >= 70:
            rsi_status = "과매수 (매도 검토)"
            score -= 1
        elif rsi <= 30:
            rsi_status = "과매도 (반등 기대)"
            score += 0.5
        elif rsi > 50:
            rsi_status = "매수세 우위 (>50)"
            score += 1
        else:
            rsi_status = "매도세 우위 (<50)"
            
        print(f"3. RSI (강도): {rsi:.2f} -> [{rsi_status}]")
        
        # 4. OBV Trend
        # Check if OBV is rising over last 5-10 days
        obv_trend = df['OBV'].iloc[-10:]
        # Simple Logic: Is current OBV > 10-day MA of OBV?
        obv_ma = obv_trend.mean()
        obv_curr = latest['OBV']
        
        obv_status = "중립"
        if obv_curr > obv_ma:
            obv_status = "매집/상승 동반 (긍정)"
            score += 1
        else:
            obv_status = "거래량 이탈/약세"
            
        print(f"4. OBV (심리): {obv_status}")
        print("-" * 40)
        
        # Final Verdict
        print(f"✅ 종합 점수: {score}점")
        if score >= 4:
            print(">>> ⭐ 강력 매수 (Strong Buy) - 모든 신호가 긍정적입니다!")
        elif score >= 3:
            print(">>> 🟢 매수 (Buy) - 상승 추세가 확인되었습니다.")
        elif score >= 1.5:
            print(">>> 🟡 관망 (Wait) - 확실한 신호를 기다리세요.")
        else:
            print(">>> 🔴 매도/비중축소 (Sell) - 하락 리스크가 큽니다.")

def main():
    parser = argparse.ArgumentParser(description='Stock Technical Screener')
    parser.add_argument('--code', type=str, default='005930', help='Stock Code (default: Samsung Elec)')
    args = parser.parse_args()
    
    screener = TechnicalScreener()
    print(f"Fetching data for {args.code}...")
    
    df = screener.fetch_ohlcv(args.code)
    if df.empty:
        print("데이터를 가져올 수 없습니다.")
        return
        
    df = screener.calculate_indicators(df)
    screener.analyze(df)

if __name__ == "__main__":
    main()
