from llama_index.tools import QueryEngineTool, ToolMetadata
from llama_index.agent import ReActAgent
from llama_index.llms import OpenAI
from llama_index.callbacks.base import CallbackManager
from index_wikipages import create_index
from utils import get_apikey

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

    openai.api_key = get_apikey()
    llm = OpenAI(model=MODEL)
    callback_manager = CallbackManager([])
    agent = ReActAgent.from_tools(
        tools=query_engine_tools,
        llm=llm,
        callback_manager=callback_manager,
        verbose=True,
    )
    return agent

def run_agent(agent, message):
    query = message
    while True:
        tool_decision = agent.decide_tool_usage(query)
        tool_result = tool_decision.use_tool()
        outcome = agent.observe_tool_outcome(tool_result)
        if agent.is_outcome_sufficient(outcome):
            break
        else:
            query = agent.refine_query(query, outcome)
    response = agent.respond_to_query(outcome)
    return response
