---
name: recommand
description: A fact checker tool for brokerage recommendations, ranking brokers, and tracking excluded stocks.
---

# Recommendation Fact Checker (증권사 추천 신뢰도 검증기)

This skill analyzes and scores brokerage stock recommendations to filter "True" insights from marketing noise.
It checks for vague/risky keywords and ranks brokerages based on their recommendation history.

## Features

1.  **Risk Keyword Warning (위험 키워드 경고)**:
    -   Scans report titles for vague future promises (e.g., "기대", "전망", "턴어라운드", "회복 예상").
    -   Flags reports as "Caution" if keywords exceed a threshold.

2.  **Brokerage Ranking (증권사 실력 랭킹)**:
    -   Calculates the average return of "Buy" recommendations for each brokerage over the scanned period.
    -   Ranks brokerages: 🥇 1st Place (Highest ROI), 🥈 2nd Place, 🥉 3rd Place.

3.  **Excluded Stock Watch (추천 제외 종목 추적)**:
    -   Tracks stocks that disappear from recommendation lists (needs persistent history run daily).
    -   For first run: Simulates "tracking started" or shows recent drop-offs if detectable.

## Usage

Run the checker:

```bash
python3 skills/recommand/checker.py
```

Or check specific brokerage performance (if implemented):
```bash
python3 skills/recommand/checker.py --broker "KB증권"
```
