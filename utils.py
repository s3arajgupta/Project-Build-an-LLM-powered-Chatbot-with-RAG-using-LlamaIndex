import os 
import yaml
from dotenv import load_dotenv

load_dotenv()

def get_apikey():
    # """
    # Reads API key from a configuration file.

    # This function opens a configuration file named "apikeys.yml", reads the 
    # API key for OpenAI

    # Returns: api_key (str): The OpenAI API key.
    # """
    
    # # Construct the full path to the configuration file
    # file_path = os.path.join("apikeys.yml")

    # with open(file_path, 'r') as yamlfile:
    #     loaded_yamlfile = yaml.safe_load(yamlfile)
    #     API_KEY = loaded_yamlfile['openai']['api_key']
        
    return os.getenv('OPENAI_API_KEY')

if __name__ == "__main__":
    print("API_KEY", get_apikey())

# python utils.py