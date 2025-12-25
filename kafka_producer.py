"""
MomentumFlow AI - Kafka Stock Price Producer
============================================
Streams real-time S&P 500 stock data to Confluent Kafka.
Pre-calculates momentum score AND bull flag detection for instant scanning.

Usage:
    1. Install dependencies: pip install confluent-kafka yfinance numpy
    2. Update your API credentials below
    3. Run: python kafka_producer.py
"""

import json
import time
from datetime import datetime
from confluent_kafka import Producer
import yfinance as yf
import numpy as np

# =============================================================================
# CONFIGURATION - Update these with your Confluent credentials
# =============================================================================

KAFKA_CONFIG = {
    'bootstrap.servers': 'pkc-lzoyy.europe-west6.gcp.confluent.cloud:9092',
    'security.protocol': 'SASL_SSL',
    'sasl.mechanisms': 'PLAIN',
    'sasl.username': 'YOUR_API_KEY',      # <-- Replace with your API Key
    'sasl.password': 'YOUR_API_SECRET',   # <-- Replace with your API Secret
}

TOPIC_NAME = 'stock_prices'

# =============================================================================
# COMPLETE S&P 500 STOCK LIST (503 components as of Dec 2024)
# =============================================================================

SP500_STOCKS = [
    # Technology (75)
    "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "NVDA", "META", "TSLA", "AVGO", "ADBE",
    "ORCL", "CRM", "CSCO", "ACN", "IBM", "INTC", "AMD", "QCOM", "TXN", "NOW",
    "AMAT", "LRCX", "ADI", "MU", "SNPS", "CDNS", "KLAC", "MCHP", "APH", "MSI",
    "FTNT", "HPQ", "HPE", "KEYS", "CTSH", "IT", "ANSS", "MPWR", "ON", "SWKS",
    "TER", "AKAM", "JNPR", "NTAP", "WDC", "STX", "ZBRA", "TRMB", "TYL", "LDOS",
    "FFIV", "ENPH", "PAYC", "CPRT", "VRSN", "CDW", "INTU", "ADSK", "PYPL", "NFLX",
    "PANW", "CRWD", "ZS", "DDOG", "SNOW", "ANET", "FICO", "EPAM", "FSLR", "GEN",
    "GDDY", "PTC", "SMCI", "PLTR", "NXPI",
    
    # Finance (70)
    "BRK-B", "JPM", "V", "MA", "BAC", "WFC", "GS", "MS", "BLK", "AXP",
    "C", "SCHW", "PNC", "USB", "CME", "ICE", "CB", "MMC", "AON", "TFC",
    "AIG", "MET", "PRU", "TRV", "ALL", "AFL", "PGR", "SPGI", "MCO", "MSCI",
    "COF", "BK", "STT", "NTRS", "AMP", "CINF", "GL", "RE", "RJF", "FITB",
    "HBAN", "CFG", "KEY", "RF", "MTB", "DFS", "SYF", "AIZ", "L", "WRB",
    "FDS", "MKTX", "NDAQ", "CBOE", "CMA", "EWBC", "ZION", "FHN", "ALLY",
    "ACGL", "AJG", "BEN", "BRO", "BX", "FI", "FIS", "GPN", "HIG", "IVZ",
    "KKR", "TROW",
    
    # Healthcare (60)
    "UNH", "JNJ", "LLY", "PFE", "ABBV", "MRK", "TMO", "ABT", "DHR", "BMY",
    "AMGN", "GILD", "ISRG", "SYK", "REGN", "VRTX", "ZTS", "BDX", "MDT", "CI",
    "ELV", "HUM", "CNC", "MCK", "CAH", "BSX", "EW", "DXCM", "IQV", "A",
    "IDXX", "MTD", "WAT", "HOLX", "ALGN", "COO", "RMD", "TFX", "BAX", "VTRS",
    "HSIC", "DGX", "LH", "PKI", "BIO", "INCY", "BIIB", "MRNA", "ZBH", "STE",
    "HCA", "DVA", "UHS", "VEEV", "PODD", "COR", "CRL", "CTLT", "MOH", "RVTY",
    
    # Consumer Discretionary (60)
    "HD", "MCD", "NKE", "SBUX", "TJX", "LOW", "BKNG", "CMG", "ORLY", "AZO",
    "ROST", "MAR", "HLT", "YUM", "DHI", "LEN", "PHM", "NVR", "GRMN", "POOL",
    "BBY", "ULTA", "DRI", "WYNN", "LVS", "MGM", "CZR", "NCLH", "CCL", "RCL",
    "EXPE", "ABNB", "EBAY", "ETSY", "TSCO", "DG", "DLTR", "KMX", "GPC", "APTV",
    "BWA", "LEA", "TPR", "RL", "VFC", "PVH", "HAS", "F", "GM", "RIVN",
    "DECK", "DPZ", "LKQ", "LULU", "LW", "MHK", "UBER",
    
    # Consumer Staples (40)
    "PG", "KO", "PEP", "COST", "WMT", "PM", "MO", "MDLZ", "CL", "KMB",
    "GIS", "KHC", "HSY", "K", "CPB", "SJM", "HRL", "MKC", "CHD", "CLX",
    "STZ", "TAP", "MNST", "KDP", "CAG", "TSN", "SYY", "ADM", "KR", "WBA",
    "TGT", "EL", "BG", "CASY", "USFD", "CVS", "KVUE",
    
    # Energy (25)
    "XOM", "CVX", "COP", "SLB", "EOG", "PXD", "VLO", "PSX", "MPC", "OXY",
    "KMI", "WMB", "OKE", "HAL", "BKR", "DVN", "HES", "FANG", "APA", "EQT",
    "CTRA", "MRO", "TRGP", "OVV", "AR",
    
    # Utilities (32)
    "NEE", "DUK", "SO", "D", "AEP", "SRE", "EXC", "XEL", "WEC", "ED",
    "ES", "EIX", "FE", "DTE", "PPL", "ETR", "AEE", "CMS", "CNP", "NI",
    "EVRG", "PNW", "LNT", "ATO", "NRG", "PEG", "AWK", "AES", "CEG", "PCG",
    "VST",
    
    # Industrials (80)
    "CAT", "HON", "UNP", "RTX", "BA", "GE", "LMT", "MMM", "EMR", "ITW",
    "DE", "FDX", "UPS", "WM", "RSG", "CSX", "NSC", "PCAR", "GD", "NOC",
    "GWW", "CTAS", "ROK", "FAST", "ODFL", "PWR", "JCI", "TT", "CARR", "OTIS",
    "IR", "AME", "PH", "ETN", "DOV", "XYL", "SNA", "TTC", "MAS", "LII",
    "AOS", "MLM", "VMC", "NUE", "STLD", "FCX", "FMC", "CF", "MOS", "ALB",
    "DAL", "UAL", "LUV", "AAL", "JBHT", "CHRW", "EXPD", "XPO", "URI", "WAB",
    "GNRC", "TDG", "HWM", "HII", "TXT", "AXON", "BLDR", "BR", "CMI", "CPAY",
    "EFX", "FTV", "GEHC", "GEV", "HUBB", "J", "LHX", "NDSN", "PNR", "ROL",
    "ROP", "SWK", "TDY", "VLTO", "WST", "WTW",
    
    # Communication Services (25)
    "DIS", "CMCSA", "T", "VZ", "TMUS", "CHTR", "EA", "TTWO", "WBD", "PARA",
    "FOX", "FOXA", "OMC", "IPG", "LYV", "MTCH", "RBLX", "SPOT", "ROKU", "ZM",
    "NWS", "NWSA",
    
    # Real Estate (32)
    "PLD", "AMT", "EQIX", "CCI", "PSA", "SPG", "O", "WELL", "AVB", "EQR",
    "DLR", "ARE", "VTR", "BXP", "PEAK", "VICI", "INVH", "MAA", "UDR", "HST",
    "CBRE", "JLL", "ESS", "CPT", "KIM", "REG", "FRT", "NNN", "WY", "IRM",
    "DOC", "EXR", "SBAC",
    
    # Materials (28)
    "LIN", "APD", "SHW", "ECL", "PPG", "DD", "EMN", "CE", "RPM", "AVY",
    "SEE", "PKG", "IP", "WRK", "BALL", "NEM", "GOLD", "AEM", "AMCR", "CTVA",
    "DOW", "IFF", "LYB", "GLW",
    
    # Additional/Recent additions
    "ADP", "ALLE", "CSGP", "DAY", "EG", "IEX", "JKHY", "PAYX", "PFG", "QRVO",
    "SOLV", "TECH", "TEL",
]

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def delivery_report(err, msg):
    """Callback for message delivery reports."""
    if err is not None:
        print(f'❌ Delivery failed: {err}')


