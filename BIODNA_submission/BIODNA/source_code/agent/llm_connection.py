"""Connects LangChain to the Hugging Face LLM (openai/gpt-oss-20b by default)."""
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

from source_code.common import config


def create_chat_model() -> ChatHuggingFace:
    endpoint = HuggingFaceEndpoint(
        repo_id=config.HF_MODEL,                       # which model
        huggingfacehub_api_token=config.HF_TOKEN,      # your token from .env
        provider="auto",                               # Hugging Face picks a server
        max_new_tokens=config.LLM_MAX_TOKENS,          # maximum reply length
        temperature=config.LLM_TEMPERATURE,            # low = factual
    )
    return ChatHuggingFace(llm=endpoint)