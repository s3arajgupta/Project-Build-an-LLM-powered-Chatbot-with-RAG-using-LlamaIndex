from llama_index import download_loader, VectorStoreIndex, ServiceContext
from llama_index.node_parser import SimpleNodeParser
from llama_index.text_splitter import get_default_text_splitter
import openai
from llama_index.llms import OpenAI as LlamaOpenAI
from pydantic import BaseModel
from llama_index.program import OpenAIPydanticProgram
from utils import get_apikey

# Define the data model in pydantic
class WikiPageList(BaseModel):
    "Data model for WikiPageList"
    pages: list

def wikipage_list(query, model):
    openai.api_key = get_apikey()

    prompt_template_str = """
    Given the input {query}, 
    extract the Wikipedia pages mentioned after 
    "please index:" and return them as a list.
    If only one page is mentioned, return a single
    element list.
    """

    llm = LlamaOpenAI(model=model)

    program = OpenAIPydanticProgram.from_defaults(
        output_cls=WikiPageList,
        prompt_template_str=prompt_template_str,
        verbose=True,
        llm=llm
    )

    wikipage_requests = program(query=query)
    return wikipage_requests

def create_wikidocs(wikipage_requests):
    custom_loader_path = './llamahub_modules'
    WikipediaReader = download_loader("WikipediaReader", custom_path=custom_loader_path)
    loader = WikipediaReader()
    documents = loader.load_data(pages=wikipage_requests.pages)
    return documents

def create_index(query, model):
    wikipage_requests = wikipage_list(query, model)
    documents = create_wikidocs(wikipage_requests)
    text_splits = get_default_text_splitter(chunk_size=150, chunk_overlap=45)
    parser = SimpleNodeParser.from_defaults(text_splitter=text_splits)
    service_context = ServiceContext.from_defaults(node_parser=parser)
    index = VectorStoreIndex.from_documents(documents, service_context=service_context)
    return index

if __name__ == "__main__":
    query = "/get wikipages: paris, lagos, lao"
    index = create_index(query)
    print("INDEX CREATED", index)
