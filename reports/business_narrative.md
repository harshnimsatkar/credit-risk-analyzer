narrative = """# Credit Card Fraud Risk Analysis — Business Narrative
**Author:** Harsh Nimsatkar  
**Dataset:** 1.85M transactions (fraudTrain + fraudTest), 284K transactions (creditcard.csv)  
**Tools:** Python, SQL (SQLite), Pandas, Matplotlib

---

## Executive Summary

Analysis of 1,852,394 credit card transactions revealed that combining four rule-based 
signals — time of day, merchant category, transaction velocity, and amount threshold — 
creates a risk scoring system that identifies CRITICAL-tier transactions with a 66.5% 
fraud rate, representing a 1,750x improvement over LOW-tier transactions (0.038%).

---

## Key Finding 1 — Time-Based Risk (SQL: 02)

Fraud rate spikes dramatically during late night hours:

| Hour Window | Fraud Rate |
|-------------|-----------|
| 10pm – 3am  | 1.3% – 2.6% |
| 4am – 9pm   | 0.086% – 0.133% |

**Business Impact:** Transactions between 10pm–3am are 25x more likely to be fraudulent.
Applying a time-based alert rule to this 6-hour window would flag 5,689 confirmed fraud 
cases — representing 58.9% of all fraud in the dataset.

---

## Key Finding 2 — Merchant Category Risk (SQL: 03)

Three merchant categories drive majority of fraud losses:

| Category     | Fraud Rate | Total Fraud Loss |
|--------------|-----------|-----------------|
| shopping_net | 1.593%    | $2.21M          |
| misc_net     | 1.304%    | $0.94M          |
| grocery_pos  | 1.265%    | $0.70M          |

**Business Impact:** These 3 categories account for 58% of all fraud cases. Enhanced 
monitoring on online shopping and miscellaneous net transactions alone would cover 
$3.15M in fraud losses.

---

## Key Finding 3 — Velocity-Based Detection (SQL: 04)

Cards making 5+ transactions within 60 minutes show extreme fraud concentration:

| Velocity Flag   | Fraud Rate | Multiplier vs Normal |
|-----------------|-----------|---------------------|
| HIGH VELOCITY   | 15.930%   | 37x                 |
| MEDIUM VELOCITY | 3.247%    | 8x                  |
| NORMAL          | 0.427%    | baseline            |

**Business Impact:** A simple velocity rule (5 txns / 60 min) flags transactions that 
are 37x more likely to be fraudulent. Average fraud amount in HIGH VELOCITY group 
is $152.89 — suggesting rapid card-testing behavior before large purchases.

---

## Key Finding 4 — Combined Risk Scoring (SQL: 05)

Combining all 4 signals into a composite risk tier:

| Risk Tier | Transactions | Fraud Cases | Fraud Rate | Avg Amount |
|-----------|-------------|-------------|-----------|------------|
| CRITICAL  | 4,414       | 2,936       | 66.516%   | $907.61    |
| HIGH      | 126,333     | 3,473       | 2.749%    | $142.32    |
| MEDIUM    | 597,889     | 2,811       | 0.470%    | $79.13     |
| LOW       | 1,123,758   | 431         | 0.038%    | $53.83     |

**Business Impact:** Flagging only CRITICAL-tier transactions for manual review would:
- Catch **2,936 fraud cases** (30.4% of all fraud)
- Review only **4,414 transactions** (0.24% of total volume)
- Achieve **66.5% precision** — 2 in 3 flagged transactions are genuinely fraudulent
- Average fraud transaction in CRITICAL tier is **$907.61** — highest financial risk

---

## Recommendation

A three-layer rule engine combining time window + merchant category + velocity signals 
achieves strong fraud detection with minimal disruption to legitimate customers:

1. **Immediate block:** CRITICAL tier (3+ signals) — automatic hold for review
2. **Soft alert:** HIGH tier (2 signals) — step-up authentication (OTP/biometric)
3. **Monitor only:** MEDIUM tier (1 signal) — flag for batch review
4. **Pass through:** LOW tier (0 signals) — no friction added

This approach protects **$4.86M in potential fraud losses** while adding friction to 
only **0.24% of legitimate transaction volume**.
"""

with open("../reports/business_narrative.md", "w") as f:
    f.write(narrative)

print("business_narrative.md saved!")