def calculate_momentum_score(price, open_price, prev_close, volume, avg_volume, high, low):
    """Calculate the 5-criteria momentum score."""
    score = 0
    criteria = {}
    
    # Calculate metrics
    pct_change = ((price - prev_close) / prev_close * 100) if prev_close > 0 else 0
    rel_volume = (volume / avg_volume) if avg_volume > 0 else 1
    range_pct = ((high - low) / price * 100) if price > 0 else 0
    
    # Criterion 1: Price $5-$500
    criteria['price_ok'] = bool(5 <= price <= 500)
    if criteria['price_ok']:
        score += 1
    
    # Criterion 2: Change >= 0.5%
    criteria['change_ok'] = bool(pct_change >= 0.5)
    if criteria['change_ok']:
        score += 1
    
    # Criterion 3: Relative Volume >= 1.0x
    criteria['volume_ok'] = bool(rel_volume >= 1.0)
    if criteria['volume_ok']:
        score += 1
    
    # Criterion 4: Momentum (Price > Open)
    criteria['momentum_ok'] = bool(price > open_price)
    if criteria['momentum_ok']:
        score += 1
    
    # Criterion 5: Volatility >= 0.5%
    criteria['volatility_ok'] = bool(range_pct >= 0.5)
    if criteria['volatility_ok']:
        score += 1
    
    return score, criteria, pct_change, rel_volume, range_pct


