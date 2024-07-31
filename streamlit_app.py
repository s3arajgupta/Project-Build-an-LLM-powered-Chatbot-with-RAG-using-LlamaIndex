import streamlit as st
from index_wikipages import create_index
from chat_agent import create_react_agent
import openai
from utils import get_apikey
import os

# Initialize global variables
index = None
agent = None

st.title("Wikipedia Index and Chat Agent")

# Display the instructions from chainlit.md
def show_instructions():
    with open("chainlit.md", "r") as file:
        instructions = file.read()
    st.markdown(instructions)

# Function to handle settings
def handle_settings():
    global index, agent
    model_choice = st.selectbox("Choose Model:", ["gpt-3.5-turbo"])
    query = st.text_input("Enter pages to index (comma-separated):", "paris, lagos, lao")
    if st.button("Confirm"):
        with st.spinner("Indexing..."):
            index = create_index(query)
            st.success(f'Wikipage(s) "{query}" successfully indexed')
            agent = create_react_agent(model_choice)

# Function to handle chat
def handle_chat():
    user_message = st.text_input("You: ")
    if st.button("Send"):
        if agent:
            response = agent.chat(user_message)
            st.text_area("Agent:", response, height=200)
        else:
            st.warning("Please set up the settings first.")

# Display instructions on initial load
if "instructions_shown" not in st.session_state:
    show_instructions()
    st.session_state["instructions_shown"] = True

# Main Settings and Chat Interface
st.header("Settings and Chat Interface")
handle_settings()
st.write("index")
st.write(index)

# Chat Box
st.header("Chat with Agent")
if index:
    handle_chat()
else:
    st.warning("Please index pages first.")

# Ensure the OpenAI API key is set
openai.api_key = get_apikey()
