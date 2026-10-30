from langchain_core.tools import tool
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

from source_code.common import config


# STEP 1: Write a normal Python function, and mark it as a "tool"
#         The text in """ """ tells the AI what this tool is for. The AI reads it!
@tool
def get_lab_opening_hours(day: str) -> str:
    """Returns the BIODNA lab's sample collection hours for a given day of the week."""
    return "Monday to Saturday 7:00 AM to 8:00 PM; Sunday 7:00 AM to 1:00 PM."


# STEP 2: Connect to the AI model on Hugging Face
endpoint = HuggingFaceEndpoint(
    repo_id=config.HF_MODEL,                    # which model: openai/gpt-oss-20b
    huggingfacehub_api_token=config.HF_TOKEN,   # your login token from .env
    provider="auto",                            # Hugging Face picks a server for us
    max_new_tokens=512,                         # maximum length of the AI's reply
    temperature=0.1,                            # low = less creative, more factual
)
chat_model = ChatHuggingFace(llm=endpoint)      # wrap it so LangChain can talk to it


# STEP 3: Tell the AI "you are allowed to use this tool"
model_with_tools = chat_model.bind_tools([get_lab_opening_hours])


# STEP 4: Ask a question and see what the AI decides
response = model_with_tools.invoke("What time does the BIODNA lab open on Sunday?")

print("Model:", config.HF_MODEL)
print("Tool calls:", response.tool_calls)       # which tool the AI wants to use, and with what input
print("Text reply:", response.content)          # any text the AI wrote