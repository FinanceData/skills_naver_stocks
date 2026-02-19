# 주식 분석 및 투자 보조 스킬 모음 (Stock Analysis Skills)

이 프로젝트는 다양한 투자 전략과 분석 기법을 자동화한 파이썬 스킬 모음입니다.
네이버 금융 데이터를 기반으로 동작하며, 가치 투자, 기술적 분석, 계절성 테마 등 다양한 관점에서 종목을 발굴하고 검증합니다.

## 🛠️ 포함된 스킬 (Skills)

### 1. 급등주 포착 스캐너 (`stock_scanner`)
- **기능**: 거래량 급증(200% 이상) 및 주가 상승(3% 이상) 종목을 실시간으로 포착합니다.
- **실행**: `python3 skills/stock_scanner/scanner.py`

### 2. Uprise 전략 스캐너 (`stock_uprise`)
- **기능**: "적자 기업 제외" 및 "심리적 저점(안전마진)" 원칙을 적용하여, 리스크가 적은 눌림목 종목을 추천합니다.
- **실행**: `python3 skills/stock_uprise/scanner.py`

### 3. 펀더멘털 신호등 (`stock_fundamental`)
- **기능**: 기업의 재무 건전성(부채비율, 유보율), 가치평가(PER, PBR), 업종 대비 매력도를 "신호등(초록/빨강)"으로 시각화합니다.
- **실행**: `python3 skills/stock_fundamental/analysis.py --code 005930`

### 4. 증권사 추천 팩트체커 (`stock_recommand`)
- **기능**: 증권사 리포트의 "위험 키워드(기대, 전망 등)"를 감지하고, 추천 제외 종목의 은폐된 손실률을 추적합니다.
- **실행**: `python3 skills/stock_recommand/checker.py`

### 5. 계절/이벤트 테마 캘린더 (`stock_event`)
- **기능**: 매년 반복되는 계절적 테마(황사, 방산, 여름 등)를 1~3개월 전에 예측하고, 바닥권에 있는 대장주를 선취매하도록 알림을 줍니다.
- **실행**: `python3 skills/stock_event/planner.py` (특정 월 시뮬레이션: `--month 4`)

### 6. 기술적 지표 복합 크로스체크 (`stock_technical`)
- **기능**: MACD, 스토캐스틱, RSI, OBV 4가지 핵심 지표를 종합 분석하여 매수/매도 타이밍을 정밀하게 판별합니다.
- **실행**: `python3 skills/stock_technical/screener.py --code 005930`

## 🚀 설치 및 실행 방법

1. **필수 패키지 설치**
   ```bash
   pip install -r requirements.txt
   # 또는 각 스킬 디렉토리 내 requirements.txt 사용
   ```

2. **전체 스킬 테스트**
   각 스킬 폴더 내의 스크립트를 직접 실행하거나 `walkthrough.md`를 참조하세요.

## ⚠️ 주의사항
- 본 도구는 투자를 돕는 보조 도구일 뿐이며, 실제 투자의 책임은 사용자 본인에게 있습니다.
- 네이버 금융 웹페이지 구조 변경 시 일부 기능이 동작하지 않을 수 있습니다.
