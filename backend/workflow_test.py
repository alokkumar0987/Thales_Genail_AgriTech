import json
from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from typing import TypedDict, Optional, Dict

# --- Specialist Tools ---
# These are your tested and working tool functions.
from location_agent import detect_user_location_json
from weather_agent import get_weather_alerts
from soil_agent import get_soil_recommendations
from market_agent import get_market_prices
from image_agent import analyze_pest_disease
from location_agent import detect_user_location, set_manual_location, get_location_info, detect_user_location_json
import json

# --- State Definition ---
# Added 'crop_type' to the state to pass it from the router to the handler.
class FarmerState(TypedDict):
    farmer_id: str
    query: str
    location: Optional[Dict] # Storing the full location dict is more robust
    response: Optional[str]
    category: Optional[str]
    crop_type: Optional[str]
    image_path: Optional[str]

# --- Global Memory Store ---
FARMER_MEMORY = {}

def get_farmer_memory(farmer_id: str) -> dict:
    if farmer_id not in FARMER_MEMORY:
        FARMER_MEMORY[farmer_id] = {
            "location": None,
            "last_crop": None,
        }
    return FARMER_MEMORY[farmer_id]

def format_location_string(location_data: Optional[Dict]) -> str:
    """Helper to create a clean location string for tools."""
    if not location_data:
        return "Indore, India" # Default fallback
    parts = [
        location_data.get('city'),
        location_data.get('state'),
        location_data.get('country')
    ]
    return ', '.join(part for part in parts if part)

# === Node 1: Resolve Location ===
def resolve_location(state: FarmerState):
    """Gets location from memory or detects it automatically."""
    mem = get_farmer_memory(state["farmer_id"])
    
    if not state.get("location") and mem.get("location"):
        state["location"] = mem["location"]
    
    if not state.get("location"):
        try:
            loc_json = detect_user_location_json.invoke("")
            if loc_json and loc_json.get("city"):
                state["location"] = loc_json
                mem["location"] = loc_json # Save to memory for next time
            else:
                state["location"] = {"city": "Indore", "state": "Madhya Pradesh", "country": "India"}
        except Exception as e:
            state["response"] = f"Location detection failed: {e}"
    
    return state

# === Node 2: Smart LLM Router (UPGRADED) ===
# After
# After
llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
def llm_router(state: FarmerState):
    if state.get("response"):
        return state
    
    try:
        query = state["query"]
        # Create the prompt directly
        prompt_text = f"""
You are a master at analyzing a farmer's query.
Your task is to classify the query into a category and extract the crop type if mentioned.

Respond with ONLY a JSON object containing two keys: 'category' and 'crop_type'.
The possible categories are: ["weather", "soil", "market", "pest", "general"].
If no specific crop is mentioned, the value for 'crop_type' should be null.

Examples:
Query: "Mandi me gehun ka daam kya hai?"
Response: {{"category": "market", "crop_type": "wheat"}}

Query: "aaj ka mausam batao"
Response: {{"category": "weather", "crop_type": null}}

Query: {query}
Response:
"""
        router_output = llm.invoke(prompt_text)
        router_output_str = router_output.content
        
        print(f"Raw LLM Output: {router_output_str}")
        
        # Extract JSON from markdown code blocks if present
        if "```json" in router_output_str:
            # Extract content between ```json and ```
            start_idx = router_output_str.find("```json") + 7
            end_idx = router_output_str.rfind("```")
            router_output_str = router_output_str[start_idx:end_idx].strip()
        elif "```" in router_output_str:
            # Extract content between any ``` blocks
            start_idx = router_output_str.find("```") + 3
            end_idx = router_output_str.rfind("```")
            router_output_str = router_output_str[start_idx:end_idx].strip()
        
        # Parse the JSON output from the LLM
        router_data = json.loads(router_output_str)
        
        state["category"] = router_data.get("category", "general")
        state["crop_type"] = router_data.get("crop_type")
        
        print(f"🧠 Router Decision: Category='{state['category']}', Crop='{state['crop_type']}'")

    except Exception as e:
        state["response"] = f"Query routing failed: {e}"
        state["category"] = "general"
        
    return state