def detect_bull_flag(hist, lookback=20):
    """Detect bull flag pattern in historical data."""
    if hist is None or len(hist) < lookback:
        return {'detected': False}
    
    try:
        recent = hist.tail(lookback)
        closes = recent['Close'].values
        highs = recent['High'].values
        lows = recent['Low'].values
        volumes = recent['Volume'].values
        
        # Pole: First 40% | Flag: Last 60%
        pole_end = int(lookback * 0.4)
        
        if pole_end < 3:
            return {'detected': False}
        
        pole_data = closes[:pole_end]
        flag_data = closes[pole_end:]
        flag_highs = highs[pole_end:]
        flag_lows = lows[pole_end:]
        
        # Calculate characteristics
        pole_return = ((pole_data[-1] - pole_data[0]) / pole_data[0] * 100) if pole_data[0] > 0 else 0
        flag_range = ((max(flag_data) - min(flag_data)) / np.mean(flag_data) * 100) if len(flag_data) > 0 else 100
        
        pole_vol = float(np.mean(volumes[:pole_end]))
        flag_vol = float(np.mean(volumes[pole_end:]))
        vol_decrease = flag_vol < pole_vol
        
        # Bull Flag (adapted for S&P 500 large-caps): 1.5%+ pole, <7% flag range, volume decrease
        pattern_detected = pole_return > 1.5 and flag_range < 7 and vol_decrease
        
        entry_price = float(max(flag_highs)) if len(flag_highs) > 0 else 0
        stop_loss = float(min(flag_lows)) if len(flag_lows) > 0 else 0
        risk = entry_price - stop_loss
        target = entry_price + (risk * 2) if risk > 0 else 0
        
        return {
            'detected': bool(pattern_detected),
            'pole_return': round(float(pole_return), 2),
            'flag_range': round(float(flag_range), 2),
            'vol_decrease': bool(vol_decrease),
            'entry': round(entry_price, 2),
            'stop': round(stop_loss, 2),
            'target': round(target, 2)
        }
    except Exception as e:
        return {'detected': False}


