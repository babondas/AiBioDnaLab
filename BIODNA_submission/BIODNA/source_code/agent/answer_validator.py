"""The second agent: the Answer Validator.

It reviews the Lab Agent's answer and checks that every fact in it
is supported by the passages the answer was based on.

    question + answer + passages
            |
    chain = prompt | model | parser
            |
    "SUPPORTED"                         -> answer.validated = True
    "NOT_SUPPORTED: <reason>"           -> warning with the reason
    (the LLM call fails)                -> warning: could not be checked

Answers without passages (blocked questions, "not found", the document list)
are skipped, because there is nothing to check them against.

Usage:
    answer = AnswerValidator().validate(question, answer)
"""
import logging

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from source_code.agent.agent_instructions import VALIDATOR_PROMPT
from source_code.agent.llm_connection import create_chat_model
from source_code.common import user_messages as messages
from source_code.common.data_models import AgentAnswer, SearchResult

logger = logging.getLogger("biodna")


class AnswerValidator:

    def __init__(self):
        prompt = ChatPromptTemplate.from_messages([
            ("system", VALIDATOR_PROMPT),
            ("human", "Question:\n{question}\n\nAnswer to check:\n{answer}\n\nPassages:\n{passages}"),
        ])
        # prompt -> LLM -> plain text
        self.chain = prompt | create_chat_model() | StrOutputParser()

    # ---------------------------------------------------------------
    # Public method
    # ---------------------------------------------------------------
    def validate(self, question: str, answer: AgentAnswer) -> AgentAnswer:
        if len(answer.sources) == 0:
            return answer                                  # nothing to check against

        try:
            verdict = self.chain.invoke({
                "question": question,
                "answer": answer.text,
                "passages": self._format_passages(answer.sources),
            })
        except Exception as error:
            logger.warning("The Answer Validator failed: %s", error)
            self._add_warning(answer, messages.ANSWER_COULD_NOT_BE_VALIDATED)
            return answer

        if self._is_supported(verdict):
            answer.validated = True
        else:
            reason = self._get_reason(verdict)
            self._add_warning(answer, messages.ANSWER_NOT_SUPPORTED.format(reason=reason))
        return answer

    # ---------------------------------------------------------------
    # Private helper methods
    # ---------------------------------------------------------------
    def _format_passages(self, sources: list[SearchResult]) -> str:
        passages = []
        for number, source in enumerate(sources, start=1):
            passages.append(f"[Passage {number}: {source.file_name} ({source.location})]\n{source.text}")
        return "\n\n".join(passages)

    def _is_supported(self, verdict: str) -> bool:
        first_line = verdict.strip().split("\n")[0].upper()
        return first_line.startswith("SUPPORTED")

    def _get_reason(self, verdict: str) -> str:
        """From 'NOT_SUPPORTED: the tube colour is wrong', returns 'the tube colour is wrong'."""
        first_line = verdict.strip().split("\n")[0]
        if ":" in first_line:
            return first_line.split(":", 1)[1].strip()
        return "no reason was given."

    def _add_warning(self, answer: AgentAnswer, warning: str):
        if answer.warning:
            answer.warning = answer.warning + " " + warning
        else:
            answer.warning = warning
