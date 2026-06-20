from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import numpy as np
import requests
import json
import random
import math
from datetime import datetime

app = FastAPI(title="Nexus-Quant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# Stock Database (realistic profiles)
# ─────────────────────────────────────────────

STOCK_DB = {
    "RELIANCE":   {"company": "Reliance Industries Ltd",      "sector": "Energy / Conglomerate",  "base": 2950,  "vol": 0.022, "trend_bias": 0.60, "currency": "INR"},
    "TCS":        {"company": "Tata Consultancy Services",    "sector": "IT Services",             "base": 3820,  "vol": 0.018, "trend_bias": 0.65, "currency": "INR"},
    "INFY":       {"company": "Infosys Limited",              "sector": "IT Services",             "base": 1620,  "vol": 0.020, "trend_bias": 0.55, "currency": "INR"},
    "HDFCBANK":   {"company": "HDFC Bank Limited",            "sector": "Banking",                 "base": 1780,  "vol": 0.019, "trend_bias": 0.58, "currency": "INR"},
    "ICICIBANK":  {"company": "ICICI Bank Limited",           "sector": "Banking",                 "base": 1120,  "vol": 0.021, "trend_bias": 0.62, "currency": "INR"},
    "WIPRO":      {"company": "Wipro Limited",                "sector": "IT Services",             "base": 510,   "vol": 0.023, "trend_bias": 0.48, "currency": "INR"},
    "SBIN":       {"company": "State Bank of India",          "sector": "Public Sector Banking",   "base": 820,   "vol": 0.025, "trend_bias": 0.52, "currency": "INR"},
    "BAJFINANCE": {"company": "Bajaj Finance Limited",        "sector": "NBFC",                    "base": 7200,  "vol": 0.028, "trend_bias": 0.60, "currency": "INR"},
    "TATAMOTORS": {"company": "Tata Motors Limited",          "sector": "Automobiles",             "base": 980,   "vol": 0.030, "trend_bias": 0.55, "currency": "INR"},
    "ADANIENT":   {"company": "Adani Enterprises Ltd",        "sector": "Infrastructure",          "base": 2400,  "vol": 0.035, "trend_bias": 0.45, "currency": "INR"},
    "SUNPHARMA":  {"company": "Sun Pharmaceutical Industries","sector": "Pharmaceuticals",         "base": 1680,  "vol": 0.019, "trend_bias": 0.58, "currency": "INR"},
    "ONGC":       {"company": "Oil & Natural Gas Corporation","sector": "Energy",                  "base": 280,   "vol": 0.022, "trend_bias": 0.50, "currency": "INR"},
    "MARUTI":     {"company": "Maruti Suzuki India Ltd",      "sector": "Automobiles",             "base": 12500, "vol": 0.018, "trend_bias": 0.60, "currency": "INR"},
    "NTPC":       {"company": "NTPC Limited",                 "sector": "Power Generation",        "base": 390,   "vol": 0.020, "trend_bias": 0.55, "currency": "INR"},
    "AXISBANK":   {"company": "Axis Bank Limited",            "sector": "Banking",                 "base": 1180,  "vol": 0.024, "trend_bias": 0.52, "currency": "INR"},
    "KOTAKBANK":  {"company": "Kotak Mahindra Bank Ltd",      "sector": "Banking",                 "base": 1850,  "vol": 0.019, "trend_bias": 0.57, "currency": "INR"},
    "LT":         {"company": "Larsen & Toubro Ltd",          "sector": "Engineering & EPC",       "base": 3650,  "vol": 0.021, "trend_bias": 0.63, "currency": "INR"},
    "TATASTEEL":  {"company": "Tata Steel Limited",           "sector": "Metals & Mining",         "base": 155,   "vol": 0.030, "trend_bias": 0.48, "currency": "INR"},
    "HINDALCO":   {"company": "Hindalco Industries Ltd",      "sector": "Metals & Mining",         "base": 680,   "vol": 0.027, "trend_bias": 0.52, "currency": "INR"},
    "AAPL":       {"company": "Apple Inc.",                   "sector": "Consumer Technology",     "base": 195,   "vol": 0.016, "trend_bias": 0.65, "currency": "USD"},
    "MSFT":       {"company": "Microsoft Corporation",        "sector": "Cloud & Enterprise Tech", "base": 415,   "vol": 0.015, "trend_bias": 0.70, "currency": "USD"},
    "GOOGL":      {"company": "Alphabet Inc.",                "sector": "Digital Advertising",     "base": 175,   "vol": 0.018, "trend_bias": 0.62, "currency": "USD"},
    "AMZN":       {"company": "Amazon.com Inc.",              "sector": "E-Commerce / Cloud",      "base": 195,   "vol": 0.019, "trend_bias": 0.63, "currency": "USD"},
    "TSLA":       {"company": "Tesla Inc.",                   "sector": "Electric Vehicles",       "base": 240,   "vol": 0.038, "trend_bias": 0.50, "currency": "USD"},
    "META":       {"company": "Meta Platforms Inc.",          "sector": "Social Media / AI",       "base": 520,   "vol": 0.022, "trend_bias": 0.65, "currency": "USD"},
    "NVDA":       {"company": "NVIDIA Corporation",           "sector": "Semiconductors / AI",     "base": 875,   "vol": 0.028, "trend_bias": 0.72, "currency": "USD"},
}

ALIASES = {
    "RELIANCE": "RELIANCE", "RIL": "RELIANCE",
    "TCS": "TCS",
    "INFOSYS": "INFY", "INFY": "INFY",
    "HDFC": "HDFCBANK", "HDFCBANK": "HDFCBANK",
    "ICICI": "ICICIBANK", "ICICIBANK": "ICICIBANK",
    "WIPRO": "WIPRO",
    "SBI": "SBIN", "SBIN": "SBIN",
    "BAJAJFINANCE": "BAJFINANCE", "BAJFINANCE": "BAJFINANCE",
    "TATA": "TATAMOTORS", "TATAMOTORS": "TATAMOTORS",
    "ADANI": "ADANIENT", "ADANIENT": "ADANIENT",
    "SUNPHARMA": "SUNPHARMA",
    "ONGC": "ONGC",
    "MARUTI": "MARUTI",
    "NTPC": "NTPC",
    "AXIS": "AXISBANK", "AXISBANK": "AXISBANK",
    "KOTAK": "KOTAKBANK", "KOTAKBANK": "KOTAKBANK",
    "LT": "LT",
    "TATASTEEL": "TATASTEEL",
    "HINDALCO": "HINDALCO",
    "APPLE": "AAPL", "AAPL": "AAPL",
    "MICROSOFT": "MSFT", "MSFT": "MSFT",
    "GOOGLE": "GOOGL", "GOOGL": "GOOGL",
    "AMAZON": "AMZN", "AMZN": "AMZN",
    "TESLA": "TSLA", "TSLA": "TSLA",
    "META": "META",
    "NVIDIA": "NVDA", "NVDA": "NVDA",
}


def resolve_stock(name: str):
    n = name.upper().strip()
    key = ALIASES.get(n, n)
    profile = STOCK_DB.get(key) or {
        "company": f"{n} Ltd", "sector": "General Market",
        "base": 500.0, "vol": 0.025, "trend_bias": 0.5, "currency": "INR"
    }
    return key, profile


# ─────────────────────────────────────────────
# AGENT 1 — Trend Analysis
# ─────────────────────────────────────────────

def trend_analysis_agent(stock_key: str, profile: dict) -> dict:
    today = datetime.now()
    seed = int(f"{today.year}{today.month}{today.day}") + sum(ord(c) for c in stock_key)
    rng = np.random.default_rng(seed)

    # GBM price series (65 trading days ≈ 3 months)
    mu = (profile["trend_bias"] - 0.5) * 0.004
    sigma = profile["vol"]
    S = profile["base"]
    prices = [S]
    for _ in range(64):
        r = rng.normal(mu, sigma)
        S = S * math.exp(r)
        prices.append(round(S, 4))
    close = np.array(prices)

    # Volume series
    vols = rng.lognormal(math.log(1_200_000), 0.4, 65).astype(int)

    signals, bullish_count, bearish_count = [], 0, 0
    cur = close[-1]

    # 1. Price vs SMA20
    sma20 = float(np.mean(close[-20:]))
    if cur > sma20:
        signals.append({"name": "Price above SMA-20", "signal": "Bullish"}); bullish_count += 1
    else:
        signals.append({"name": "Price below SMA-20", "signal": "Bearish"}); bearish_count += 1

    # 2. SMA5 vs SMA20
    sma5 = float(np.mean(close[-5:]))
    if sma5 > sma20:
        signals.append({"name": "SMA-5 > SMA-20 (Golden cross)", "signal": "Bullish"}); bullish_count += 2
    else:
        signals.append({"name": "SMA-5 < SMA-20 (Death cross)", "signal": "Bearish"}); bearish_count += 2

    # 3. 10-day momentum
    mom = (close[-1] - close[-10]) / close[-10] * 100
    if mom > 2:
        signals.append({"name": f"10-day momentum +{mom:.1f}%", "signal": "Bullish"}); bullish_count += 1
    elif mom < -2:
        signals.append({"name": f"10-day momentum {mom:.1f}%", "signal": "Bearish"}); bearish_count += 1
    else:
        signals.append({"name": f"10-day momentum {mom:.1f}% (flat)", "signal": "Neutral"})

    # 4. Volume trend
    v_recent = float(np.mean(vols[-5:]))
    v_avg    = float(np.mean(vols[-20:]))
    if v_recent > v_avg * 1.2:
        signals.append({"name": "Volume surge (+20% vs avg)", "signal": "Bullish"}); bullish_count += 1
    elif v_recent < v_avg * 0.8:
        signals.append({"name": "Volume declining (-20%)", "signal": "Bearish"}); bearish_count += 1
    else:
        signals.append({"name": "Volume within normal range", "signal": "Neutral"})

    # 5. RSI-14
    delta = np.diff(close[-15:])
    avg_gain = float(np.mean(np.where(delta > 0, delta, 0))) + 1e-9
    avg_loss = float(np.mean(np.where(delta < 0, -delta, 0))) + 1e-9
    rsi_val = 100 - (100 / (1 + avg_gain / avg_loss))
    if rsi_val < 35:
        signals.append({"name": f"RSI {rsi_val:.0f} — Oversold zone", "signal": "Bullish"}); bullish_count += 2
    elif rsi_val > 65:
        signals.append({"name": f"RSI {rsi_val:.0f} — Overbought zone", "signal": "Bearish"}); bearish_count += 2
    else:
        signals.append({"name": f"RSI {rsi_val:.0f} — Neutral zone", "signal": "Neutral"})

    # 6. EMA12 vs EMA26 (MACD proxy)
    def ema(arr, n):
        k = 2 / (n + 1); e = arr[0]
        for v in arr[1:]: e = v * k + e * (1 - k)
        return e
    ema12 = ema(close[-30:], 12); ema26 = ema(close[-30:], 26)
    if ema12 > ema26:
        signals.append({"name": "EMA-12 > EMA-26 (MACD bullish)", "signal": "Bullish"}); bullish_count += 1
    else:
        signals.append({"name": "EMA-12 < EMA-26 (MACD bearish)", "signal": "Bearish"}); bearish_count += 1

    pct = (close[-1] - close[0]) / close[0] * 100
    total = bullish_count + bearish_count
    if bullish_count > bearish_count:
        trend = "UP";      conf = int(bullish_count / total * 100)
    elif bearish_count > bullish_count:
        trend = "DOWN";    conf = int(bearish_count / total * 100)
    else:
        trend = "NEUTRAL"; conf = 50

    return {
        "trend": trend, "confidence": min(conf, 95),
        "signals": signals,
        "price_change_pct": round(float(pct), 2),
        "current_price": round(float(cur), 2),
        "rsi": round(float(rsi_val), 1),
        "sma_20": round(sma20, 2), "sma_5": round(sma5, 2),
        "bullish_signals": bullish_count, "bearish_signals": bearish_count,
    }


# ─────────────────────────────────────────────
# AGENT 2 — Sentiment Analysis via Claude API
# ─────────────────────────────────────────────

HL_BULLISH = [
    "{company} reports record quarterly revenue, beats analyst estimates",
    "{company} announces strategic expansion into new markets",
    "Analysts upgrade {ticker} with revised target price upward",
    "{company} secures landmark deal worth thousands of crores",
    "{ticker} shares climb as institutional investors increase stake",
    "{company} dividend announcement boosts investor confidence",
    "{sector} outlook improves; {company} well-positioned to benefit",
    "{company} Q3 profit jumps on strong demand and margin expansion",
    "{company} wins major government tender, stock surges",
    "{company} CEO signals strong pipeline ahead in investor call",
]
HL_BEARISH = [
    "{company} misses earnings expectations amid rising operational costs",
    "Regulatory concerns weigh on {ticker} near-term outlook",
    "{company} faces headwinds as competitive pressure intensifies",
    "Analysts cut {ticker} price target citing margin compression",
    "{sector} faces challenges; {company} stock under pressure",
    "{company} management cautions on near-term revenue visibility",
    "Global macro uncertainty clouds {ticker} growth outlook",
    "{company} reports widening losses in latest quarterly results",
    "{ticker} insiders file to sell shares, dampening sentiment",
    "{company} faces probe over compliance issues, stock falls",
]
HL_NEUTRAL = [
    "{company} to announce quarterly results next week",
    "{ticker} trading volumes remain steady amid market churn",
    "{company} board meeting scheduled to discuss capital allocation",
    "{sector} awaits policy clarity before directional moves",
    "{company} maintains full-year guidance unchanged",
    "{ticker} holds steady as investors assess macro environment",
]


def generate_headlines(company, ticker, sector, trend_bias):
    random.seed(sum(ord(c) for c in ticker) + datetime.now().day)
    if trend_bias >= 0.60:
        mix = [("b", 5), ("n", 3), ("a", 2)]
    elif trend_bias <= 0.45:
        mix = [("a", 5), ("n", 3), ("b", 2)]
    else:
        mix = [("n", 4), ("b", 3), ("a", 3)]

    out = []
    for kind, cnt in mix:
        pool = HL_BULLISH if kind == "b" else HL_BEARISH if kind == "a" else HL_NEUTRAL
        for tmpl in random.sample(pool, min(cnt, len(pool))):
            out.append(tmpl.format(company=company, ticker=ticker, sector=sector))
    random.shuffle(out)
    return out[:10]


def sentiment_analysis_agent(stock_key, profile):
    company = profile["company"]
    sector  = profile.get("sector", "General")
    headlines = generate_headlines(company, stock_key, sector, profile["trend_bias"])

    prompt = f"""You are a financial sentiment analyst for Nexus-Quant.
Analyze these {len(headlines)} news headlines about {company} ({stock_key}), a company in the {sector} sector.

Headlines:
{chr(10).join(f'{i+1}. {h}' for i, h in enumerate(headlines))}

Respond ONLY with valid JSON — no markdown, no explanation, no code fences:
{{
  "headlines": [
    {{"headline": "...", "sentiment": "Positive|Negative|Neutral", "score": 0.0, "reason": "one sentence"}}
  ],
  "overall_sentiment": "POSITIVE|NEGATIVE|NEUTRAL",
  "overall_score": 0.0,
  "summary": "2-sentence market narrative."
}}

score = float from -1.0 to +1.0 (negative = bearish, positive = bullish, 0 = neutral).
overall_score = weighted average of individual scores."""

    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"Content-Type": "application/json"},
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=30
        )
        result = resp.json()
        text = result["content"][0]["text"].strip()
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"): text = text[4:]
        text = text.strip()

        data = json.loads(text)
        analyzed = data.get("headlines", [])
        overall  = data.get("overall_sentiment", "NEUTRAL")
        score    = float(data.get("overall_score", 0.0))
        summary  = data.get("summary", "")

        pos = sum(1 for h in analyzed if h.get("sentiment") == "Positive")
        neg = sum(1 for h in analyzed if h.get("sentiment") == "Negative")
        neu = sum(1 for h in analyzed if h.get("sentiment") == "Neutral")

        return {
            "sentiment": overall, "score": round(score, 4),
            "confidence": min(100, int(abs(score) * 120 + 30)),
            "analyzed_headlines": analyzed,
            "headline_count": len(analyzed),
            "positive_count": pos, "negative_count": neg, "neutral_count": neu,
            "summary": summary, "error": None
        }

    except Exception as e:
        # Rule-based fallback
        pos = sum(1 for h in headlines if any(w in h.lower() for w in ["record","beats","upgrade","strong","surges","wins","boosts"]))
        neg = sum(1 for h in headlines if any(w in h.lower() for w in ["miss","pressure","concern","probe","losses","headwind","falls","cut"]))
        neu = len(headlines) - pos - neg
        score = (pos - neg) / (len(headlines) + 1e-9)
        overall = "POSITIVE" if score > 0.1 else "NEGATIVE" if score < -0.1 else "NEUTRAL"
        analyzed = [{"headline": h, "sentiment": "Positive" if any(w in h.lower() for w in ["record","beats","upgrade","strong","surges","wins"]) else "Negative" if any(w in h.lower() for w in ["miss","pressure","concern","probe","losses"]) else "Neutral", "score": 0.0, "reason": "Keyword-based fallback"} for h in headlines]
        return {
            "sentiment": overall, "score": round(float(score), 4),
            "confidence": min(100, int(abs(score) * 100 + 30)),
            "analyzed_headlines": analyzed,
            "headline_count": len(headlines),
            "positive_count": pos, "negative_count": neg, "neutral_count": neu,
            "summary": f"Rule-based fallback. Claude API error: {str(e)[:60]}",
            "error": str(e)[:80]
        }


