import streamlit as st
import sys
import os

root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
try:
    from scripts.agent import generate_itinerary
except Exception as e:
    st.error(f"THE REAL IMPORT ERROR: {e}")
    st.stop()

st.set_page_config(page_title="AI Travel Planner", page_icon="✈️", layout="wide")
st.title("AI Travel Planner")

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

if submit_button:
    with st.spinner("Agent analyzing constraints and searching Knowledge Base..."):
        try:
            result = generate_itinerary(source, destination, budget, days, food_pref, specs, travelers)
            
            st.success("Itinerary Generated Successfully!")
            st.divider()
            st.markdown(result)
            
        except Exception as e:
            st.error(f"Agent Error: {e}")