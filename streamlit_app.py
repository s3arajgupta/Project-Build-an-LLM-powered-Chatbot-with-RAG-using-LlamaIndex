import streamlit as st
from index_wikipages import create_index
from chat_agent import create_react_agent, run_agent
import openai
from utils import get_apikey
import os

# Initialize session state variables
if "index" not in st.session_state:
    st.session_state.index = None
if "agent" not in st.session_state:
    st.session_state.agent = None
if "model_choice" not in st.session_state:
    st.session_state.model_choice = None
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "user_message" not in st.session_state:
    st.session_state.user_message = ""

# Function to show instructions
def show_intro():
    with open("show_intro.md", "r") as file:
        instructions = file.read()
    st.markdown(instructions)

# Function to show end instructions
def show_end():
    with open("show_end.md", "r") as file:
        instructions = file.read()
    st.markdown(instructions)

# Function to handle settings
def handle_settings():
    st.header("Settings")
    st.session_state.model_choice = st.selectbox("Choose Model:", [None, "gpt-3.5-turbo"], index=[None, "gpt-3.5-turbo"].index(st.session_state.model_choice))
    query = st.text_input("Enter pages to index (comma-separated):", placeholder="Batman, Paris, Sesame Street, Star Wars: Episode V - The Empire Strikes Back")
    if st.button("Index Pages"):
        with st.spinner("Indexing..."):
            try:
                st.session_state.index = create_index(query, st.session_state.model_choice)
                if st.session_state.index:
                    st.success(f'Wikipage(s) "{query}" successfully indexed.')
                else:
                    st.error("Failed to create index.")
            except Exception as e:
                st.error(f"An error occurred: {e}")
                print(e)

# Function to handle chat input submission
def submit_message():
    if st.session_state.agent and st.session_state.user_message:
        try:
            response = run_agent(st.session_state.agent, st.session_state.user_message)
            st.session_state.conversation_history.append(("You", st.session_state.user_message))
            st.session_state.conversation_history.append(("Agent", response))
            st.session_state.user_message = ""  # Clear the input field after sending
        except Exception as e:
            st.error(f"An error occurred while chatting: {e}")
            print(e)

# Function to handle chat
def handle_chat():
    if st.session_state.index and st.session_state.model_choice:
        st.session_state.agent = create_react_agent(st.session_state.model_choice, st.session_state.index)
        st.header("Chat with Agent")

        st.text_input("You:", key="user_message", on_change=submit_message)

        # Add CSS for fade-in animation
        st.markdown("""
            <style>
                @keyframes fadeIn {
                    0% { opacity: 0; }
                    100% { opacity: 1; }
                }
                .fade-in {
                    animation: fadeIn 1.5s ease-in-out;
                }
            </style>
        """, unsafe_allow_html=True)

        # Display conversation history in reverse order
        for speaker, message in reversed(st.session_state.conversation_history):
            if speaker == "You":
                st.markdown(f"""
                    <div class='fade-in' style='background-color: #d3f3d3; padding: 10px; border-radius: 5px; margin-bottom: 5px;color: #000000;'>
                        <strong>You:</strong> {message}
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class='fade-in' style='background-color: #f3f3d3; padding: 10px; border-radius: 5px; margin-bottom: 5px; color: #000000;'>
                        <strong>Agent:</strong> {message}
                    </div>
                """, unsafe_allow_html=True)
    elif st.session_state.index:
        st.warning("Please choose a Model at home page.")
    elif st.session_state.model_choice:
        st.warning("Please create some indexes of Wikipedia page(s) at home page.")
    else:
        st.warning("Please choose a Model at home page.")
        st.warning("Please create indexe(s) of Wikipedia page(s) at home page.")

# Main App
def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Chat with Agent"])
    if st.sidebar.button("Reset and Clear Cache"):
        st.cache_data.clear()
        st.session_state.index = None
        st.session_state.user_message = ""
        st.session_state.conversation_history = []
        st.session_state.model_choice = None
        st.session_state.agent = None
        st.session_state.page = "Home"

    if page == "Home":
        st.title("🎉Welcome🎊 to Wikipedia Indexing & Chat Agent")
        
        # if "instructions_shown" not in st.session_state:
        #     show_intro()
        #     st.session_state["instructions_shown"] = True
        show_intro()
        handle_settings()
        show_end()

    elif page == "Chat with Agent":
        handle_chat()

    # Ensure the OpenAI API key is set
    openai.api_key = get_apikey()

if __name__ == "__main__":
    main()

# .\myenv311\Scripts\activate
# streamlit run streamlit_app.py