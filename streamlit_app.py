import streamlit as st
from index_wikipages import create_index
from chat_agent import create_react_agent, run_agent
import openai
from utils import get_apikey
import os

# Initialize global variables
index = None
agent = None

# Function to show instructions
def show_instructions():
    with open("chainlit.md", "r") as file:
        instructions = file.read()
    st.markdown(instructions)

# Function to handle settings
def handle_settings():
    global index, agent
    st.header("Settings")
    model_choice = st.selectbox("Choose Model:", ["gpt-3.5-turbo"])
    query = st.text_input("Enter pages to index (comma-separated):", "paris, tokyo")
    if st.button("Index Pages"):
        with st.spinner("Indexing..."):
            try:
                index = create_index(query)
                if index:
                    st.success(f'Wikipage(s) "{query}" successfully indexed')
                    agent = create_react_agent(model_choice, index)
                else:
                    st.error("Failed to create index.")
            except Exception as e:
                st.error(f"An error occurred: {e}")
                print(e)

# Function to handle chat
def handle_chat():
    st.header("Chat with Agent")
    user_message = st.text_input("You: ")
    if st.button("Send"):
        st.write("agent handle_chat ", agent)
        if agent:
            try:
                response = run_agent(agent, user_message)
                st.text_area("Agent:", response, height=200)
            except Exception as e:
                st.error(f"An error occurred while chatting: {e}")
                print(e)
        else:
            st.warning("Please index pages first.")

# Main App
def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Chat with Agent"])

    if page == "Home":
        st.title("Wikipedia Index and Chat Agent")
        
        # Display instructions on initial load
        if "instructions_shown" not in st.session_state:
            show_instructions()
            st.session_state["instructions_shown"] = True
        
        handle_settings()
    elif page == "Chat with Agent":
        handle_chat()

    # Ensure the OpenAI API key is set
    openai.api_key = get_apikey()

if __name__ == "__main__":
    main()
