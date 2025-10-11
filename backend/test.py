# app.py (Corrected for Conversational Flow)
import os
import streamlit as st
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferMemory
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import tool
from PIL import Image
import tempfile

# --- Import Your Specialist Tools ---
from location_agent import get_location_info
from weather_agent import get_weather_alerts
from soil_agent import get_soil_recommendations
from market_agent import get_market_prices
from image_agent import analyze_pest_disease

# --- LLM Configuration ---
llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.2, max_tokens=2048)

# --- Define Tools ---
@tool
def weather_tool(location: str) -> str:
    """Provides weather alerts and farming advice for a specific location."""
    return get_weather_alerts(location)

@tool
def soil_tool(crop_type: str, location: str) -> str:
    """Gives soil health recommendations for a specific crop and location."""
    return get_soil_recommendations({"crop_type": crop_type, "location": location})

@tool
def market_tool(crop_type: str, location: str) -> str:
    """Provides current market prices and trends for a crop in a location."""
    return get_market_prices({"crop_type": crop_type, "location": location})

@tool
def pest_tool(image_path: str) -> str:
    """Analyzes a plant image from a file path to detect pests or diseases."""
    return analyze_pest_disease(image_path)

# --- Create Conversational Agent (Cached for Session) ---
@st.cache_resource
def create_conversational_agent():
    """Initializes the conversational agent and its memory."""
    tools = [weather_tool, soil_tool, market_tool, pest_tool]
    
    # --- THIS PROMPT IS SIMPLIFIED ---
    # The context (like location) will now be part of the user's input string.
    system_prompt = """
    You are Kisan Mitra, a helpful and conversational AI assistant for farmers in India.
    - Analyze the user's input carefully. It will contain their direct query and may also contain contextual information like their current location or an available image path.
    - Use your tools to answer questions about weather, soil, market prices, and plant diseases based on the provided context.
    - If you need information that isn't provided (like a crop type), you MUST ask the user for it.
    - Always respond in a friendly and helpful tone, primarily in a Hindi/English mix.
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        memory=memory
    )
    return agent_executor

# --- Streamlit Chatbot Interface ---
def main():
    st.set_page_config(page_title="Kisan Mitra", page_icon="🌾")
    st.title("🌾 Kisan Mitra - Your Farming Friend")

    # Initialize session state
    if "agent_executor" not in st.session_state:
        st.session_state.agent_executor = create_conversational_agent()
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hello! How can I help you today?"}]
    if "current_location" not in st.session_state:
        # Auto-detect location on first run
        with st.spinner("Detecting your location..."):
            try:
                loc_info = get_location_info()
                st.session_state.current_location = f"{loc_info.get('city', 'Unknown')}, {loc_info.get('state', 'Unknown')}"
            except Exception:
                st.session_state.current_location = "Indore, Madhya Pradesh" # Fallback
    if "image_path" not in st.session_state:
        st.session_state.image_path = None

    # Sidebar
    with st.sidebar:
        st.header("Settings")
        st.info(f"📍 Current Location: **{st.session_state.current_location}**")

        st.header("📸 Plant Health Check")
        uploaded_file = st.file_uploader("Upload a leaf image", type=["jpg", "jpeg", "png"])

        if uploaded_file is not None:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                # Save the path for the agent to use
                st.session_state.image_path = tmp_file.name
            st.image(uploaded_file, caption="Image ready for analysis.")
            st.success("Image uploaded. Ask me to 'analyze this image' in the chat.")

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Handle user input
    if prompt := st.chat_input("Ask me about farming..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # --- THIS IS THE KEY FIX ---
                    # We now combine all context into a single input string for the agent.
                    input_with_context = f"User query: '{prompt}'"
                    input_with_context += f"\n[Context: My current location is {st.session_state.current_location}]"
                    if st.session_state.image_path:
                        input_with_context += f"\n[Context: An image has been uploaded and is available at the path: {st.session_state.image_path}]"

                    # Call the agent with the single, formatted input.
                    response = st.session_state.agent_executor.invoke({
                        "input": input_with_context
                    })
                    
                    st.markdown(response["output"])
                    st.session_state.messages.append({"role": "assistant", "content": response["output"]})
                    
                    # Clean up the temporary image file after it has been used
                    if st.session_state.image_path:
                        os.unlink(st.session_state.image_path)
                        st.session_state.image_path = None

                except Exception as e:
                    error_msg = f"Sorry, an error occurred: {e}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

if __name__ == "__main__":
    main()