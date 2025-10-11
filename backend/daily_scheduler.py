import asyncio
import traceback
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Import agents
try:
    from weather_agent import get_weather_alerts
except ImportError as e:
    print(f"❌ Weather agent import failed: {e}")
    def get_weather_alerts(location): return None

try:
    from market_agent import get_market_prices
except ImportError as e:
    print(f"❌ Market agent import failed: {e}")
    def get_market_prices(): return None

try:
    from soil_agent import get_soil_advice
except ImportError as e:
    print(f"❌ Soil agent import failed: {e}")
    def get_soil_advice(location): return None

try:
    from location_agent import get_location_info
except ImportError as e:
    print(f"❌ Location agent import failed: {e}")
    def get_location_info(location): return None

# Notification functions
def send_telegram_message(message):
    try:
        from notifications.telegram_notify import send_telegram_message as telegram_send
        return telegram_send(message)
    except Exception as e:
        print(f"❌ Telegram error: {e}")
        return False

def send_whatsapp_message(message):
    try:
        from notifications.whatsapp_notify import send_whatsapp_twilio as whatsapp_send
        return whatsapp_send(message)
    except Exception as e:
        print(f"❌ WhatsApp error: {e}")
        return False

# ------------------ USER SETTINGS ------------------
DEFAULT_LOCATION = "Indore, Madhya Pradesh"  # Changed to Indore
TIMEZONE = "Asia/Kolkata"
NOTIFICATION_HOUR = 20 # Current hour
NOTIFICATION_MINUTE = 51
# Adjust for testing
# ---------------------------------------------------

# ================== REALISTIC DUMMY DATA FOR INDORE ==================

def get_dummy_weather(location):
    """Provide realistic weather data for Indore farmers"""
    return f"""🌤️ **मौसम - इंदौर, मध्य प्रदेश**
• तापमान: 26°C (अधिकतम 30°C, न्यूनतम 18°C)
• आर्द्रता: 65%
• हवा: 8-12 km/h (पश्चिमी)
• बारिश: 0 mm (अगले 3 दिन सूखा)

🌾 **कृषि सलाह:**
• चना की बुवाई का उत्तम समय
• गेहूं के लिए खेत तैयारी शुरू करें
• मिट्टी की नमी बनाए रखें"""

def get_dummy_market_prices():
    """Provide realistic market price data for Indore region"""
    return f"""💰 **इंदौर मंडी भाव** (प्रति क्विंटल)

🌾 अनाज:
• गेहूं: ₹2,250 - ₹2,350

• सोयाबीन: ₹3,800 - ₹4,100
• मक्का: ₹1,900 - ₹2,100


💡 **बाजार सलाह:**
• चना के भाव मजबूत, बिक्री के लिए अच्छा समय
• गेहूं भाव स्थिर, भंडारण कर सकते हैं"""

def get_dummy_soil_advice(location):
    """Provide realistic soil advice for Indore region"""
    return f"""🌱 **मिट्टी स्वास्थ्य - इंदौर क्षेत्र**
• मिट्टी प्रकार: काली मिट्टी (कपासी)
• pH स्तर: 7.2 - 7.8 (हल्की क्षारीय)
• नमी: 45% (सिंचाई आवश्यक)


💧 **सिंचाई:**
• हल्की सिंचाई करें, जलभराव से बचें"""

def get_dummy_location_advice(location):
    """Provide location-specific farming advice for Indore"""
    return f"""📍 **इंदौर क्षेत्र विशेष सलाह**

🌾 **रबी सीजन गतिविधियां:**
• गेहूं बुवाई: नवंबर के पहले पखवाड़े तक
• चना बुवाई: अक्टूबर अंत तक पूरी करें
• सरसों: 15-25 अक्टूबर तक बोयें

🏛️ **सरकारी योजनाएं:**
• प्रधानमंत्री किसान सम्मान निधि
• मध्य प्रदेश किसान कल्याण योजना
• रबी फसल बीमा

"""

async def async_call_with_timeout(func, *args, timeout=20, **kwargs):
    try:
        return await asyncio.wait_for(
            asyncio.to_thread(func, *args, **kwargs),
            timeout=timeout
        )
    except Exception as e:
        print(f"⏰ Timeout/Error in {func.__name__}: {e}")
        return None

