import streamlit as st
import sys
import os
import uuid

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

try:
    from backend.agent import run_agent, generate_itinerary
except Exception as e:
    st.error(f"IMPORT ERROR: {e}")
    st.stop()

st.set_page_config(page_title="AI Travel Planner", page_icon="✈️", layout="wide")
st.title("AI Travel Planner")

# session id for memory
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

with st.form("travel_form"):
    st.subheader("Plan Your Next Trip")
    
    col1, col2 = st.columns(2)
    with col1:
        source = st.text_input("Source Location", value="Chennai, Tamil Nadu, India")
        destination = st.text_input("Destination", placeholder="Leave empty for AI suggestions")
        travelers = st.text_input("Traveler Count & Description", placeholder="e.g. 4 People (2 Adults, 2 Kids)")
    
    with col2:
        budget = st.text_input("Total Budget for the whole group", placeholder="e.g. ₹1,00,000")
        days = st.slider("Duration (Days)", min_value=1, max_value=30, value=5)
        food_pref = st.text_input("Food Preferences", placeholder="e.g., Jain, Vegan, Local cuisine")
        
    specs = st.text_area("Additional Specifications", placeholder="e.g., Plan a relaxed summer trip focusing on beaches and historical sites")
    
    submit_button = st.form_submit_button("Generate Itinerary")

# initial itinerary generation
if submit_button:
    with st.spinner("Generating itinerary..."):
        try:
            result = generate_itinerary(source, destination, budget, days, food_pref, specs, travelers)

            st.session_state.chat_history = []
            st.session_state.chat_history.append(("assistant", result))

            st.success("Itinerary Generated Successfully!")

        except Exception as e:
            st.error(f"Agent Error: {e}")

# show itinerary + chat
if st.session_state.chat_history:
    st.divider()

    for role, msg in st.session_state.chat_history:
        if role == "user":
            st.markdown(f"**You:** {msg}")
        else:
            st.markdown(msg)

    st.divider()
    st.subheader("Discuss / Modify Plan")

    user_input = st.text_input("Ask to modify itinerary...")

    if st.button("Send"):
        if user_input.strip():
            st.session_state.chat_history.append(("user", user_input))

            with st.spinner("Updating plan..."):
                try:
                    response = run_agent(user_input, st.session_state.session_id)

                    st.session_state.chat_history.append(("assistant", response))

                except Exception as e:
                    st.error(f"Agent Error: {e}")

            st.rerun()