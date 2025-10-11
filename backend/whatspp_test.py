# notifications/whatsapp_notify.py
import os
import logging
from twilio.rest import Client
import time

# Twilio credentials
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
FARMER_WHATSAPP_NUMBER = os.getenv('FARMER_WHATSAPP_NUMBER')


# In whatsapp_notify.py, add this if you need proxy:
import os
os.environ['HTTP_PROXY'] = 'http://your-proxy:port'
os.environ['HTTPS_PROXY'] = 'https://your-proxy:port'

def send_whatsapp_twilio(message, max_retries=2):
    """Send WhatsApp message via Twilio with retry logic"""
    
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, FARMER_WHATSAPP_NUMBER]):
        logging.error("Twilio credentials not properly set")
        return False
    
    for attempt in range(max_retries):
        try:
            logging.info(f"Attempting to send WhatsApp message (attempt {attempt + 1})")
            
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            
            # Add timeout to the request
            msg = client.messages.create(
                body=message,
                from_=f"whatsapp:{TWILIO_PHONE_NUMBER}",
                to=f"whatsapp:{FARMER_WHATSAPP_NUMBER}",
                timeout=30  # 30 second timeout
            )
            
            logging.info(f"WhatsApp message sent successfully. SID: {msg.sid}")
            return True
            
        except Exception as e:
            logging.warning(f"WhatsApp attempt {attempt + 1} failed: {e}")
            
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 5  # 5, 10 seconds
                logging.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                logging.error("All WhatsApp sending attempts failed")
                return False
    
    return False