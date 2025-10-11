# soil_advisor.py

from typing import Dict
from langchain.tools import tool
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from utils import GROQ_API_KEY

# ------------------- SoilAgent (Expert Engine) -------------------
class SoilAgent:
    def __init__(self):
        self.llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name="openai/gpt-oss-120b")
    
    def get_soil_advice(self, query: str, location: str = "your region", crop_type: str = "general crops", soil_data: dict = None) -> str:
        """Generate expert soil & fertilizer advice"""
        soil_data_text = f"Additional soil data: {soil_data}" if soil_data else ""
        
        prompt_template = """You are an agricultural expert specializing in soil health and fertilizers.
Provide detailed, farmer-friendly recommendations for {crop_type} cultivation in {location}.
{soil_data_text}

Query: {query}

Include:
1. Ideal soil conditions
2. Fertilizer recommendations (types, quantities, schedule)
3. Soil amendment suggestions
4. Location-specific considerations
5. Organic alternatives if available

Format your response with headings and bullet points, in simple farmer-friendly language."""
        
        prompt = ChatPromptTemplate.from_template(prompt_template)
        chain = prompt | self.llm
        
        response = chain.invoke({
            "location": location,
            "crop_type": crop_type,
            "soil_data_text": soil_data_text,
            "query": query
        })
        return response.content

# ------------------- SoilSessionManager (Step-by-Step Conversation) -------------------
class SoilSessionManager:
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}
        self.soil_agent = SoilAgent()

    def _get_session(self, session_id: str) -> Dict:
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "location": None,
                "crop_type": None,
                "soil_data": {},
                "additional_info": {}
            }
        return self.sessions[session_id]

    def handle_query(self, session_id: str, user_input: str) -> str:
        """Step-by-step conversation until all required info is collected"""
        session = self._get_session(session_id)

        # Step 1: Location
        if not session["location"]:
            states = ["punjab", "haryana", "bihar", "up", "delhi", "maharashtra", "indore"]
            for st in states:
                if st in user_input.lower():
                    session["location"] = st.title() + ", India"
                    break
            if not session["location"]:
                return "🌍 Aapki kheti kis location par hai? (e.g., Punjab, Bihar, Indore)"

        # Step 2: Crop type
        if not session["crop_type"]:
            crops = ["wheat", "rice", "corn", "maize", "cotton", "sugarcane"]
            for crop in crops:
                if crop in user_input.lower():
                    session["crop_type"] = crop
                    break
            if not session["crop_type"]:
                return "🌾 Aap kis crop ke liye soil advice chahte ho? (e.g., wheat, rice, corn)"

        # Step 3: Soil pH
        if not session["soil_data"].get("pH"):
            if "ph" in user_input.lower():
                try:
                    ph_value = float(user_input.split("ph")[-1].strip().split()[0])
                    session["soil_data"]["pH"] = ph_value
                except:
                    pass
            if not session["soil_data"].get("pH"):
                return "🧪 Kya aapke paas soil test report hai? Agar haan to pH value batayein."

        # Step 4: Irrigation info (optional)
        if not session["additional_info"].get("irrigation"):
            if any(term in user_input.lower() for term in ["canal","drip","borewell","none","available","nahi"]):
                session["additional_info"]["irrigation"] = user_input
            else:
                return "💧 Aapke paas kaun si irrigation facility hai? (canal, borewell, drip, none)"

        # Step 5: All info collected → final recommendation
        return self.soil_agent.get_soil_advice(
            query=f"Soil advice for {session['crop_type']} in {session['location']} with soil data {session['soil_data']} and irrigation info {session['additional_info']}",
            location=session["location"],
            crop_type=session["crop_type"],
            soil_data=session["soil_data"]
        )

# ------------------- LangChain Tool -------------------
soil_session_manager = SoilSessionManager()

@tool
def get_personalized_soil_recommendations(session_id: str, user_input: str) -> str:
    """Step-by-step personalized soil advisor"""
    return soil_session_manager.handle_query(session_id, user_input)

# ------------------- Daily Summary Generic Soil Advice -------------------
def get_soil_advice(location: str = "your region") -> str:
    """
    Simple soil advice for daily 6AM summary.
    This avoids step-by-step conversation and just gives general tips.
    """
    return soil_session_manager.soil_agent.get_soil_advice(
        query=f"General soil advice for crops in {location}",
        location=location,
        crop_type="general crops",
        soil_data=None
    )