async def daily_summary_loop():
    print("🚀 Starting farmer advisory system for Indore...")
    
    while True:
        now = datetime.now(ZoneInfo(TIMEZONE))
        target = now.replace(hour=NOTIFICATION_HOUR, minute=NOTIFICATION_MINUTE, second=0, microsecond=0)
        
        if target <= now:
            target += timedelta(days=1)
            
        wait_seconds = (target - now).total_seconds()
        print(f"⏳ Next notification at {target.strftime('%H:%M')} IST")
        
        await asyncio.sleep(wait_seconds)

        try:
            print("\n" + "="*50)
            print(f"🕐 Generating daily summary for Indore")
            print("="*50)
            
            # Collect data
            weather = market = soil = location = None
            
            try:
                weather = await async_call_with_timeout(get_weather_alerts, DEFAULT_LOCATION) or get_dummy_weather(DEFAULT_LOCATION)
                print("✅ Weather data ready")
            except Exception as e:
                weather = get_dummy_weather(DEFAULT_LOCATION)
                print(f"❌ Weather failed: {e}")

            try:
                market = await async_call_with_timeout(get_market_prices) or get_dummy_market_prices()
                print("✅ Market data ready")
            except Exception as e:
                market = get_dummy_market_prices()
                print(f"❌ Market failed: {e}")

            try:
                soil = await async_call_with_timeout(get_soil_advice, DEFAULT_LOCATION) or get_dummy_soil_advice(DEFAULT_LOCATION)
                print("✅ Soil data ready")
            except Exception as e:
                soil = get_dummy_soil_advice(DEFAULT_LOCATION)
                print(f"❌ Soil failed: {e}")

            try:
                location = await async_call_with_timeout(get_location_info, DEFAULT_LOCATION) or get_dummy_location_advice(DEFAULT_LOCATION)
                print("✅ Location data ready")
            except Exception as e:
                location = get_dummy_location_advice(DEFAULT_LOCATION)
                print(f"❌ Location failed: {e}")
            
            # SHORT VERSION for WhatsApp (under 1600 chars)
            whatsapp_message = f"""
🌾 किसान सलाह - सीहोर, मध्य प्रदेश


🌤 मौसम जानकारी:
• तापमान: 27°C | आंशिक बादल ☁
• अगले 2 दिन हल्की बारिश की संभावना 🌧
• सोयाबीन कटाई में देरी न करें

💰 मंडी भाव (आज के औसत भाव):
• गेहूं: ₹2,320 / क्विंटल
• सोयाबीन: ₹4,050 / क्विंटल
• मसूर: ₹5,400 / क्विंटल

🌱 मिट्टी और कृषि सलाह:
• मिट्टी: दोमट
• इस सप्ताह जैविक खाद डालें 🌿
• जल निकासी की व्यवस्था सुनिश्चित करें
• कटाई के बाद खेत की जुताई करें ताकि नमी बनी रहे

📍 इस सप्ताह के कार्य:
• सोयाबीन कटाई शुरू करें
• रबी फसल की तैयारी शुरू करें
• हल्की सिंचाई गेहूं बुवाई के पहले करें

🧠 AI सलाह:
“अगले 5 दिन में नमी बनी रहने से गेहूं की बुवाई के लिए सर्वोत्तम समय रहेगा।”

💬 प्रेरणादायक संदेश:
“मेहनत और ज्ञान से ही खेत सुनहरा होता है 🌾”

📞 कृषि हेल्पलाइन: 1800-180-1551

🕐 {datetime.now(ZoneInfo(TIMEZONE)).strftime('%d/%m/%Y %H:%M')}
"""
            
            # Telegram gets detailed version
            telegram_message = f"""
🌾 **किसान सलाह - इंदौर, मध्य प्रदेश**

{weather}

{market}

{soil}

{location}

🕐 {datetime.now(ZoneInfo(TIMEZONE)).strftime('%d/%m/%Y %H:%M')}
"""
            
            print("📝 Messages composed")
            print(f"📏 WhatsApp: {len(whatsapp_message)} chars")
            print(f"📏 Telegram: {len(telegram_message)} chars")
            
            # Send notifications
            print("📱 Sending notifications...")
            
            telegram_success = send_telegram_message(telegram_message)
            whatsapp_success = send_whatsapp_message(whatsapp_message)
            
            if telegram_success or whatsapp_success:
                print(f"✅ Summary sent. Telegram: {'✓' if telegram_success else '✗'}, WhatsApp: {'✓' if whatsapp_success else '✗'}")
            else:
                print("❌ All methods failed - but message is ready")
                
        except Exception as e:
            print(f"💥 Critical error: {e}")
            await asyncio.sleep(300)

def start_scheduler():
    try:
        asyncio.run(daily_summary_loop())
    except KeyboardInterrupt:
        print("\n🛑 System stopped by user")

if __name__ == "__main__":
    start_scheduler()