# ─────────────────────────────────────────────
# AGENT 3 — Risk Evaluation
# ─────────────────────────────────────────────

def risk_evaluation_agent(trend_data, sentiment_data, profile):
    trend      = trend_data.get("trend", "NEUTRAL")
    trend_conf = trend_data.get("confidence", 50) / 100
    sentiment  = sentiment_data.get("sentiment", "NEUTRAL")
    sent_score = sentiment_data.get("score", 0.0)
    price_chg  = trend_data.get("price_change_pct", 0)
    rsi        = trend_data.get("rsi", 50)
    bull       = trend_data.get("bullish_signals", 0)
    bear       = trend_data.get("bearish_signals", 0)

    # Trend score 0–100
    trend_score = 50 + (trend_conf * 48 if trend == "UP" else -trend_conf * 48 if trend == "DOWN" else 0)

    # Sentiment score 0–100
    sent_numeric = (sent_score + 1) / 2 * 100

    # RSI score
    rsi_score = 75 if rsi < 30 else 25 if rsi > 70 else 60 if rsi < 45 else 40 if rsi > 55 else 50

    # Signal strength bonus
    signal_bonus = min(8, (bull - bear) * 1.5)

    composite = max(0, min(100, trend_score * 0.55 + sent_numeric * 0.30 + rsi_score * 0.15 + signal_bonus))

    if composite >= 63:   risk_level, decision = "LOW",    "BUY"
    elif composite >= 42: risk_level, decision = "MEDIUM", "HOLD"
    else:                 risk_level, decision = "HIGH",   "AVOID"

    expl = []
    if trend == "UP":
        expl.append(f"📈 Technical trend is UPWARD ({trend_conf*100:.0f}% confidence). {bull} bullish vs {bear} bearish signals — price action and moving averages support continued momentum.")
    elif trend == "DOWN":
        expl.append(f"📉 Technical trend is DOWNWARD ({trend_conf*100:.0f}% confidence). {bear} bearish vs {bull} bullish signals — selling pressure currently dominates.")
    else:
        expl.append(f"📊 Technical trend is NEUTRAL — signals evenly split ({bull} bullish / {bear} bearish). No clear directional bias.")

    if rsi < 35:
        expl.append(f"⚡ RSI at {rsi:.0f} is in the OVERSOLD zone — historically a mean-reversion opportunity. Downside risk appears limited.")
    elif rsi > 65:
        expl.append(f"⚡ RSI at {rsi:.0f} is in the OVERBOUGHT zone — risk of pullback is elevated. Consider waiting for cooling-off period.")
    else:
        expl.append(f"⚡ RSI at {rsi:.0f} is in the NEUTRAL zone — no extreme conditions, momentum is balanced.")

    if sentiment == "POSITIVE":
        expl.append(f"📰 News sentiment is POSITIVE (score: {sent_score:+.3f}) — market narrative and headlines support optimism.")
    elif sentiment == "NEGATIVE":
        expl.append(f"📰 News sentiment is NEGATIVE (score: {sent_score:+.3f}) — headlines signal concern; headline risk is elevated.")
    else:
        expl.append(f"📰 News sentiment is NEUTRAL (score: {sent_score:+.3f}) — no strong directional signal from recent news flow.")

    if abs(price_chg) > 5:
        d = "gained" if price_chg > 0 else "lost"
        expl.append(f"📊 Stock has {d} {abs(price_chg):.1f}% over 3 months — {'strong appreciation reflects positive momentum.' if price_chg > 0 else 'significant decline may indicate structural concern.'}")

    verdict = {
        "BUY":   f"✅ VERDICT: Bullish signals are broadly aligned. Composite score {composite:.0f}/100 reflects LOW-RISK conditions. Consider initiating or adding to a position with appropriate sizing.",
        "HOLD":  f"⏸️ VERDICT: Mixed signals create a MEDIUM-RISK scenario. Composite score {composite:.0f}/100 is inconclusive. Existing holders may maintain; new entries should await confirmation.",
        "AVOID": f"🛑 VERDICT: Converging bearish signals create HIGH-RISK conditions. Composite score {composite:.0f}/100 signals caution. Protect capital and wait for stabilisation before entering."
    }
    expl.append(f"\n{verdict[decision]}")

    return {
        "risk_level": risk_level, "decision": decision,
        "composite_score": round(float(composite), 1),
        "trend_score": round(float(trend_score), 1),
        "sentiment_score": round(float(sent_numeric), 1),
        "rsi_score": round(float(rsi_score), 1),
        "explanation": expl,
    }


# ─────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────

@app.get("/analyze/{stock_name}")
async def analyze_stock(stock_name: str):
    key, profile = resolve_stock(stock_name)
    trend_data     = trend_analysis_agent(key, profile)
    sentiment_data = sentiment_analysis_agent(key, profile)
    risk_data      = risk_evaluation_agent(trend_data, sentiment_data, profile)
    return {
        "stock": stock_name.upper(),
        "ticker": key,
        "timestamp": datetime.now().isoformat(),
        "company_name": profile["company"],
        "sector": profile.get("sector", ""),
        "current_price": trend_data["current_price"],
        "currency": profile["currency"],
        "trend": trend_data,
        "sentiment": sentiment_data,
        "risk": risk_data,
    }

@app.get("/stocks")
async def list_stocks():
    return {"stocks": list(STOCK_DB.keys())}

@app.get("/")
async def root():
    return FileResponse("D:/major_project/index.html")