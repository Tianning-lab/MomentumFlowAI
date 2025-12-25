"""
================================================================================
KAFKA NEWS PRODUCER - Google News Streaming
MomentumFlow AI - Confluent AI Partner Catalyst Hackathon
New Way Capital Advisory Limited © 2025
================================================================================

This producer fetches stock-specific news from Google News RSS feed and streams
it to Confluent Kafka for real-time consumption by the Shiny dashboard.

FEATURES:
- Fetches news for S&P 500 stocks using Google News RSS
- Filters for stock-specific news using company name + ticker
- Streams to Kafka topic 'stock_news'
- Cycles through stocks continuously
- Includes sentiment hints from headline analysis

USAGE:
    python kafka_news_producer.py

REQUIREMENTS:
    pip install confluent-kafka feedparser requests

================================================================================
"""

import json
import time
import feedparser
import requests
from datetime import datetime, timezone
from confluent_kafka import Producer
import re
import html

# =============================================================================
# CONFLUENT KAFKA CONFIGURATION
# =============================================================================

KAFKA_CONFIG = {
    'bootstrap.servers': 'pkc-lzoyy.europe-west6.gcp.confluent.cloud:9092',
    'security.protocol': 'SASL_SSL',
    'sasl.mechanisms': 'PLAIN',
    'sasl.username': 'YOUR_API_KEY',      # <-- Replace with your API Key
    'sasl.password': 'YOUR_API_SECRET',   # <-- Replace with your API Secret
    'client.id': 'momentumflow-news-producer'
}

NEWS_TOPIC = 'stock_news'

# =============================================================================
# STOCK SYMBOLS WITH COMPANY NAMES (for better Google News search)
# =============================================================================

# Map of ticker -> company name for accurate news search
STOCK_INFO = {
    # Top momentum stocks (prioritized for news)
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "GOOGL": "Google Alphabet",
    "AMZN": "Amazon",
    "NVDA": "NVIDIA",
    "META": "Meta Facebook",
    "TSLA": "Tesla",
    "AMD": "AMD Advanced Micro Devices",
    "NFLX": "Netflix",
    "CRM": "Salesforce",
    
    # Finance
    "JPM": "JPMorgan Chase",
    "BAC": "Bank of America",
    "C": "Citigroup",
    "GS": "Goldman Sachs",
    "MS": "Morgan Stanley",
    "WFC": "Wells Fargo",
    "V": "Visa",
    "MA": "Mastercard",
    "AXP": "American Express",
    "BLK": "BlackRock",
    
    # Healthcare
    "UNH": "UnitedHealth",
    "JNJ": "Johnson Johnson",
    "PFE": "Pfizer",
    "ABBV": "AbbVie",
    "MRK": "Merck",
    "LLY": "Eli Lilly",
    "TMO": "Thermo Fisher",
    "ABT": "Abbott",
    "BMY": "Bristol Myers",
    "AMGN": "Amgen",
    
    # Consumer
    "WMT": "Walmart",
    "HD": "Home Depot",
    "MCD": "McDonald's",
    "NKE": "Nike",
    "SBUX": "Starbucks",
    "TGT": "Target",
    "COST": "Costco",
    "LOW": "Lowe's",
    "DIS": "Disney",
    "CMCSA": "Comcast",
    
    # Energy
    "XOM": "Exxon Mobil",
    "CVX": "Chevron",
    "COP": "ConocoPhillips",
    "SLB": "Schlumberger",
    "OXY": "Occidental Petroleum",
    "MPC": "Marathon Petroleum",
    "VLO": "Valero Energy",
    "PSX": "Phillips 66",
    "EOG": "EOG Resources",
    "HAL": "Halliburton",
    
    # Industrials
    "CAT": "Caterpillar",
    "BA": "Boeing",
    "HON": "Honeywell",
    "UNP": "Union Pacific",
    "UPS": "UPS",
    "RTX": "Raytheon",
    "LMT": "Lockheed Martin",
    "GE": "General Electric",
    "MMM": "3M",
    "DE": "John Deere",
    
    # Technology extras
    "INTC": "Intel",
    "QCOM": "Qualcomm",
    "TXN": "Texas Instruments",
    "AVGO": "Broadcom",
    "ORCL": "Oracle",
    "CSCO": "Cisco",
    "IBM": "IBM",
    "ADBE": "Adobe",
    "NOW": "ServiceNow",
    "INTU": "Intuit",
    
    # Communication
    "T": "AT&T",
    "VZ": "Verizon",
    "TMUS": "T-Mobile",
    
    # Real Estate
    "AMT": "American Tower",
    "PLD": "Prologis",
    "CCI": "Crown Castle",
    "EQIX": "Equinix",
    "SPG": "Simon Property",
    
    # Utilities
    "NEE": "NextEra Energy",
    "DUK": "Duke Energy",
    "SO": "Southern Company",
    "D": "Dominion Energy",
    "AEP": "American Electric Power",
}

# =============================================================================
# GOOGLE NEWS FETCHER
# =============================================================================

def clean_html(text):
    """Remove HTML tags and decode entities"""
    clean = re.sub(r'<[^>]+>', '', text)
    clean = html.unescape(clean)
    return clean.strip()

def analyze_sentiment(headline):
    """Simple sentiment analysis based on keywords"""
    headline_lower = headline.lower()
    
    bullish_words = ['surge', 'soar', 'jump', 'rally', 'gain', 'rise', 'up', 'high', 
                     'buy', 'upgrade', 'beat', 'strong', 'growth', 'profit', 'record',
                     'outperform', 'bullish', 'positive', 'boom', 'breakout']
    
    bearish_words = ['fall', 'drop', 'sink', 'plunge', 'crash', 'down', 'low', 
                     'sell', 'downgrade', 'miss', 'weak', 'loss', 'decline', 'cut',
                     'underperform', 'bearish', 'negative', 'warning', 'risk']
    
    bullish_count = sum(1 for word in bullish_words if word in headline_lower)
    bearish_count = sum(1 for word in bearish_words if word in headline_lower)
    
    if bullish_count > bearish_count:
        return "bullish"
    elif bearish_count > bullish_count:
        return "bearish"
    else:
        return "neutral"

