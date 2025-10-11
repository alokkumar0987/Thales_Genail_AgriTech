
from market_agent import get_market_prices
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

def main():
    """
    Runs a series of test cases to check the functionality
    of the get_market_prices tool from market_agent.py.
    """
    print("Starting market price analysis tests...")

    # Test Case 1: Wheat prices in a specific location (Delhi)
    print("\n=== Requesting Market Price Analysis for Wheat in Delhi ===")
    try:
        # The .invoke() method is the standard way to run LangChain tools
        result_wheat = get_market_prices.invoke({"crop_type": "wheat", "location": "Delhi"})
        print("\n--- Analysis Result for Wheat in Delhi ---")
        print(result_wheat)
    except Exception as e:
        print(f"An error occurred while fetching wheat prices: {e}")

    # Separator for clarity
    print("\n" + "="*60 + "\n")

    # Test Case 2: Rice prices without a specific location (general analysis)
    print("\n=== Requesting Market Price Analysis for Rice (General) ===")
    try:
        result_rice = get_market_prices.invoke({"crop_type": "rice"})
        print("\n--- Analysis Result for Rice (General) ---")
        print(result_rice)
    except Exception as e:
        print(f"An error occurred while fetching rice prices: {e}")
        
    # Separator for clarity
    print("\n" + "="*60 + "\n")

    # Test Case 3: Tomato prices in a specific, local market
    print("\n=== Requesting Market Price Analysis for Tomato in Indore ===")
    try:
        result_tomato = get_market_prices.invoke({"crop_type": "tomato", "location": "Indore"})
        print("\n--- Analysis Result for Tomato in Indore ---")
        print(result_tomato)
    except Exception as e:
        print(f"An error occurred while fetching tomato prices: {e}")


if __name__ == "__main__":
    # This standard Python construct ensures that the main() function is called
    # only when the script is executed directly (e.g., "python test_market_prices.py").
    main()