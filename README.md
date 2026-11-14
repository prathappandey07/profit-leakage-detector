# Small Business Profit Leakage Detector

**Python Hackathon (Skill Palaver) | KL Business School, KLU | Problem Statement #12**

## Problem
Small business owners often make sales but still lose money without knowing why. Profit quietly leaks through discounts, wastage, rising operating expenses and wrongly priced products. This project finds those leaks and shows what the owner can fix.

## Objectives
- Clean and combine sales and expense records
- Show where every rupee of sales goes (profit waterfall)
- Score each cost category by how much it leaks (% of gross sales)
- Flag loss-making products
- Generate plain-English insights automatically
- Simulate "what if" savings (discounts, wastage, prices)

## Features
| Feature | What it does |
|---|---|
| Data cleaning | Fixes data types, fills blanks, removes duplicates |
| Profit waterfall | Gross sales to net profit, step by step |
| Leakage score | Ranks leaks as High / Medium / Low risk |
| Product margins | Flags loss-making and thin-margin products |
| Auto insights | Code writes its own findings and alerts |
| What-if simulator | Sliders to test discount, wastage and price changes |

## Files
| File | Purpose |
|---|---|
| `analysis.py` | Core logic: cleaning, summaries, leakage score, insights, what-if |
| `charts.py` | Matplotlib charts |
| `run_analysis.py` | Command-line report and chart images |
| `app.py` | Streamlit dashboard |
| `generate_data.py` | Creates the sample dataset |
| `sales.csv`, `expenses.csv` | Sample data (Aug-Oct 2026) |

## How to run
```
pip install -r requirements.txt
python run_analysis.py
streamlit run app.py
```

## Python concepts used
pandas (`read_csv`, `groupby`, `pivot_table`, `fillna`, `drop_duplicates`, `to_numeric`), functions, dictionaries, loops, conditional logic, matplotlib charts, Streamlit.

## Sample result
The sample shop's net profit falls from Rs 34,332 (Aug) to a loss of Rs 6,253 (Oct). Discounts rise from 4% to 11.3% of sales and wastage rises sharply. Sugar and Egg Tray are sold below cost after discounts.

## Note
The dataset is sample data created for testing. Upload your own sales and expenses CSV in the dashboard to analyze a real business.

## Team
| Name | Roll No. |
|---|---|
| DEVALALA MITHUL | 2600560002 |
| SAI PRATHAP PANDEY | 2600560050 |
| PATAN AMEER KHAN | 2600560287 |
| BOTTA ANISH KUMAR | 2600560521 |