def fetch_google_news(symbol, company_name, max_items=5):
    """
    Fetch news from Google News RSS for a specific stock
    """
    try:
        # Build search query: "Company Name" stock OR ticker
        search_query = f'"{company_name}" stock OR {symbol}'
        encoded_query = requests.utils.quote(search_query)
        
        # Google News RSS URL
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
        
        # Parse RSS feed
        feed = feedparser.parse(rss_url)
        
        news_items = []
        
        for entry in feed.entries[:max_items]:
            # Extract and clean data
            title = clean_html(entry.get('title', ''))
            link = entry.get('link', '')
            
            # Parse publication date
            pub_date = entry.get('published', '')
            try:
                # Google News format: "Tue, 24 Dec 2024 10:30:00 GMT"
                pub_datetime = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %Z")
                pub_timestamp = pub_datetime.isoformat()
                
                # Calculate time ago
                now = datetime.now(timezone.utc)
                pub_datetime = pub_datetime.replace(tzinfo=timezone.utc)
                diff = now - pub_datetime
                
                if diff.total_seconds() < 3600:
                    time_ago = f"{int(diff.total_seconds() / 60)}m ago"
                elif diff.total_seconds() < 86400:
                    time_ago = f"{int(diff.total_seconds() / 3600)}h ago"
                else:
                    time_ago = f"{int(diff.total_seconds() / 86400)}d ago"
            except:
                pub_timestamp = datetime.now(timezone.utc).isoformat()
                time_ago = "recent"
            
            # Extract source from title (Google News format: "Title - Source")
            source = "Google News"
            if ' - ' in title:
                parts = title.rsplit(' - ', 1)
                if len(parts) == 2:
                    title = parts[0]
                    source = parts[1]
            
            # Analyze sentiment
            sentiment = analyze_sentiment(title)
            
            news_items.append({
                'symbol': symbol,
                'company': company_name,
                'title': title,
                'source': source,
                'link': link,
                'published': pub_timestamp,
                'time_ago': time_ago,
                'sentiment': sentiment,
                'fetched_at': datetime.now(timezone.utc).isoformat()
            })
        
        return news_items
        
    except Exception as e:
        print(f"  ⚠️  Error fetching news for {symbol}: {e}")
        return []

# =============================================================================
# KAFKA PRODUCER
# =============================================================================

def delivery_callback(err, msg):
    """Callback for Kafka message delivery"""
    if err:
        print(f"  ❌ Delivery failed: {err}")
    else:
        symbol = msg.key().decode('utf-8') if msg.key() else 'unknown'
        print(f"  ✓ News delivered for {symbol}")

def create_producer():
    """Create Kafka producer instance"""
    return Producer(KAFKA_CONFIG)

def produce_news(producer, news_item):
    """Send news item to Kafka topic"""
    try:
        producer.produce(
            topic=NEWS_TOPIC,
            key=news_item['symbol'].encode('utf-8'),
            value=json.dumps(news_item).encode('utf-8'),
            callback=delivery_callback
        )
    except Exception as e:
        print(f"  ❌ Error producing message: {e}")

# =============================================================================
# MAIN LOOP
# =============================================================================

def main():
    print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║   📰 KAFKA NEWS PRODUCER - Google News Streaming                              ║
║   MomentumFlow AI | Confluent AI Partner Catalyst Hackathon                   ║
║   © 2025 New Way Capital Advisory Limited                                     ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    print(f"🔧 Configuration:")
    print(f"   Kafka Topic: {NEWS_TOPIC}")
    print(f"   Stocks to Monitor: {len(STOCK_INFO)}")
    print(f"   News Source: Google News RSS")
    print()
    
    # Create Kafka producer
    print("📡 Connecting to Confluent Kafka...")
    producer = create_producer()
    print("✅ Connected!\n")
    
    cycle = 0
    
    try:
        while True:
            cycle += 1
            print(f"\n{'='*70}")
            print(f"📰 NEWS CYCLE {cycle} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*70}\n")
            
            total_news = 0
            
            for symbol, company in STOCK_INFO.items():
                print(f"🔍 Fetching news for {symbol} ({company})...")
                
                news_items = fetch_google_news(symbol, company, max_items=3)
                
                if news_items:
                    for item in news_items:
                        produce_news(producer, item)
                        total_news += 1
                    
                    # Show sample headline
                    sentiment_icon = {"bullish": "📈", "bearish": "📉", "neutral": "➖"}
                    print(f"   {sentiment_icon.get(news_items[0]['sentiment'], '➖')} {news_items[0]['title'][:60]}...")
                else:
                    print(f"   (no recent news)")
                
                # Flush periodically
                producer.poll(0)
                
                # Rate limit: be nice to Google
                time.sleep(1)
            
            # Ensure all messages are sent
            producer.flush()
            
            print(f"\n✅ Cycle {cycle} complete: {total_news} news items streamed")
            print(f"⏳ Waiting 5 minutes before next cycle...")
            print(f"   (Press Ctrl+C to stop)\n")
            
            # Wait 5 minutes between cycles (news doesn't update that fast)
            time.sleep(300)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down gracefully...")
        producer.flush()
        print("✅ All pending messages delivered. Goodbye!")

if __name__ == "__main__":
    main()
