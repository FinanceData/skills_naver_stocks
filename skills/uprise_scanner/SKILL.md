---
name: uprise_scanner
description: A scanner to identify "True Soaring Stocks" and "Pullback" opportunities with fundamental analysis.
---

# Uprise Scanner (진정한 급등주 및 눌림목 포착 스캐너)

This skill implements a stock scanner that filters for high-quality soaring stocks and identifies potential buy entry points during pullbacks.

## Features

1.  **Rising Stock Detection**:
    *   Finds stocks with >3% daily price increase.
    *   Filters for >200% volume surge compared to 20-day average.

2.  **Safety Checks**:
    *   **Psychological Low Point**: Ensures price is within the lower 30% of 3-year range.
    *   **Financial Health**: Excludes companies with deficits (Operating Income < 0) or poor fundamentals (PER < 0, PBR < 0, ROE < 0).

3.  **Fundamental Analysis (Traffic Light)**:
    *   Evaluates Stability (Debt Ratio), Earnings (Reserve Ratio), and Valuation (PER/PBR) to verify "True" value.

4.  **Pullback & Buy Signal**:
    *   Monitors for pullback entry signals (e.g., Stochastic Slow Golden Cross, Resistance Breakout).
    *   Simulates a "Smartphone Alert" when a buy signal is detected.

## Usage

Run the scanner directly:

```bash
python3 skills/uprise_scanner/scanner.py
```
