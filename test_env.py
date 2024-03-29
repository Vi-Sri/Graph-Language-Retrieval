import os
from dotenv import load_dotenv
load_dotenv()
print(os.environ.get("OPENAI_API_KEY"))