# === Node 3: Handle Category (FIXED) ===
def handle_category(state: FarmerState):
    """Calls the correct tool based on the router's decision."""
    if state.get("response"):
        return state

    mem = get_farmer_memory(state["farmer_id"])
    loc_str = format_location_string(state.get("location"))
    category = state.get("category", "general")
    crop_type = state.get("crop_type") or mem.get("last_crop") # Use new crop or fall back to memory

    try:
        if category == "weather":
            state["response"] = get_weather_alerts.invoke(loc_str)
        
        elif category in ["soil", "market"]:
            if not crop_type:
                state["response"] = "Please specify which crop you are asking about (e.g., 'gehun', 'chawal')."
            else:
                # FIXED: Pass the extracted crop_type to the tool.
                tool_input = {"location": loc_str, "crop_type": crop_type}
                if category == "soil":
                    state["response"] = get_soil_recommendations.invoke(tool_input)
                else:
                    state["response"] = get_market_prices.invoke(tool_input)
                mem["last_crop"] = crop_type # FIXED: Save the crop to memory!

        elif category == "pest":
            if state.get("image_path"):
                # FIXED: Handle the string output from the tool correctly.
                analysis_result = analyze_pest_disease.invoke(state["image_path"])
                state["response"] = f"Image Analysis Result:\n{analysis_result}"
            else:
                state["response"] = "For pest and disease analysis, please upload a photo of the affected plant leaf."
        
        else: # general category
            state["response"] = f"I am ready to help. Your location is set to {loc_str}. How can I assist you with weather, soil, market prices, or pest detection?"

    except Exception as e:
        state["response"] = f"An error occurred: {e}"

    return state

# === Build and Compile Graph ===
workflow = StateGraph(FarmerState)
workflow.add_node("resolve_location", resolve_location)
workflow.add_node("llm_router", llm_router)
workflow.add_node("handle_category", handle_category)

workflow.set_entry_point("resolve_location")
workflow.add_edge("resolve_location", "llm_router")
workflow.add_edge("llm_router", "handle_category")
workflow.add_edge("handle_category", END)

app = workflow.compile()

# === Example Runs ===
farmer_id = "farmer_123"

print("\n--- Weather Query ---")
result = app.invoke({"farmer_id": farmer_id, "query": "aaj ka mausam batao"})
print(f"✅ Response: {result['response']}")

print("\n--- Market Query (with crop) ---")
result = app.invoke({"farmer_id": farmer_id, "query": "Mandi me gehun ka daam kya hai?"})
print(f"✅ Response: {result['response']}")

print("\n--- Soil Query (using memory for crop) ---")
result = app.invoke({"farmer_id": farmer_id, "query": "meri mitti ke liye kya salah hai"})
print(f"✅ Response: {result['response']}")

print("\n--- Pest Query (without image) ---")
result = app.invoke({"farmer_id": farmer_id, "query": "Patte pe daag aa rahe hain"})
print(f"✅ Response: {result['response']}")

print("\n--- Pest Query (with image) ---")
image_path = r"D:\crop_advisory\Potato\Train\Potato___healthy\Potato_healthy-76-_0_7539.jpg" # Make sure this path is correct
result = app.invoke({
    "farmer_id": farmer_id,
    "query": "Is this leaf healthy?",
    "image_path": image_path
})
print(f"✅ Response: {result['response']}")

print("=== Testing detect_user_location (string) ===")
location_str = detect_user_location.invoke("")
print(location_str)
print("\n")

print("=== Testing set_manual_location ===")
manual_location = set_manual_location.invoke("Delhi, India")
print(manual_location)
print("\n")

print("=== Testing get_location_info (with query) ===")
query_location = get_location_info.invoke("near Mumbai")
print(query_location)
print("\n")

print("=== Testing detect_user_location_json ===")
location_json = detect_user_location_json.invoke("")
print(json.dumps(location_json, indent=4))