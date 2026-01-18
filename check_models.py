try:
    from google import genai
except ImportError:
    import google.generativeai as genai
    print("Using legacy google.generativeai SDK")
import os
from dotenv import load_dotenv

# Explicitly define path to .env file
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path, override=True)

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("API Key not found in .env")
    exit()

print(f"Using API Key: {api_key[:10]}...")

try:
    client = genai.Client(api_key=api_key)
    for model in client.models.list():
        print(model.name)
        
except Exception as e:
    print(f"Error: {e}")
