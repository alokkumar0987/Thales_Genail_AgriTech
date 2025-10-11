from langchain.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from utils import TAVILY_API_KEY, GROQ_API_KEY
import re
import json

class MarketAgent:
    def __init__(self):
        # CORRECTED: Use the runnable TavilySearchResults tool instead of the wrapper.
        self.search = TavilySearchResults(tavily_api_key=TAVILY_API_KEY, max_results=5)
        self.llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name="openai/gpt-oss-120b")
        self.price_patterns = {
            'wheat': r'₹?\s*(\d+,?\d*\.?\d*)\s*(?:per\s*quintal|/qtl|/quintal)',
            'rice': r'₹?\s*(\d+,?\d*\.?\d*)\s*(?:per\s*quintal|/qtl|/quintal)',
            'corn': r'₹?\s*(\d+,?\d*\.?\d*)\s*(?:per\s*quintal|/qtl|/quintal)',
            'cotton': r'₹?\s*(\d+,?\d*\.?\d*)\s*(?:per\s*quintal|/qtl|/quintal)',
            'sugarcane': r'₹?\s*(\d+,?\d*\.?\d*)\s*(?:per\s*quintal|/qtl|/quintal)',
            'tomato': r'₹?\s*(\d+,?\d*\.?\d*)\s*(?:per\s*kg|/kg|per\s*kilogram)',
            'potato': r'₹?\s*(\d+,?\d*\.?\d*)\s*(?:per\s*kg|/kg|per\s*kilogram)',
            'onion': r'₹?\s*(\d+,?\d*\.?\d*)\s*(?:per\s*kg|/kg|per\s*kilogram)'
        }
    
    def extract_prices_from_text(self, text: str, crop_type: str) -> list:
        """
        Extract prices from text using regex patterns.
        """
        pattern = self.price_patterns.get(crop_type.lower())
        if not pattern:
            return []
        
        # Find all matching price strings
        matches = re.findall(pattern, text, re.IGNORECASE)
        # Clean matches by removing commas and converting to float
        cleaned_prices = [float(price.replace(',', '')) for price in matches]
        return cleaned_prices
    
    def get_prices(self, query: str, location: str = None) -> str:
        """
        Track market prices for specific crops in a location.
        """
        crop_type = self.extract_crop_type(query)
        if not crop_type:
            crop_type = "agricultural commodities"
        
        search_query = f"current market prices for {crop_type}"
        if location:
            search_query += f" in {location}"
        
        # Using a more recent year; ideally, this would be dynamic.
        search_query += " in 2024 OR 2025 today current"
        
        # Search for market information
        # The TavilySearchResults tool returns a list of dictionaries.
        search_results = self.search.invoke(search_query)
        
        # CORRECTED: Process the list of results into a single string for analysis.
        # This prevents a TypeError with the regex function and provides clean context to the LLM.
        market_info_text = ""
        if isinstance(search_results, list):
            market_info_text = "\n\n".join([f"Source: {res.get('url')}\nContent: {res.get('content')}" for res in search_results])
        
        prices = []
        if crop_type != "agricultural commodities" and market_info_text:
            prices = self.extract_prices_from_text(market_info_text, crop_type)
        
        prompt = ChatPromptTemplate.from_template(
            """You are an agricultural market analyst based in India. Analyze the following market information 
            for {crop_type} and provide clear, actionable insights for a farmer.

            Market Information Found:
            {market_info}
            
            Location Context: {location_text}
            Extracted Raw Prices (if any): {prices_text}
            
            Please provide a structured report with the following sections:
            1.  **Current Price Analysis:** State the current price range you found in ₹ (Indian Rupees). Mention the most common price per quintal (or kg for vegetables). If there are conflicting prices, point it out.
            2.  **Market Trends:** Based on the information, is the price stable, rising, or falling?
            3.  **Key Factors:** What are the main reasons affecting the current prices (e.g., demand, supply, weather, government policy)?
            4.  **Future Outlook:** Give a brief prediction for price movements in the near future (next few weeks).
            5.  **Selling Recommendation:** Based on your analysis, provide a simple recommendation for a farmer: "Consider Selling Now," "Hold for Better Prices," or "Market is Unstable, Sell in Batches."
            
            Format your response clearly. Use Indian Rupee (₹) symbols for all prices."""
        )
        
        location_text = f"Focusing on {location}" if location else "General market"
        prices_text = f"₹{', ₹'.join(map(str, prices))}" if prices else "No specific prices could be extracted automatically."
        
        chain = prompt | self.llm
        response = chain.invoke({
            "crop_type": crop_type,
            "market_info": market_info_text,
            "location_text": location_text,
            "prices_text": prices_text
        })
        
        return response.content
    
    def extract_crop_type(self, query: str) -> str:
        """
        Extract crop type from user query.
        """
        query_lower = query.lower()
        
        crop_keywords = {
            'wheat': ['wheat', 'gehu', 'kanak'],
            'rice': ['rice', 'chawal', 'dhan', 'paddy'],
            'corn': ['corn', 'makka', 'maize', 'bhutta'],
            'cotton': ['cotton', 'kapas', 'rui'],
            'sugarcane': ['sugarcane', 'ganna', 'ikh'],
            'tomato': ['tomato', 'tamatar'],
            'potato': ['potato', 'aaloo', 'alu'],
            'onion': ['onion', 'pyaaz', 'kanda']
        }
        
        for crop, keywords in crop_keywords.items():
            for keyword in keywords:
                if keyword in query_lower:
                    return crop
        
        return ""

market_agent = MarketAgent()

@tool
def get_market_prices(crop_type: str, location: str = None) -> str:
    """
    Track market prices for specific crops in a location. This tool provides a detailed analysis of current prices, trends, influencing factors, and selling recommendations for farmers.
    
    Args:
        crop_type: Type of crop (e.g., "wheat", "rice", "tomato").
        location: Optional geographic location for local market prices (e.g., "Indore", "Punjab").
        
    Returns:
        A detailed market analysis report for the specified crop.
    """
    query = f"{crop_type} prices"
    if location:
        query += f" in {location}"
    
    return market_agent.get_prices(query, location)
