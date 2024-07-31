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
    with st.form("settings_form"):
        model_choice = st.selectbox("Choose Model:", ["gpt-3.5-turbo"])
        query = st.text_input("Enter pages to index (comma-separated):", "paris, tokyo")
        submitted = st.form_submit_button("Confirm")
        if submitted:
            with st.spinner("Indexing..."):
                try:
                    index = create_index(query)
                    st.write(index)
                    if index:
                        st.success(f'Wikipage(s) "{query}" successfully indexed')
                        agent = create_react_agent(model_choice)
                        st.write(agent)
                    else:
                        st.error("Failed to create index.")
                except Exception as e:
                    st.error(f"An error occurred: {e}")
                    print(e)

# Function to handle chat
def handle_chat():
    user_message = st.text_input("You: ")
    if st.button("Send"):
        if agent:
            try:
                response = agent.chat(user_message)
                st.text_area("Agent:", response, height=200)
            except Exception as e:
                st.error(f"An error occurred while chatting: {e}")
                print(e)
        else:
            st.warning("Please set up the settings first.")

# Display instructions on initial load
if "instructions_shown" not in st.session_state:
    show_instructions()
    st.session_state["instructions_shown"] = True

# Settings Panel
st.sidebar.header("Settings Panel")
handle_settings()

# Chat Box
st.header("Chat with Agent")
if index:
    handle_chat()
else:
    st.warning("Please index pages first.")

# Ensure the OpenAI API key is set
openai.api_key = get_apikey()
