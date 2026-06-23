# Nexus-Quant 📊
### Multi-Agent Financial Intelligence System

> An AI-powered stock analysis tool that combines technical analysis, news sentiment, and risk evaluation into a single actionable recommendation — **BUY, HOLD, or AVOID**.

---

## 🧠 What It Does

Nexus-Quant takes a stock name as input (e.g., `RELIANCE`, `TCS`, `AAPL`) and runs it through three specialized AI agents that work in sequence:

1. **Trend Analysis Agent** — analyzes price behavior using 6 technical indicators
2. **Sentiment Analysis Agent** — reads news headlines and scores market mood using Claude AI
3. **Risk Evaluation Agent** — fuses both signals into a composite risk score and final decision

The output is a clean dashboard showing the trend direction, sentiment verdict, risk level, composite score, and a plain-English explanation of the reasoning.

---

## 🏗️ System Architecture

```
User Input (Stock Name)
        │
        ▼
┌───────────────────┐     ┌───────────────────┐
│  Agent 1          │     │  Agent 2           │
│  Trend Analysis   │     │  Sentiment Analysis│
│                   │     │                    │
│  • SMA-5 / SMA-20 │     │  • News headlines  │
│  • RSI-14         │     │  • Claude API NLP  │
│  • MACD proxy     │     │  • Score: -1 to +1 │
│  • Momentum       │     │  • POS/NEG/NEUTRAL │
│  • Volume trend   │     └────────┬───────────┘
└────────┬──────────┘              │
         │                         │
         └──────────┬──────────────┘
                    ▼
        ┌───────────────────────┐
        │  Agent 3              │
        │  Risk Evaluation      │
        │                       │
        │  Trend   →  55%       │
        │  Sentiment → 30%      │
        │  RSI     →  15%       │
        │                       │
        │  Score: 0–100         │
        │  Decision: BUY /      │
        │  HOLD / AVOID         │
        └───────────┬───────────┘
                    ▼
            Dashboard Output
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| API Server | FastAPI + Uvicorn | REST endpoints, file serving |
| Numerics | NumPy | Price simulation, technical indicators |
| AI Sentiment | Claude API (Sonnet) | NLP headline analysis and scoring |
| HTTP Client | Requests | Claude API calls |
| Price Model | Geometric Brownian Motion | Realistic synthetic market data |
| Risk Fusion | Weighted scoring formula | BUY / HOLD / AVOID decision |
| Frontend | HTML + CSS + JavaScript | Dashboard UI (single file, no framework) |
| Typography | Google Fonts | Space Mono + Syne |

---

## 📁 Project Structure

```
nexus-quant/
│
├── main.py            # FastAPI backend — all three agents
├── index.html         # Frontend dashboard (served by FastAPI)
├── requirements.txt   # Python dependencies
├── run.sh             # One-command startup script
└── README.md          # This file
```

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.10 or above
- pip

### Step 1 — Clone or download the project

```bash
git clone https://github.com/Prakruthisb/Nexus-Quant
cd nexus-quant
```

### Step 2 — Install dependencies

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install fastapi uvicorn numpy requests
```

### Step 3 — Run the server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 4 — Open the dashboard

```
http://localhost:8000
```

---

## 🚀 Usage

**Via the dashboard:**
Type any stock name in the search bar and click **ANALYZE →**

**Via the API directly:**
```bash
curl http://localhost:8000/analyze/RELIANCE
```

**List all supported stocks:**
```bash
curl http://localhost:8000/stocks
```

**Sample API Response:**
```json
{
  "stock": "RELIANCE",
  "company_name": "Reliance Industries Ltd",
  "current_price": 2950.42,
  "currency": "INR",
  "trend": {
    "trend": "UP",
    "confidence": 78,
    "rsi": 54.3,
    "price_change_pct": 6.2
  },
  "sentiment": {
    "sentiment": "POSITIVE",
    "score": 0.312,
    "headline_count": 10
  },
  "risk": {
    "risk_level": "LOW",
    "decision": "BUY",
    "composite_score": 71.4,
    "explanation": [...]
  }
}
```

---

## 📈 Supported Stocks

