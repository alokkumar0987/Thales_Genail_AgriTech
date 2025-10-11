# main.py
import os
import uuid
import asyncio
import tempfile
import base64
from contextlib import asynccontextmanager
from langgraph.graph import StateGraph, END 
from typing import TypedDict, List, Optional, Any, Dict

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

# --- Step 1: Correctly Import ONLY Your Working Tools ---
# These are the functions decorated with @tool from your agent files.
# The old Agent classes are no longer needed here.
from weather_agent import get_weather_alerts
from soil_agent import get_soil_recommendations
from market_agent import get_market_prices
from location_agent import detect_user_location, set_manual_location
from image_agent import analyze_pest_disease

# --- Configuration ---
from utils import GROQ_API_KEY, DEFAULT_LOCATION

# --- FastAPI Boilerplate (Lifespan, Models, SessionManager) ---

class SessionManager:
    """Manages user sessions and conversation history."""
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def get_session(self, session_id: str) -> Dict[str, Any]:
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "chat_history": [],
                "user_location": DEFAULT_LOCATION,
                "created_at": asyncio.get_event_loop().time()
            }
        return self.sessions[session_id]

    def update_session(self, session_id: str, updates: Dict[str, Any]):
        if session_id in self.sessions:
            self.sessions[session_id].update(updates)

    def cleanup_old_sessions(self, max_age: int = 3600): # 1 hour
        current_time = asyncio.get_event_loop().time()
        to_delete = [
            sid for sid, data in self.sessions.items()
            if current_time - data.get("created_at", 0) > max_age
        ]
        for sid in to_delete:
            del self.sessions[sid]
        if to_delete:
            print(f"Cleaned up {len(to_delete)} old sessions.")

session_manager = SessionManager()

async def cleanup_task():
    while True:
        await asyncio.sleep(3600)
        session_manager.cleanup_old_sessions()

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(cleanup_task())
    print("🚀 AgriSmart Advisory System is running...")
    yield
    task.cancel()
    print("🛑 System shutting down.")

app = FastAPI(
    title="AgriSmart Advisory System",
    description="An AI-powered agricultural advisor using a tool-calling agent.",
    version="3.0.0",
    lifespan=lifespan
)

class QueryRequest(BaseModel):
    text: Optional[str] = None
    session_id: Optional[str] = None

class QueryResponse(BaseModel):
    response: str
    session_id: str

# --- Step 2: Define the Master Agent ---

# Consolidate all imported functions into a single `tools` list.
tools = [
    get_weather_alerts,
    get_soil_recommendations,
    get_market_prices,
    detect_user_location,
    set_manual_location,
]

# The Master Prompt that instructs the agent how to behave.
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are AgriSmart, a helpful and friendly AI assistant for farmers in India.
- Your current location is set to: {user_location}.
- You have access to specialized tools for weather, soil, market prices, and location.
- **Analyze the user's question carefully to determine which tool, if any, is needed.**
- If a user asks a multi-part question (e.g., "What are wheat prices and is it going to rain?"), you must use multiple tools in sequence to provide a complete answer.
- If the question is a general greeting, conversation, or something you can answer without a tool, do so naturally.
- Always be polite and provide actionable advice. Format complex information with bullet points for clarity."""),
    ("placeholder", "{chat_history}"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name="llama-3.1-8b-instant")
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# --- Step 3: Define the LangGraph Workflow ---

class AgentState(TypedDict):
    """Represents the state of our conversation graph."""
    input: str
    user_location: str
    chat_history: List[BaseMessage]
    session_id: str
    image_path: Optional[str]

# Node for handling all text-based queries via the agent
async def call_agent_node(state: AgentState) -> AgentState:
    session = session_manager.get_session(state["session_id"])
    result = await agent_executor.ainvoke({
        "input": state["input"],
        "chat_history": state["chat_history"],
        "user_location": state["user_location"]
    })
    response_text = result.get("output", "I encountered an error.")
    session["chat_history"].extend([HumanMessage(content=state["input"]), AIMessage(content=response_text)])
    state["input"] = response_text
    return state

# Node for handling the special case of image analysis
def image_analysis_node(state: AgentState) -> AgentState:
    if state.get("image_path"):
        response = analyze_pest_disease(state["image_path"])
        session = session_manager.get_session(state["session_id"])
        session["chat_history"].extend([
            HumanMessage(content=f"[Image Analysis]"),
            AIMessage(content=response)
        ])
        state["input"] = response
    return state

# The router that decides which node to call
def route_query(state: AgentState) -> str:
    return "image_analysis" if state.get("image_path") else "call_agent"

# Build the graph
workflow = StateGraph(AgentState)
workflow.add_node("image_analysis", image_analysis_node)
workflow.add_node("call_agent", call_agent_node)
workflow.set_conditional_entry_point(route_query, {
    "image_analysis": "image_analysis",
    "call_agent": "call_agent",
})
workflow.add_edge("image_analysis", END)
workflow.add_edge("call_agent", END)
app_workflow = workflow.compile()

# --- Step 4: Define FastAPI Endpoints ---

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Processes a farmer's text query."""
    session_id = request.session_id or str(uuid.uuid4())
    session = session_manager.get_session(session_id)
    initial_state = AgentState(
        input=request.text or "",
        user_location=session.get("user_location", DEFAULT_LOCATION),
        chat_history=session.get("chat_history", []),
        session_id=session_id,
        image_path=None
    )
    result = await app_workflow.ainvoke(initial_state)
    return QueryResponse(response=result["input"], session_id=session_id)

@app.post("/upload-image", response_model=QueryResponse)
async def upload_image(file: UploadFile = File(...), session_id: str = Form(None)):
    """Uploads an image for direct analysis."""
    session_id = session_id or str(uuid.uuid4())
    session = session_manager.get_session(session_id)
    temp_path = ""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name
        initial_state = AgentState(
            input="Analyze this plant leaf image.",
            user_location=session.get("user_location", DEFAULT_LOCATION),
            chat_history=session.get("chat_history", []),
            session_id=session_id,
            image_path=temp_path
        )
        result = await app_workflow.ainvoke(initial_state)
        return QueryResponse(response=result["input"], session_id=session_id)
    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)