"""Turns technical errors from Hugging Face (LLM or embeddings) into sentences users can act on.

Used by the agent (when answering) and by the app (when adding documents),
because both now call Hugging Face over the internet.
"""
from source_code.common import user_messages as messages


def explain_error(error: Exception) -> str:
    details = (type(error).__name__ + " " + str(error)).lower()

    if mentions_any(details, ["401", "403", "unauthorized", "forbidden", "invalid token", "invalid credentials"]):
        return messages.LLM_INVALID_TOKEN
    if mentions_any(details, ["402", "payment required", "credit"]):
        return messages.LLM_CREDITS_USED_UP
    if mentions_any(details, ["429", "rate limit", "too many requests"]):
        return messages.LLM_TOO_MANY_REQUESTS
    if mentions_any(details, ["404", "model not found", "not supported", "does not exist"]):
        return messages.LLM_MODEL_UNAVAILABLE
    if mentions_any(details, ["timeout", "timed out", "connect", "network", "getaddrinfo", "name resolution"]):
        return messages.LLM_NO_INTERNET
    return messages.LLM_UNKNOWN_ERROR


def mentions_any(text: str, words: list[str]) -> bool:
    for word in words:
        if word in text:
            return True
    return False
