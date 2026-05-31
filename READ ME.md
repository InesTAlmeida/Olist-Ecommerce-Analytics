# Olist E-Commerce Analytics Dashboard

An interactive, data analytics project built to explore, visualize and extract strategic business insights from Brazil's largest department store marketplace (Olist). 

This repository contains the interactive Streamlit Web Application designed to bridge between static Exploratory Data Analysis (EDA) and dynamic business intelligence.

**Live Project Link:** [Explore the Interactive Dashboard Live](METER_AQUI_O_LINK_DO_STREAMLIT)  
**Kaggle Notebook:** [View the Complete End-to-End EDA]https://www.kaggle.com/datasets/quietluna/brazilian-e-commerce-dataset-by-olist

---

## Key Business Insights Captured

The application is tailored around core data discoveries extracted during exploration:

* **Extreme Seasonality & The Black Friday Phenomenon:** The platform demonstrated aggressive growth throughout 2017, culminating in an unmatched revenue spike in late November. The dashboard highlights this critical historical milestone, proving Black Friday as Olist's primary annual growth catalyst.
* **Weekly & Daily Waves:** Transaction volumes are heavily concentrated early in the week (Mondays and Tuesdays) and follow a strict daily double-peak distribution pattern (**11:00–14:00** and **20:00–22:00**).
* **The Volume vs. Value Paradox:** Core retail categories show distinct behavioral patterns. High-velocity sectors like `bed_bath_table` capture market share via pure transaction volume but maintain low average pricing, whereas premium clusters like `watches_gifts` act as strong revenue anchors due to a high Average Order Value (AOV).

---

## Tech Stack & Architecture

* **Language:** Python 3.x
* **Framework:** Streamlit (UI & Reactive State Management)
* **Data Processing:** Pandas & NumPy
* **Data Visualization:** Matplotlib & Seaborn

---

## Repository Structure

```text
├── app.py                # Main Streamlit application script
├── requirements.txt      # Server-side environment dependencies
└── README.md             # Project documentation and presentation