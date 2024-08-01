import streamlit as st
from index_wikipages import create_index
from chat_agent import create_react_agent, run_agent
import openai
from utils import get_apikey

# Initialize session state variables
if "index" not in st.session_state:
    st.session_state.index = None
if "agent" not in st.session_state:
    st.session_state.agent = None
if "model_choice" not in st.session_state:
    st.session_state.model_choice = None

# Function to show instructions
def show_instructions():
    with open("chainlit.md", "r") as file:
        instructions = file.read()
    st.markdown(instructions)

# Function to handle settings
def handle_settings():
    st.header("Settings")
    st.session_state.model_choice = st.selectbox("Choose Model:", ["gpt-3.5-turbo"])
    query = st.text_input("Enter pages to index (comma-separated):", "paris, tokyo")
    if st.button("Index Pages"):
        with st.spinner("Indexing..."):
            try:
                st.session_state.index = create_index(query)
                if st.session_state.index:
                    st.success(f'Wikipage(s) "{query}" successfully indexed.')
                else:
                    st.error("Failed to create index.")
            except Exception as e:
                st.error(f"An error occurred: {e}")
                print(e)

# Function to handle chat
def handle_chat():
    
    st.write("handle_chat 0 ", st.session_state.index, st.session_state.agent, st.session_state.model_choice)
    
    if st.session_state.index and st.session_state.model_choice:
        st.session_state.agent = create_react_agent(st.session_state.model_choice, st.session_state.index)
        st.header("Chat with Agent")
        user_message = st.text_input("You: ")
        if st.button("Send"):
            if st.session_state.agent:
                try:
                    response = run_agent(st.session_state.agent, user_message)
                    st.text_area("Agent:", response, height=200)
                except Exception as e:
                    st.error(f"An error occurred while chatting: {e}")
                    print(e)
            else:
                st.warning("Please index pages first.")
    else:
        st.warning("Please set up the settings first.")

# Main App
def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Chat with Agent"])

    if page == "Home":
        st.title("Wikipedia Index and Chat Agent")
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