### Indian Markets (NSE)
| Symbol | Company |
|---|---|
| RELIANCE | Reliance Industries Ltd |
| TCS | Tata Consultancy Services |
| INFY | Infosys Limited |
| HDFCBANK | HDFC Bank Limited |
| ICICIBANK | ICICI Bank Limited |
| WIPRO | Wipro Limited |
| SBIN | State Bank of India |
| BAJFINANCE | Bajaj Finance Limited |
| TATAMOTORS | Tata Motors Limited |
| ADANIENT | Adani Enterprises Ltd |
| SUNPHARMA | Sun Pharmaceutical |
| MARUTI | Maruti Suzuki India Ltd |
| LT | Larsen & Toubro Ltd |
| AXISBANK | Axis Bank Limited |
| KOTAKBANK | Kotak Mahindra Bank |
| NTPC | NTPC Limited |
| ONGC | Oil & Natural Gas Corp |
| TATASTEEL | Tata Steel Limited |
| HINDALCO | Hindalco Industries Ltd |

### US Markets
| Symbol | Company |
|---|---|
| AAPL | Apple Inc. |
| MSFT | Microsoft Corporation |
| GOOGL | Alphabet Inc. |
| AMZN | Amazon.com Inc. |
| TSLA | Tesla Inc. |
| META | Meta Platforms Inc. |
| NVDA | NVIDIA Corporation |

> You can also type aliases like `INFOSYS`, `HDFC`, `SBI`, `TATA`, `APPLE`, `GOOGLE`, `TESLA` — the system resolves them automatically.

---

## 🤖 Agent Details

### Agent 1 — Trend Analysis
Generates a 65-day price series using Geometric Brownian Motion (GBM) with stock-specific drift (μ) and volatility (σ) parameters. Computes 6 technical signals:

- **SMA Crossover** — Price vs 20-day moving average
- **Golden/Death Cross** — SMA-5 vs SMA-20
- **10-day Momentum** — Percentage price change
- **Volume Trend** — Recent vs 20-day average volume
- **RSI-14** — Relative Strength Index (oversold < 35, overbought > 65)
- **MACD Proxy** — EMA-12 vs EMA-26

Outputs: `UP / DOWN / NEUTRAL` with confidence percentage.

### Agent 2 — Sentiment Analysis
Generates 10 contextual headlines per stock based on its sector and trend profile, sends them to the **Claude API (claude-sonnet)** via a structured JSON prompt, and receives:
- Per-headline sentiment score (−1.0 to +1.0)
- Overall sentiment: `POSITIVE / NEGATIVE / NEUTRAL`
- 2-sentence market narrative

Falls back to keyword-based scoring if the API is unreachable.

### Agent 3 — Risk Evaluation
Fuses Agent 1 and Agent 2 outputs using a weighted composite formula:

```
Composite Score = (Trend Score × 0.55) + (Sentiment Score × 0.30) + (RSI Score × 0.15) + Signal Bonus

Score ≥ 63  →  LOW Risk    →  BUY
Score 42–62 →  MEDIUM Risk →  HOLD
Score < 42  →  HIGH Risk   →  AVOID
```

Generates a plain-English explanation covering trend reasoning, RSI interpretation, sentiment context, and a final verdict.

---

## ✅ Current Progress

- Three-agent pipeline fully implemented and tested
- FastAPI backend with REST API and file serving
- Complete frontend dashboard (single HTML file, no framework)
- 26 pre-profiled stocks across Indian and US markets
- Claude API integration for AI-powered sentiment analysis
- Deterministic daily seeding for reproducible results

---

## 🔄 Ongoing Work

- Replacing simulated GBM prices with live market data (yfinance / NSE API)
- Replacing template headlines with real news feeds (NewsAPI / Google News RSS)

---

## 🚀 Future Scope

1. **Live Market Data Integration** — Connect yfinance or NSE API for real-time prices and actual technical signals
2. **Social Media & Commodity Agents** — Add Reddit/Twitter sentiment and commodity price tracking (oil, gold) as two additional agents
3. **Backtesting Engine** — Replay historical signals against actual outcomes to measure BUY/HOLD/AVOID accuracy
4. **Portfolio Risk Dashboard** — Multi-stock portfolio view with aggregate risk score, correlation analysis, and real-time alerts

---

## ⚠️ Disclaimer

This project is built for **educational and portfolio demonstration purposes only**. The analysis generated is not financial advice. Stock market investments carry risk. Always consult a certified financial advisor before making investment decisions.
