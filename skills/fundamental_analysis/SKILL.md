---
name: fundamental_analysis
description: A dashboard that visualizes stock fundamentals as a "Traffic Light" system (Stability, Earnings, Valuation).
---

# Fundamental Analysis (가치투자 펀더멘털 신호등)

This skill provides a clear, "Traffic Light" style assessment of a company's financial health and valuation, allowing investors to quickly identify high-quality, undervalued stocks without deep accounting knowledge.

## Features

1.  **Stability (안정성)**:
    -   Checks if Debt Ratio < 100% (Green Light).
    -   Warns if Debt Ratio > 200% (Red Light).

2.  **Earnings Strength (이익 체력)**:
    -   Uses **Reserve Ratio** (유보율) as a proxy for Retained Earnings stability.
    -   Reserve Ratio > 500% (Green Light) indicates strong accumulated earnings.

3.  **Valuation (가치 평가)**:
    -   Combines PER and PBR.
    -   Green Light: PBR < 1 AND PER < 10 (Undervalued).
    -   Red Light: PBR > 1 AND PER > 10 (Overvalued).

4.  **Relative Valuation**:
    -   Compares PER with Industry Average PER.

## Usage

Run the analysis for a specific stock code:

```bash
python3 skills/fundamental_analysis/analysis.py --code 005930
```

Or run interactively:
```bash
python3 skills/fundamental_analysis/analysis.py
```
