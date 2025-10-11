import asyncio
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Import agents with fallbacks
try:
    from weather_agent import get_weather_alerts
except ImportError:
    def get_weather_alerts(location): return None

try:
    from market_agent import get_market_prices  
except ImportError:
    def get_market_prices(): return None

try:
    from soil_agent import get_soil_advice
except ImportError:
    def get_soil_advice(location): return None

try:
    from location_agent import get_location_info
except ImportError:
    def get_location_info(location): return None

# Notification functions
def send_telegram_message(message):
    try:
        from notifications.telegram_notify import send_telegram_message as telegram_send
        return telegram_send(message)
    except Exception:
        return False

def send_whatsapp_message(message):
    try:
        from notifications.whatsapp_notify import send_whatsapp_twilio as whatsapp_send
        return whatsapp_send(message)
    except Exception:
        return False

# Config
DEFAULT_LOCATION = "Indore, Madhya Pradesh"
TIMEZONE = "Asia/Kolkata"
NOTIFICATION_HOUR = 2
NOTIFICATION_MINUTE = 58

# Compact dummy data
def get_dummy_weather(location):
    return """🌤 मौसम - इंदौर
• तापमान: 26°C (max 30°C)
• हवा: 8-12 km/h  
• बारिश: 0 mm (3 दिन सूखा)
• चना बुवाई का उत्तम समय"""

def get_dummy_market_prices():
    return """ इंदौर मंडी भाव
• गेहूं: ₹2,250-2,350/क्विंटल
• सोयाबीन: ₹3,800-4,100
• चना भाव मजबूत, बिक्री के लिए अच्छा"""

def get_dummy_soil_advice(location):
    return """ मिट्टी - इंदौर
• प्रकार: काली मिट्टी
• pH: 7.2-7.8  
• नमी: 45%
• हल्की सिंचाई करें"""

def get_dummy_location_advice(location):
    return """ इंदौर सलाह
• गेहूं बुवाई: नवंबर पहले पखवाड़े
• चना बुवाई: अक्टूबर अंत तक
• प्रधानमंत्री किसान सम्मान निधि"""

async def async_call_with_timeout(func, *args, timeout=20, **kwargs):
    try:
        return await asyncio.wait_for(
            asyncio.to_thread(func, *args, **kwargs), timeout=timeout
        )
    except Exception:
        return None

async def collect_data():
    """Collect all farmer data with fallbacks"""
    data = {}
    
    agents = [
        ('weather', get_weather_alerts, get_dummy_weather),
        ('market', get_market_prices, get_dummy_market_prices), 
        ('soil', get_soil_advice, get_dummy_soil_advice),
        ('location', get_location_info, get_dummy_location_advice)
    ]
    
    for name, real_func, dummy_func in agents:
        try:
            if name == 'market':
                data[name] = await async_call_with_timeout(real_func) or dummy_func()
            else:
                data[name] = await async_call_with_timeout(real_func, DEFAULT_LOCATION) or dummy_func(DEFAULT_LOCATION)
            print(f" {name} data ready")
        except Exception:
            data[name] = dummy_func(DEFAULT_LOCATION) if name != 'market' else dummy_func()
            print(f" {name} failed, using dummy")
    
    return data

def create_whatsapp_message(data):
    """Compact message for WhatsApp (~500 chars)"""
    return f"""🌾 किसान सलाह - इंदौर

 {data['weather'].split('•')[0].replace('🌤 मौसम - इंदौर', 'मौसम')}
• तापमान: 26°C | हवा: 8-12 km/h

 {data['market'].split('•')[1]}
• {data['market'].split('•')[2]}

 {data['soil'].split('•')[1]}
• {data['soil'].split('•')[3]}

 इस सप्ताह:
• गेहूं बुवाई तैयारी
• चना बुवाई जारी रखें

     हेल्पलाइन: 1800-180-1551
    {datetime.now(ZoneInfo(TIMEZONE)).strftime('%d/%m/%Y %H:%M')}"""

def create_telegram_message(data):
    """Detailed message for Telegram"""
    return f"""🌾 *किसान सलाह - इंदौर*

{data['weather']}

{data['market']}

{data['soil']}

{data['location']}

    {datetime.now(ZoneInfo(TIMEZONE)).strftime('%d/%m/%Y %H:%M')}"""

async def daily_summary_loop():
    print(" Starting farmer advisory system...")
    
    while True:
        now = datetime.now(ZoneInfo(TIMEZONE))
        target = now.replace(hour=NOTIFICATION_HOUR, minute=NOTIFICATION_MINUTE, second=0, microsecond=0)
        
        if target <= now:
            target += timedelta(days=1)
            
        wait_seconds = (target - now).total_seconds()
        print(f" Next notification at {target.strftime('%H:%M')} IST")
        await asyncio.sleep(wait_seconds)

        try:
            print("\n" + "="*40)
            print(f" Generating daily summary")
            print("="*40)
            
            data = await collect_data()
            
            whatsapp_msg = create_whatsapp_message(data)
            telegram_msg = create_telegram_message(data)
            
            print(f" WhatsApp: {len(whatsapp_msg)} chars")
            print(f" Telegram: {len(telegram_msg)} chars")
            
            telegram_success = send_telegram_message(telegram_msg)
            whatsapp_success = send_whatsapp_message(whatsapp_msg)
            
            print(f" Sent. Telegram: {'✓' if telegram_success else '✗'}, WhatsApp: {'✓' if whatsapp_success else '✗'}")
                
        except Exception as e:
            print(f" Error: {e}")
            await asyncio.sleep(300)

def start_scheduler():
    try:
        asyncio.run(daily_summary_loop())
    except KeyboardInterrupt:
        print("\n System stopped")

if __name__ == "__main__":
    start_scheduler()