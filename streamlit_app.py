import streamlit as st
from index_wikipages import create_index
from chat_agent import create_react_agent
import openai
from utils import get_apikey

# Initialize global variables
index = None
agent = None

st.title("Wikipedia Index and Chat Agent")

# Display the instructions from chainlit.md
def show_instructions():
    with open("chainlit.md", "r") as file:
        instructions = file.read()
    st.markdown(instructions)

show_instructions()

# Section to index Wikipedia pages
st.header("Index Wikipedia Pages")
query = st.text_input("Enter pages to index (comma-separated):", "paris, lagos, lao")
if st.button("Index Pages"):
    with st.spinner("Indexing..."):
        index = create_index(query)
        st.success("Indexing completed")

# Section to interact with the chat agent
st.header("Chat with Agent")
if index:
    model_choice = st.selectbox("Choose Model:", ["gpt-3.5-turbo"])
    user_message = st.text_input("You: ")
    if st.button("Send"):
        if not agent:
            agent = create_react_agent(model_choice)
        
        response = agent.chat(user_message)
        st.text_area("Agent:", response, height=200)
else:
    st.warning("Please index pages first.")

# Ensure the OpenAI API key is set
openai.api_key = get_apikey()
