import os
import time
from datetime import datetime
import pytz
import requests
import yfinance as yf

# Render च्या Environment Variable मधून Webhook URL घेईल (किंवा इथे थेट टाकू शकता)
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "YOUR_DISCORD_WEBHOOK_URL_HERE")

TICKERS = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS"]

def is_market_open():
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    
    if now.weekday() >= 5: # शनिवार-रविवार सुट्टी
        return False
        
    market_start = now.replace(hour=9, minute=15, second=0, microsecond=0)
    market_end = now.replace(hour=15, minute=30, second=0, microsecond=0)
    
    return market_start <= now <= market_end

def get_live_market_data():
    message = "🔴 **LIVE Nifty Volume & Zone Updates** 🔴\n\n"
    
    for ticker in TICKERS:
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period="1d", interval="5m")
            
            if data.empty:
                continue
                
            current_price = data['Close'].iloc[-1]
            latest_volume = data['Volume'].iloc[-1]
            avg_volume = data['Volume'].rolling(window=10).mean().iloc[-1]
            
            zone_status = "⚡ Normal Volume"
            if latest_volume > (avg_volume * 1.8):
                zone_status = "🔥 High Volume Spurt (Near Demand/Supply Zone)"
                
            symbol_name = ticker.replace('.NS', '')
            message += f"🔹 **{symbol_name}**\n"
            message += f"   • Price: ₹{current_price:.2f}\n"
            message += f"   • Status: {zone_status}\n\n"
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
            
    return message

def send_to_discord(message):
    data = {"content": message}
    requests.post(DISCORD_WEBHOOK_URL, json=data)

if __name__ == "__main__":
    print("Stock Bot started on Render...")
    while True:
        if is_market_open():
            try:
                msg = get_live_market_data()
                send_to_discord(msg)
            except Exception as e:
                print(f"Loop Error: {e}")
            
            time.sleep(300) # ५ मिनिटे थांबा
        else:
            print("Market is closed. Waiting...")
            time.sleep(900) # १५ मिनिटे थांबा