---
name: stock_technical
description: A comprehensive technical analysis tool using MACD, Stochastic Slow, RSI, and OBV for cross-verification.
---

# Technical Indicator 4-Type Cross-Check (기술적 지표 복합 크로스체크)

This skill analyzes 4 key technical indicators to identify precise entry points and avoid false signals.
It calculates MACD, Stochastic Slow, RSI, and OBV from daily price data.

## Features

1.  **MACD (Trend)**:
    -   Identifying Trend Direction (MACD Line > Signal Line & Above 0).
    -   "Is the trend rising?"

2.  **Stochastic Slow (Entry Point)**:
    -   Detecting oversold reversals (Golden Cross below 20).
    -   "Is this the exact timing to buy?"

3.  **RSI (Strength)**:
    -   Measuring momentum (Above 50 = Strong Trend).
    -   "Is the trend strong enough?"

4.  **OBV (Volume Confirmation)**:
    -   Validating price moves with volume (Rising OBV).
    -   "Is smart money (volume) supporting the price?"

## Usage

Run the screener for a specific stock:

```bash
python3 skills/stock_technical/screener.py --code 005930
```
