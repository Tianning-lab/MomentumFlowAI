# MomentumFlow AI

<p align="center">
  <img src="https://img.shields.io/badge/Confluent-Kafka-blue?style=for-the-badge&logo=apache-kafka" alt="Confluent Kafka"/>
  <img src="https://img.shields.io/badge/R-Shiny-276DC3?style=for-the-badge&logo=r" alt="R Shiny"/>
  <img src="https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python" alt="Python"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="MIT License"/>
</p>

<p align="center">
  <b>Real-time AI-Powered Trading Signals for S&P 500 Momentum Strategies</b>
</p>

<p align="center">
  🏆 <i>Confluent AI Partner Catalyst Hackathon 2025</i>
</p>

---

## 📖 Overview

**MomentumFlow AI** is a real-time momentum trading scanner that leverages **Confluent Kafka** streaming to deliver institutional-grade market analysis. Built for the S&P 500, it combines proven momentum trading strategies with live data streaming and AI-powered pattern recognition.

### Key Features

- 📊 **Stock Scanner** — Scans 534 S&P 500 stocks against 5 momentum criteria
- 📈 **Trend Indicator** — EMA-based trend detection (Bullish/Bearish/Neutral)
- 🚩 **Bull Flag Detection** — Automated pattern recognition with adjustable thresholds
- 📰 **Live News Feed** — Google News streaming with sentiment analysis
- 🧮 **Risk Calculator** — Position sizing with scaling protocols
- 💡 **Trade Ideas** — Auto-generated setups based on score + patterns

---

## 🏗️ Architecture

```
┌──────────────────┐     ┌─────────────────────┐     ┌──────────────────┐
│  Yahoo Finance   │     │   Confluent Kafka   │     │    R Shiny       │
│  Google News     │────▶│   (Cloud - Zurich)  │────▶│    Dashboard     │
└──────────────────┘     │                     │     └──────────────────┘
                         │  • stock_prices     │
   Python Producers      │  • stock_news       │      REST API Consumer
                         └─────────────────────┘
```

### Kafka Topics

| Topic | Content | Update Frequency |
|-------|---------|------------------|
| `stock_prices` | OHLCV + Momentum Scores | ~2 min cycle |
| `stock_news` | Headlines + Sentiment | ~5 min cycle |

---

## 📁 Project Structure

```
MomentumFlowAI/
├── app_dark_theme.R          # Main Shiny application
├── kafka_producer.py         # Stock price streaming producer
├── kafka_news_producer.py    # News streaming producer
├── README.md                 # This file
├── LICENSE                   # MIT License
└── docs/
    └── MomentumFlowAI_Hackathon_Submission.pdf
```

---

## 🚀 Quick Start

### Prerequisites

- R 4.x with RStudio
- Python 3.x
- Confluent Cloud account (free tier works)

### 1. Clone the Repository

```bash
git clone https://github.com/Tianning-lab/MomentumFlowAI.git
cd MomentumFlowAI
```

### 2. Install R Dependencies

```r
install.packages(c(
  "shiny", "shinydashboard", "quantmod", "tidyverse", 
  "plotly", "DT", "TTR", "lubridate", "scales",
  "PerformanceAnalytics", "httr", "jsonlite", "base64enc", "xml2"
))
```

### 3. Install Python Dependencies

```bash
pip install confluent-kafka yfinance pandas numpy feedparser requests
```

### 4. Configure Confluent Kafka

1. Create a Confluent Cloud account at [confluent.cloud](https://confluent.cloud)
2. Create a cluster (Basic tier is fine)
3. Create topics: `stock_prices` and `stock_news`
4. Generate API keys

Update credentials in both Python files:

```python
KAFKA_CONFIG = {
    'bootstrap.servers': 'YOUR_BOOTSTRAP_SERVER',
    'sasl.username': 'YOUR_API_KEY',
    'sasl.password': 'YOUR_API_SECRET',
    ...
}
```

### 5. Start the Producers

**Terminal 1 — Stock Prices:**
```bash
python kafka_producer.py
```

**Terminal 2 — News:**
```bash
python kafka_news_producer.py
```

### 6. Run the Shiny App

In RStudio, open `app_dark_theme.R` and click **Run App**.

---

## 📊 Momentum Criteria (Adapted for S&P 500)

| # | Criterion | Threshold | Rationale |
|---|-----------|-----------|-----------|
| 1 | Price Range | $5 - $500 | Covers most S&P 500 stocks |
| 2 | Daily Change | ≥ 0.5% | Meaningful price movement |
| 3 | Relative Volume | ≥ 1.0x average | Confirms participation |
| 4 | Momentum | Price > Open | Intraday buying pressure |
| 5 | Volatility | Range ≥ 0.5% | Sufficient profit opportunity |

---

## 🚩 Bull Flag Detection

Thresholds adapted for large-cap stocks:

| Parameter | S&P 500 | Penny Stocks |
|-----------|---------|--------------|
| Pole Return | ≥ 1.5% | ≥ 3% |
| Flag Range | < 7% | < 5% |
| Volume | Decreasing | Decreasing |

---

## 🛠️ Technology Stack

| Layer | Technology |
|-------|------------|
| Streaming | Confluent Cloud (Apache Kafka) |
| Producers | Python, confluent-kafka, feedparser |
| Data Sources | Yahoo Finance, Google News RSS |
| Frontend | R Shiny, shinydashboard |
| Visualization | Plotly, DT |
| Analysis | quantmod, TTR, PerformanceAnalytics |

---

## 📸 Screenshots

### Landing Page
![Landing Page](docs/screenshots/landing.png)

### Stock Scanner with Trend Indicator
![Scanner](docs/screenshots/scanner.png)

### Bull Flag Detection
![Bull Flags](docs/screenshots/bullflag.png)

### Live News Feed
![News](docs/screenshots/news.png)

---

## 🗺️ Roadmap

- [ ] Q1 2026: Options flow analysis via Kafka Streams
- [ ] Q2 2026: Claude AI integration for natural language queries
- [ ] Q3 2026: Multi-asset support (crypto, forex)
- [ ] Q4 2026: Mobile app with push notifications

---

## 👨‍💻 Author

**Tianning Ning**  
Founder & CEO, New Way Capital Advisory Limited

- 🐙 GitHub: [@Tianning-lab](https://github.com/Tianning-lab)
- 📧 Email: tnk@newwaycapital.com
- 📍 Geneva, Switzerland

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Confluent](https://confluent.io) for the amazing Kafka platform
- [Yahoo Finance](https://finance.yahoo.com) for market data
- [Google News](https://news.google.com) for news feeds

---

<p align="center">
  <b>© 2025 New Way Capital Advisory Limited</b><br/>
  Made with ❤️ in Geneva, Switzerland
</p>

---

## Live Demo

MomentumFlow AI is live at **[nwc-advisory.com/app](https://nwc-advisory.com/app/)** — part of the [New Way Capital Advisory](https://nwc-advisory.com) analytics platform.

### Related Tools

- [Portfolio Analyser](https://nwc-advisory.com/app/analyser/) — Institutional portfolio analysis
- [Risk API](https://nwc-advisory.com) — 7-signal market risk scoring
- [Property Comps](https://property.nwc-advisory.com) — Comparable sales across 11 markets
- [Portfolio X-Ray](https://nwc-advisory.com/xray) — Free fund look-through analysis

