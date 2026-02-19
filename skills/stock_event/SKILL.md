---
name: stock_event
description: A tool to recommend seasonal/recurring event themes (preemption strategy).
---

# Stock Event Calendar (계절/이벤트 테마주 캘린더)

This skill helps investors predict recurring market themes (e.g., weather, annual drills) 1-3 months in advance and recommends stocks that are at a "psychological low" (safe entry point).

## Features

1.  **Annual Theme Calendar (테마 발생 시기 예측)**:
    -   Predicts upcoming themes based on past data (e.g., Yellow Dust in Spring, Heating in Winter).
    -   Provides a 3-month lookahead view.

2.  **Preemption Alert (선취매 알림)**:
    -   Identifies leader stocks for the upcoming theme.
    -   Recommends buying ONLY if the stock is fundamentally sound (no deficit) and at a low price point (bottom 30% of 3-year range).
    -   "Buy the rumor, sell the news" implementation.

## Usage

Run the planner:

```bash
python3 skills/stock_event/planner.py
```

Or target a specific month:
```bash
python3 skills/stock_event/planner.py --month 4
```
