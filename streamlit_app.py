import os
import sys
import tempfile
import streamlit as st
# Access the API key from the environment variable
api_key = os.getenv('OPENAI_API_KEY')
if api_key:
    st.write("API Key found")
else:
    st.write("API Key not found")
    
import chainlit as cl
from llama_index import download_loader, VectorStoreIndex, ServiceContext
from llama_index.node_parser import SimpleNodeParser
from llama_index.text_splitter import get_default_text_splitter
from llama_index.tools import QueryEngineTool, ToolMetadata
from llama_index.agent import ReActAgent
from llama_index.llms import OpenAI
from llama_index.callbacks.base import CallbackManager
from llama_index.program import OpenAIPydanticProgram
from llama_index.llms import OpenAI as LlamaOpenAI

from pydantic import BaseModel

from utils import get_apikey
import openai

# Define the data model in pydantic
class WikiPageList(BaseModel):
    "Data model for WikiPageList"
    pages: list

def wikipage_list(query):
    # openai.api_key = get_apikey()
    openai.api_key = api_key

    prompt_template_str = """
    Given the input {query}, 
    extract the Wikipedia pages mentioned after 
    "please index:" and return them as a list.
    If only one page is mentioned, return a single
    element list.
    """

    llm = LlamaOpenAI(model="gpt-3.5-turbo")  # Explicitly set the model to gpt-3.5-turbo

    program = OpenAIPydanticProgram.from_defaults(
        output_cls=WikiPageList,
        prompt_template_str=prompt_template_str,
        verbose=True,
        llm=llm
    )


    wikipage_requests = program(query=query)

    return wikipage_requests.pages

# def create_wikidocs(wikipage_requests):
#     WikipediaReader = download_loader("WikipediaReader")
#     loader = WikipediaReader()
#     documents = loader.load_data(pages=wikipage_requests)
#     return documents

# def create_wikidocs(wikipage_requests):
#     # Use a temporary directory for downloading modules
#     with tempfile.TemporaryDirectory() as temp_dir:
#         WikipediaReader = download_loader("WikipediaReader", download_dir=temp_dir)
#         loader = WikipediaReader()
#         documents = loader.load_data(pages=wikipage_requests)
#     return documents

# def create_wikidocs(wikipage_requests):
#     # Set the environment variable for the temporary directory
#     with tempfile.TemporaryDirectory() as temp_dir:
#         os.environ['LLAMA_INDEX_MODULE_DIR'] = temp_dir
#         WikipediaReader = download_loader("WikipediaReader")
#         loader = WikipediaReader()
#         documents = loader.load_data(pages=wikipage_requests)
#     return documents

def create_wikidocs(wikipage_requests):
    # Create a custom directory for the modules
    with tempfile.TemporaryDirectory() as temp_dir:
        custom_module_dir = os.path.join(temp_dir, "llamahub_modules")
        os.makedirs(custom_module_dir, exist_ok=True)
        
        # Add the custom directory to sys.path
        sys.path.insert(0, custom_module_dir)
        
        # Now, use the custom directory for downloading modules
        WikipediaReader = download_loader("WikipediaReader")
        loader = WikipediaReader()
        documents = loader.load_data(pages=wikipage_requests)
        
        # Remove the custom directory from sys.path
        sys.path.pop(0)
        
    return documents

def create_index(query):
    wikipage_requests = wikipage_list(query)
    documents = create_wikidocs(wikipage_requests)
    text_splits = get_default_text_splitter(chunk_size=150, chunk_overlap=45)
    parser = SimpleNodeParser.from_defaults(text_splitter=text_splits)
    service_context = ServiceContext.from_defaults(node_parser=parser)
    index = VectorStoreIndex.from_documents(documents, service_context=service_context)
    return index

def wikisearch_engine(index):
    query_engine = index.as_query_engine(
        response_mode="compact", verbose=True, similarity_top_k=10
    )
    return query_engine

def create_react_agent(MODEL, index):
    query_engine_tools = [
        QueryEngineTool(
            query_engine=wikisearch_engine(index),
            metadata=ToolMetadata(
                name="Wikipedia Search",
                description="Useful for performing searches on the wikipedia knowledgebase",
            ),
        )
    ]

    # openai.api_key = get_apikey()
    openai.api_key = api_key
    llm = OpenAI(model=MODEL)
    agent = ReActAgent.from_tools(
        tools=query_engine_tools,
        llm=llm,
        callback_manager=CallbackManager([cl.LlamaIndexCallbackHandler()]),
        verbose=True,
    )
    return agent

# Streamlit UI
st.title("Chainlit RAG POC with Streamlit")
st.write("This is a Chainlit app running on Streamlit.")

query = st.text_input("Enter Wikipage Request", "")
model = st.selectbox("Select OpenAI Model", ["gpt-3.5-turbo"])

if st.button("Run Chainlit"):
    with st.spinner('Indexing Wikipage(s)...'):
        index = create_index(query)
        agent = create_react_agent(model, index)
        st.success(f'Wikipage(s) "{query}" successfully indexed')

message = st.text_input("Enter your message:", "")

if st.button("Send"):
    if 'agent' in locals():
        response = agent.chat(message)
        st.write(response)
    else:
        st.error("Please index the Wikipages first.")
