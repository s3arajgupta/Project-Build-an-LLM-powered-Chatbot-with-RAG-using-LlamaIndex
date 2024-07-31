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

# Display instructions on initial load
if "instructions_shown" not in st.session_state:
    show_instructions()
    st.session_state["instructions_shown"] = True

# Settings Section
st.header("Settings")
model_choice = st.selectbox("Choose Model:", ["gpt-3.5-turbo"])
query = st.text_input("Enter pages to index (comma-separated):", "paris, tokyo")
if st.button("Index Pages"):
    with st.spinner("Indexing..."):
        try:
            print(index)
            index = create_index(query)
            print("================================================")
            print(index)
            if index:
                st.success(f'Wikipage(s) "{query}" successfully indexed')
                agent = create_react_agent(model_choice)
                print(agent)
            else:
                # st.error("Failed to create index.")
                print("Failed to create index.")
        except Exception as e:
            # st.error(f"An error occurred: {e}")
            print(f"An error occurred: {e}")
            # print(e)

# Chat Box Section
st.header("Chat with Agent")
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
        st.warning("Please index pages first.")

# Ensure the OpenAI API key is set
openai.api_key = get_apikey()
