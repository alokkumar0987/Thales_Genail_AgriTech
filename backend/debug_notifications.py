# debug_notifications.py
import traceback
from notifications.telegram_notify import send_telegram_message
from notifications.whatsapp_notify import send_whatsapp_twilio

def debug_notifications():
    test_message = "🔧 Debug test message"
    
    print("=== DEBUGGING NOTIFICATION SERVICES ===")
    
    # Check if modules can be imported
    try:
        from notifications.telegram_notify import send_telegram_message
        print("✅ Telegram module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Telegram module: {e}")
    
    try:
        from notifications.whatsapp_notify import send_whatsapp_twilio
        print("✅ WhatsApp module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import WhatsApp module: {e}")
    
    # Test message sending
    print("\n--- Testing Telegram ---")
    try:
        send_telegram_message(test_message)
        print("✅ Telegram message sent successfully!")
    except Exception as e:
        print(f"❌ Telegram failed: {e}")
        print("Stack trace:")
        traceback.print_exc()
    
    print("\n--- Testing WhatsApp ---")
    try:
        send_whatsapp_twilio(test_message)
        print("✅ WhatsApp message sent successfully!")
    except Exception as e:
        print(f"❌ WhatsApp failed: {e}")
        print("Stack trace:")
        traceback.print_exc()

if __name__ == "__main__":
    debug_notifications()