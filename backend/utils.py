# utils.py

import os
import json
import sys
import base64
from pathlib import Path
from dotenv import load_dotenv

# ==============================================================================
#  SECTION 1: API KEYS & CONFIGURATION LOADING
# ==============================================================================

# Load environment variables from a .env file
load_dotenv()

def get_env_variable(var_name, default=None):
    """Safely retrieves an environment variable."""
    return os.getenv(var_name, default)

# --- API Keys ---
GROQ_API_KEY = get_env_variable("GROQ_API_KEY")
TAVILY_API_KEY = get_env_variable("TAVILY_API_KEY")
OPENWEATHER_API_KEY = get_env_variable("OPENWEATHER_API_KEY")



TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
FARMER_WHATSAPP_NUMBER = os.getenv("FARMER_WHATSAPP_NUMBER")

# --- Default values ---
DEFAULT_LOCATION = "India"  # Fallback location


# ==============================================================================
#  SECTION 2: LEAF DISEASE DETECTOR SETUP
# ==============================================================================

# This block is crucial for finding your LeafDiseaseDetector class.
# It temporarily adds the 'Leaf Disease' subdirectory to Python's path.
try:
    sys.path.insert(0, str(Path(__file__).resolve().parent / "Leaf Disease"))
    from main import LeafDiseaseDetector
except ImportError as e:
    print(f"FATAL ERROR: Could not import LeafDiseaseDetector from 'Leaf Disease/main.py'. "
          f"Please check your folder structure. Error: {e}")
    # In a real app, you might want to handle this more gracefully
    LeafDiseaseDetector = None
except Exception as e:
    print(f"An unexpected error occurred during LeafDiseaseDetector import: {e}")
    LeafDiseaseDetector = None


# ==============================================================================
#  SECTION 3: IMAGE PROCESSING FUNCTIONS FOR THE AGENT
# ==============================================================================

def test_with_base64_data(base64_image_string: str) -> dict | None:
    """
    Initializes the detector and analyzes a base64 encoded image string.

    Args:
        base64_image_string (str): Base64 encoded image data.

    Returns:
        A dictionary with the analysis result or None on error.
    """
    if LeafDiseaseDetector is None:
        return {"error": "LeafDiseaseDetector is not available due to an import error."}
    
    try:
        detector = LeafDiseaseDetector()
        result = detector.analyze_leaf_image_base64(base64_image_string)
        return result
    except Exception as e:
        print(f"Error during base64 image analysis: {e}")
        return {"error": str(e)}


def convert_image_to_base64_and_test(image_bytes: bytes) -> dict | None:
    """
    Converts raw image bytes to a base64 string and sends it for analysis.
    This is the main function that your image_agent.py will call.

    Args:
        image_bytes (bytes): Image data in bytes.

    Returns:
        A dictionary with the analysis result or None on error.
    """
    try:
        if not image_bytes:
            print("Error: No image bytes provided to convert.")
            return {"error": "No image bytes provided"}

        # Encode the bytes into a base64 string
        base64_string = base64.b64encode(image_bytes).decode('utf-8')
        
        # Call the analysis function
        return test_with_base64_data(base64_string)
    except Exception as e:
        print(f"Error during image to base64 conversion: {e}")
        return {"error": str(e)}


# ==============================================================================
#  SECTION 4: DIRECT EXECUTION TEST BLOCK
# ==============================================================================

if __name__ == "__main__":
    """
    This block runs only when you execute `python utils.py` directly.
    It's useful for testing the image processing functions independently.
    """
    # Define a path to a test image
    # IMPORTANT: Make sure this image path is correct relative to your project root
    test_image_path = "Media/brown-spot-4 (1).jpg" 

    print(f"--- Running test with image: {test_image_path} ---")

    if not os.path.exists(test_image_path):
        print(f"Error: Test image not found at '{test_image_path}'. Please check the path.")
    else:
        # ### CORRECTED ###
        # The function expects bytes, so we must read the file in binary mode ("rb")
        with open(test_image_path, "rb") as f:
            image_file_bytes = f.read()
        
        # Now, call the function with the image bytes
        test_result = convert_image_to_base64_and_test(image_file_bytes)
        
        print("\n--- Test Result ---")
        if test_result:
            # Pretty-print the JSON result
            print(json.dumps(test_result, indent=2))
        else:
            print("Test failed to produce a result.")