def fetch_stock_data(symbol):
    """Fetch real-time stock data from Yahoo Finance."""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        hist = ticker.history(period="60d")
        
        if hist.empty:
            return None
        
        # Current data - convert to Python native types
        price = float(info.get('currentPrice') or info.get('regularMarketPrice') or 0)
        open_price = float(info.get('open') or info.get('regularMarketOpen') or 0)
        prev_close = float(info.get('previousClose') or info.get('regularMarketPreviousClose') or 0)
        volume = int(info.get('volume') or info.get('regularMarketVolume') or 0)
        high = float(info.get('dayHigh') or info.get('regularMarketDayHigh') or 0)
        low = float(info.get('dayLow') or info.get('regularMarketDayLow') or 0)
        
        # Handle missing values
        if not price or price == 0:
            return None
        if not prev_close or prev_close == 0:
            prev_close = price
        if not open_price or open_price == 0:
            open_price = price
            
        # Calculate 50-day average volume
        avg_volume = float(hist['Volume'].tail(50).mean()) if len(hist) >= 20 else float(volume)
        
        # Calculate momentum score
        score, criteria, pct_change, rel_volume, range_pct = calculate_momentum_score(
            price, open_price, prev_close, volume, avg_volume, high, low
        )
        
        # Detect bull flag pattern
        bull_flag = detect_bull_flag(hist)
        
        data = {
            'symbol': symbol,
            'price': round(price, 2),
            'open': round(open_price, 2),
            'prev_close': round(prev_close, 2),
            'change_pct': round(pct_change, 2),
            'volume': volume,
            'avg_volume': int(avg_volume),
            'rel_volume': round(rel_volume, 2),
            'day_high': round(high, 2),
            'day_low': round(low, 2),
            'range_pct': round(range_pct, 2),
            'score': int(score),
            'criteria': criteria,
            'bull_flag': bull_flag,
            'timestamp': datetime.now().isoformat(),
        }
        
        return data
        
    except Exception as e:
        return None


# =============================================================================
# MAIN PRODUCER
# =============================================================================

def main():
    print("=" * 60)
    print("🚀 MomentumFlow AI - Kafka Producer (Full S&P 500)")
    print("=" * 60)
    print(f"Bootstrap: {KAFKA_CONFIG['bootstrap.servers']}")
    print(f"Topic: {TOPIC_NAME}")
    print(f"Stocks: {len(SP500_STOCKS)} symbols")
    print("=" * 60)
    
    # Create producer
    producer = Producer(KAFKA_CONFIG)
    
    print("\n📡 Starting to stream stock data...\n")
    
    cycle = 1
    while True:
        print(f"\n{'='*60}")
        print(f"--- Cycle {cycle} @ {datetime.now().strftime('%H:%M:%S')} ---")
        
        success_count = 0
        high_score_stocks = []
        bull_flag_stocks = []
        
        for i, symbol in enumerate(SP500_STOCKS):
            data = fetch_stock_data(symbol)
            
            if data:
                # Send to Kafka
                producer.produce(
                    topic=TOPIC_NAME,
                    key=symbol.encode('utf-8'),
                    value=json.dumps(data).encode('utf-8'),
                    callback=delivery_report
                )
                success_count += 1
                
                # Track high scorers
                if data['score'] >= 4:
                    high_score_stocks.append(f"{symbol}({data['score']})")
                
                # Track bull flags
                if data['bull_flag'].get('detected') and data['score'] >= 3:
                    bull_flag_stocks.append(symbol)
                
                # Progress indicator every 50 stocks
                if (i + 1) % 50 == 0:
                    print(f"  Processed {i + 1}/{len(SP500_STOCKS)} stocks...")
            
            # Small delay to avoid rate limiting
            time.sleep(0.05)
        
        # Flush messages
        producer.flush()
        
        # Summary
        print(f"\n✅ Cycle {cycle} complete: {success_count}/{len(SP500_STOCKS)} stocks sent")
        
        if high_score_stocks:
            print(f"🌟 High scorers (4+): {len(high_score_stocks)} stocks")
            print(f"   {', '.join(high_score_stocks[:15])}{'...' if len(high_score_stocks) > 15 else ''}")
        
        if bull_flag_stocks:
            print(f"🚩 Bull Flags detected: {', '.join(bull_flag_stocks)}")
        
        print(f"\n⏳ Waiting 120 seconds before next cycle...")
        cycle += 1
        time.sleep(120)  # 2 minutes between cycles for 450 stocks


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Producer stopped by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
