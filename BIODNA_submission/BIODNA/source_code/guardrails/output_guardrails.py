"""Checks every answer AFTER the LLM writes it, before the user sees it.

    Answer from the agent
       |
    1. Is it empty?                           -> replace with "couldn't find a clear answer"
    2. Does it contain a secret (API token)?  -> hide it
    3. Was it based on the documents?         -> if no tool was used, add a warning
    4. Does it say "not found"?               -> remove the sources, they did not answer it
       |
    Answer shown to the user

Usage:
    answer = OutputGuardrails().check_answer(answer)
"""
import re

from source_code.common import user_messages as messages
from source_code.common.data_models import AgentAnswer


class OutputGuardrails:

    def check_answer(self, answer: AgentAnswer) -> AgentAnswer:
        """Runs every check in order and returns the checked answer."""
        answer = self.replace_empty_answer(answer)
        answer = self.hide_secrets(answer)
        answer = self.warn_if_not_from_documents(answer)
        answer = self.remove_sources_if_not_found(answer)
        return answer

    def replace_empty_answer(self, answer: AgentAnswer) -> AgentAnswer:
        """Check 1: the AI wrote nothing."""
        if answer.text is None or answer.text.strip() == "":
            answer.text = messages.AGENT_NO_CLEAR_ANSWER
        return answer

    def hide_secrets(self, answer: AgentAnswer) -> AgentAnswer:
        """Check 2: Hugging Face tokens start with 'hf_'. They must never be shown."""
        answer.text = re.sub(r"hf_[A-Za-z0-9]{20,}", "[hidden]", answer.text)
        return answer

    def warn_if_not_from_documents(self, answer: AgentAnswer) -> AgentAnswer:
        """Check 3: if no tool was used, the AI answered from its own memory."""
        no_tool_was_used = len(answer.tools_used) == 0
        is_not_found_reply = messages.NOT_FOUND_IN_DOCUMENTS in answer.text

        if no_tool_was_used and not is_not_found_reply:
            answer.warning = messages.ANSWER_NOT_FROM_DOCUMENTS
        return answer

    def remove_sources_if_not_found(self, answer: AgentAnswer) -> AgentAnswer:
        """Check 4: an answer that says 'not found' should not show sources."""
        says_not_found = messages.NOT_FOUND_IN_DOCUMENTS in answer.text
        says_no_clear_answer = messages.AGENT_NO_CLEAR_ANSWER in answer.text

        if says_not_found or says_no_clear_answer:
            answer.sources = []
        return answer
