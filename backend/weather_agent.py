# weather_agent.py (Corrected and Improved)

import requests
from datetime import datetime
from langchain.tools import tool
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from utils import GROQ_API_KEY, OPENWEATHER_API_KEY

# --- Efficiency Improvement: Define the LLM and Prompt once ---
# These don't need to be created every time the function is called.

llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name="openai/gpt-oss-120b")

prompt = ChatPromptTemplate.from_template(
    """You are an expert agricultural meteorologist. Analyze the following weather forecast for {location}.
Provide specific, actionable advice for a farmer.

Weather Information:
{weather_info}

Your advisory must include:
1.  **Immediate Outlook**: A summary of today's and tomorrow's weather.
2.  **Irrigation Advice**: Recommendations for watering based on predicted rainfall.
3.  **Pest & Disease Alert**: Warnings about any conditions that might encourage pests or diseases (e.g., high humidity).
4.  **Work Planning**: Suggestions for farm activities (e.g., "Good day for spraying," "Postpone planting due to heavy rain").

Format the response clearly using markdown headings and bullet points."""
)

# Create the summarization chain once
summarizer_chain = prompt | llm

# --- Helper function to get data (not a tool itself) ---
def _get_weather_data(location: str) -> dict:
    """Internal function to fetch and process weather data from OpenWeatherMap."""
    try:
        # Step 1: Convert location name to coordinates (latitude, longitude)
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={location}&limit=1&appid={OPENWEATHER_API_KEY}"
        geo_response = requests.get(geo_url).json()
        if not geo_response:
            return {"error": f"Could not find coordinates for the location: {location}."}
        
        lat, lon = geo_response[0]['lat'], geo_response[0]['lon']

        # Step 2: Get the 5-day forecast using coordinates
        forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
        forecast_response = requests.get(forecast_url).json()
        
        if forecast_response.get("cod") != "200":
             return {"error": f"Could not retrieve weather. API response: {forecast_response.get('message', 'Unknown error')}"}
        
        return forecast_response

    except Exception as e:
        return {"error": f"An unexpected error occurred while fetching weather data: {e}"}

# --- The Main Tool for the Agent ---
@tool
def get_weather_alerts(location: str) -> str:
    """
    Fetches a 5-day weather forecast for a specified location and provides
    detailed agricultural advisories. Use this tool when a user asks about
    weather, rain, temperature, or the forecast. The location must be a
    city or place name, for example, "Indore, India".
    """
    print(f"--- TOOL: Getting weather for {location} ---")
    weather_data = _get_weather_data(location)

    if "error" in weather_data:
        return weather_data["error"]

    # Step 3: Correctly process the 5-day forecast data
    daily_summary = {}
    for forecast in weather_data.get('list', []):
        date = datetime.fromtimestamp(forecast['dt']).strftime('%Y-%m-%d')
        if date not in daily_summary:
            daily_summary[date] = {
                'temps': [],
                'conditions': [],
                'humidity': []
            }
        daily_summary[date]['temps'].append(forecast['main']['temp'])
        daily_summary[date]['conditions'].append(forecast['weather'][0]['description'])
        daily_summary[date]['humidity'].append(forecast['main']['humidity'])

    # Format the processed data into a string for the LLM
    weather_info = f"5-Day Summary for {location}:\n"
    for date, data in daily_summary.items():
        avg_temp = sum(data['temps']) / len(data['temps'])
        most_common_condition = max(set(data['conditions']), key=data['conditions'].count)
        avg_humidity = sum(data['humidity']) / len(data['humidity'])
        weather_info += (
            f"- **{date}**: Avg Temp: {avg_temp:.1f}°C, "
            f"Condition: {most_common_condition}, "
            f"Avg Humidity: {avg_humidity:.0f}%\n"
        )
    
    # Step 4: Use the LLM chain to generate the final advisory
    response = summarizer_chain.invoke({
        "location": location,
        "weather_info": weather_info
    })
    
    return response.content

# ---
# IMPORTANT: No test code or "if __name__ == '__main__':" block should be in this file.
# ---