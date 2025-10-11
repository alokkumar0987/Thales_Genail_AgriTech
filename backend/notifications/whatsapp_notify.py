import os
import time
from twilio.rest import Client
import requests
from datetime import datetime

# Twilio credentials
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
FARMER_WHATSAPP_NUMBER = os.getenv('FARMER_WHATSAPP_NUMBER')

# Telegram credentials (from utils)
from utils import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

def send_whatsapp_twilio(message, max_retries=2):
    """Send WhatsApp message via Twilio with length checking"""
    
    # Check message length first
    if len(message) > 1600:
        print(f"⚠️ Message too long ({len(message)} chars). Creating short version...")
        message = create_short_summary()
    
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, FARMER_WHATSAPP_NUMBER]):
        print("❌ Twilio credentials not set")
        return False
    
    for attempt in range(max_retries):
        try:
            print(f"📱 Sending WhatsApp (attempt {attempt + 1})")
            
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            
            msg = client.messages.create(
                body=message,
                from_=f"whatsapp:{TWILIO_PHONE_NUMBER}",
                to=f"whatsapp:{FARMER_WHATSAPP_NUMBER}"
            )
            
            print("✅ WhatsApp message delivered!")
            return True
            
        except Exception as e:
            error_str = str(e)
            if "1600 character limit" in error_str:
                print("❌ Message still too long. Using ultra-short version...")
                message = create_ultra_short_message()
                continue
                
            print(f"❌ WhatsApp attempt {attempt + 1} failed: {e}")
            
            if attempt < max_retries - 1:
                wait_time = 10
                print(f"⏳ Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
    
    return False

def send_telegram_message(message, max_retries=2):
    """Send message via Telegram bot with error handling"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ Telegram credentials not set")
        return False
    
    for attempt in range(max_retries):
        try:
            print(f"📲 Sending Telegram (attempt {attempt + 1})")
            
            # Truncate message if too long for Telegram (4096 characters)
            if len(message) > 4096:
                message = message[:4090] + "..."
                print(f"⚠️ Message truncated to {len(message)} chars for Telegram")
            
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "Markdown"
            }
            
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            print("✅ Telegram message sent successfully")
            return True
            
        except Exception as e:
            print(f"❌ Telegram attempt {attempt + 1} failed: {e}")
            
            if attempt < max_retries - 1:
                wait_time = 10
                print(f"⏳ Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
    
    return False

def create_short_summary():
    """Create short summary for WhatsApp"""
    return f"""
🌾 किसान सलाह - इंदौर

मौसम: 26°C, सूखा
बाजार: गेहूं ₹2,250-2,350
सलाह: चना बुवाई पूरी करें

पूरी जानकारी Telegram पर उपलब्ध।
{datetime.now().strftime('%d/%m %H:%M')}
"""

def create_ultra_short_message():
    """Create ultra-short message that definitely fits"""
    return "🌾 इंदौर: गेहूं बुवाई तैयारी, मौसम सूखा " + datetime.now().strftime('%d/%m %H:%M')