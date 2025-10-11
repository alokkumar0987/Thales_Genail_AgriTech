# --- ⚙️ Section 1: Imports and Setup ---
import os
import uuid
import asyncio
import tempfile
import time
import uvicorn
import math
import random
import re
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from typing import TypedDict, List, Optional, Any, Dict

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

#  LangChain & Groq (Agent System)
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

#  Tool imports (your own modules)
from weather_agent import get_weather_alerts
from soil_agent import get_personalized_soil_recommendations
from market_agent import get_market_prices
from location_agent import detect_user_location, set_manual_location
from image_agent import analyze_plant_health 
from utils import GROQ_API_KEY, DEFAULT_LOCATION
from daily_scheduler import daily_summary_loop

# ---  Whisper Integration for Indian Languages ---
import whisper


# ================================================================
#  1 Whisper Voice Transcriber
# ================================================================
class EnhancedWhisperTranscriber:
    """Offline speech recognition using Whisper model with Indian language focus."""

    def __init__(self, model_size: str = "base"):
        self.model_size = model_size
        self.model = None
        self._load_model()

    def _load_model(self):
        print(f" Loading Whisper model ({self.model_size})...")
        try:
            self.model = whisper.load_model(self.model_size)
            print(" Whisper model loaded successfully!")
        except Exception as e:
            print(f" Whisper model failed to load: {e}")
            raise RuntimeError("Whisper model initialization failed.")

    async def transcribe_audio(self, file_path: str) -> str:
        """Asynchronously transcribe an audio file."""
        try:
            result = await asyncio.to_thread(
                self.model.transcribe,
                file_path,
                fp16=False,
                language="hi",  # focus on Hindi + multilingual auto-detect
                task="transcribe",
                temperature=0.2,
                best_of=3,
            )
            text = result.get("text", "").strip()
            print(f" Transcribed Text: {text}")
            return text
        except Exception as e:
            print(f" Whisper transcription error: {e}")
            raise HTTPException(status_code=500, detail="Audio transcription failed.")


# Initialize Whisper model (load once)
whisper_transcriber = EnhancedWhisperTranscriber("large")


# ================================================================
#  2️ Agricultural Language Helpers
# ================================================================
def enhance_agricultural_understanding(text: str) -> str:
    """Map regional terms (Hindi/Bhojpuri/Marathi/etc.) → English keywords."""
    terms = {
        "fasal": "crop", "kheti": "farming", "bij": "seed", "khaad": "fertilizer",
        "paani": "water", "mitti": "soil", "rog": "disease", "patte": "leaves",
        "bazaar bhav": "market price", "mandi rate": "market price",
        "sarkari yojana": "government scheme"
    }

    text = text.lower()
    for k, v in terms.items():
        text = text.replace(k, v)
    return text


def detect_query_language(text: str) -> str:
    """Basic Hindi/English detection."""
    if re.search(r"[\u0900-\u097F]", text):
        return "hindi"
    elif re.search(r"[a-zA-Z]", text):
        return "english"
    return "unknown"


# ================================================================
#  3️ Session Manager
# ================================================================
class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def get_session(self, session_id: str) -> Dict[str, Any]:
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "chat_history": [],
                "user_location": DEFAULT_LOCATION,
                "created_at": time.time()
            }
        return self.sessions[session_id]

    def update_session(self, session_id: str, updates: Dict[str, Any]):
        if session_id in self.sessions:
            self.sessions[session_id].update(updates)

    def cleanup_old_sessions(self, max_age: int = 3600):
        now = time.time()
        for sid in list(self.sessions.keys()):
            if now - self.sessions[sid]["created_at"] > max_age:
                del self.sessions[sid]
        print(" Old sessions cleaned up.")


session_manager = SessionManager()


# ================================================================
#  4️ FastAPI App Setup
# ================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    print(" AgriSmart backend starting...")
    cleanup_task = asyncio.create_task(periodic_cleanup())
    yield
    cleanup_task.cancel()
    print(" AgriSmart shutting down.")


async def periodic_cleanup():
    while True:
        await asyncio.sleep(3600)
        session_manager.cleanup_old_sessions()


app = FastAPI(
    title="AgriSmart Advisory System",
    version="4.2.1",
    description="AI-powered multilingual agricultural advisory system",
    lifespan=lifespan
)

@app.on_event("startup")

async def start_background_tasks():
    print("stating daily advisory")
    asyncio.create_task(daily_summary_loop())

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ================================================================
# 5️ LLM Agent Setup (Groq + LangGraph)
# ================================================================
tools = [
    get_weather_alerts,
    get_personalized_soil_recommendations,
    get_market_prices,
    detect_user_location,
    set_manual_location,
    analyze_plant_health,
]

prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are AgriSmart, a multilingual AI for Indian farmers.
- Understand English, Hindi, Bhojpuri, Marathi, Punjabi etc.
- Respond in the farmer’s language.
- Provide actionable, polite, and accurate agricultural advice.
- Use tools if needed (weather, soil, market, location, image).
"""),
    ("placeholder", "{chat_history}"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name="openai/gpt-oss-120b")
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)


# ================================================================
# LangGraph Workflow
# ================================================================
class AgentState(TypedDict):
    input: str
    user_location: str
    chat_history: List[BaseMessage]
    session_id: str
    image_path: Optional[str]


async def call_agent_node(state: AgentState) -> Dict[str, Any]:
    result = await agent_executor.ainvoke({
        "input": state["input"],
        "chat_history": state["chat_history"],
        "user_location": state["user_location"],
    })
    reply = result.get("output", " Could not process query.")
    new_history = state["chat_history"] + [HumanMessage(content=state["input"]), AIMessage(content=reply)]
    return {"chat_history": new_history, "input": reply}


async def image_analysis_node(state: AgentState) -> Dict[str, Any]:
    if not state.get("image_path"):
        return {"input": "No image provided."}
    response = await asyncio.to_thread(analyze_plant_health, state["image_path"])
    new_history = state["chat_history"] + [HumanMessage(content="[Image Query]"), AIMessage(content=response)]
    return {"chat_history": new_history, "input": response}


def route_query(state: AgentState) -> str:
    return "image_analysis" if state.get("image_path") else "call_agent"


workflow = StateGraph(AgentState)
workflow.add_node("image_analysis", image_analysis_node)
workflow.add_node("call_agent", call_agent_node)
workflow.set_conditional_entry_point(route_query, {
    "image_analysis": "image_analysis",
    "call_agent": "call_agent"
})
workflow.add_edge("image_analysis", END)
workflow.add_edge("call_agent", END)
app_workflow = workflow.compile()


# ================================================================
#  7️ FastAPI Endpoints
# ================================================================
class QueryRequest(BaseModel):
    text: Optional[str]
    session_id: Optional[str]


class QueryResponse(BaseModel):
    response: str
    session_id: str


@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    session_id = request.session_id or str(uuid.uuid4())
    session = session_manager.get_session(session_id)
    text = enhance_agricultural_understanding(request.text or "")

    state = AgentState(
        input=text,
        user_location=session["user_location"],
        chat_history=session["chat_history"],
        session_id=session_id,
        image_path=None
    )

    result = await app_workflow.ainvoke(state)
    session_manager.update_session(session_id, {"chat_history": result["chat_history"]})
    return QueryResponse(response=result["input"], session_id=session_id)


@app.post("/upload-image", response_model=QueryResponse)
async def upload_image(file: UploadFile = File(...), session_id: str = Form(None)):
    session_id = session_id or str(uuid.uuid4())
    session = session_manager.get_session(session_id)
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        tmp.write(await file.read())
        temp_path = tmp.name

    try:
        state = AgentState(
            input="Analyze this plant image.",
            user_location=session["user_location"],
            chat_history=session["chat_history"],
            session_id=session_id,
            image_path=temp_path
        )
        result = await app_workflow.ainvoke(state)
        session_manager.update_session(session_id, {"chat_history": result["chat_history"]})
        return QueryResponse(response=result["input"], session_id=session_id)
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


@app.post("/voice-query", response_model=QueryResponse)
async def process_voice_query(audio_file: UploadFile = File(...), session_id: str = Form(None)):
    session_id = session_id or str(uuid.uuid4())
    session = session_manager.get_session(session_id)

    if not audio_file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="File must be an audio file.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(await audio_file.read())
        audio_path = tmp.name

    try:
        transcribed_text = await whisper_transcriber.transcribe_audio(audio_path)
        enhanced = enhance_agricultural_understanding(transcribed_text)

        state = AgentState(
            input=enhanced,
            user_location=session["user_location"],
            chat_history=session["chat_history"],
            session_id=session_id,
            image_path=None
        )
        result = await app_workflow.ainvoke(state)
        session_manager.update_session(session_id, {"chat_history": result["chat_history"]})
        return QueryResponse(response=result["input"], session_id=session_id)
    finally:
        if os.path.exists(audio_path):
            os.unlink(audio_path)


@app.get("/voice-formats")
async def get_supported_audio_formats():
    return {
        "supported_formats": ["WAV", "MP3", "M4A", "FLAC", "OGG"],
        "recommended": "WAV 16kHz for best accuracy"
    }


# ================================================================
#  8️Market Data (Real-Time Simulation)
# ================================================================
@app.get("/api/market-data/structured")
async def get_structured_market_data(crop: str, location: str = None):
    return {
        "success": True,
        "data": generate_real_time_market_data(crop, location or "India"),
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/market-data/comprehensive")
async def get_comprehensive_market_data():
    crops = ["wheat", "rice", "cotton", "mustard", "corn"]
    local = [generate_real_time_market_data(c, "India") for c in crops]
    global_data = [generate_real_time_market_data(c, "Global") for c in ["rice", "corn", "soybeans"]]
    return {
        "success": True,
        "data": {"local": local, "global": global_data, "last_updated": datetime.now().isoformat()}
    }


def generate_real_time_market_data(crop: str, location: str) -> dict:
    base = {"wheat": 2400, "rice": 3100, "cotton": 6200, "mustard": 5200, "corn": 1800, "soybeans": 4200}
    price = base.get(crop.lower(), 3000)
    change = random.uniform(-0.05, 0.05)
    trend = "increasing" if change > 0.02 else "decreasing" if change < -0.02 else "stable"
    current = price * (1 + change)
    return {
        "crop": crop.title(),
        "location": location,
        "trend": trend,
        "price": round(current, 2),
        "recommendation": generate_recommendations(crop, trend),
    }


def generate_recommendations(crop: str, trend: str) -> str:
    if trend == "increasing":
        return f"Sell {crop} soon — prices rising!"
    elif trend == "decreasing":
        return f"Hold {crop} for better rates."
    return f"Market stable for {crop}."





# ================================================================
#  Run the App
# ================================================================
if __name__ == "__main__":

    
    # Start backend APIs
    
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


