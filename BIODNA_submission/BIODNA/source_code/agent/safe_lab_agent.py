"""The agents with all their safety checks. The app calls only this class.

    SafeLabAgent.ask(question)
        |
        1. Input guardrails    (code)     -> blocked?  return the friendly message
        |
        2. Lab Agent           (agent 1)  -> plans, retrieves, reasons, writes the answer
        |                                    failed?   return a friendly message instead of crashing
        |
        3. Output guardrails   (code)     -> empty answer, secrets, "not found" clean-up
        |
        4. Answer Validator    (agent 2)  -> is every fact supported by the sources?
        |
        Answer

Usage:
    agent = SafeLabAgent(vector_store)
    answer = agent.ask("Which tube is used for HbA1c?")
"""
import logging

from source_code.agent.answer_validator import AnswerValidator
from source_code.agent.lab_agent import LabAgent
from source_code.common import config
from source_code.common.custom_errors import QuestionBlockedError
from source_code.common.data_models import AgentAnswer
from source_code.common.error_explainer import explain_error
from source_code.guardrails.input_guardrails import InputGuardrails
from source_code.guardrails.output_guardrails import OutputGuardrails
from source_code.rag_pipeline.step4_vector_store import VectorStore

logger = logging.getLogger("biodna")


class SafeLabAgent:

    def __init__(self, vector_store: VectorStore):
        self.input_guardrails = InputGuardrails()
        self.lab_agent = LabAgent(vector_store)
        self.output_guardrails = OutputGuardrails()
        self.answer_validator = AnswerValidator()

    def ask(self, question: str) -> AgentAnswer:
        # 1. Check the question
        try:
            self.input_guardrails.check_question(question)
        except QuestionBlockedError as error:
            return AgentAnswer(text=str(error), sources=[])

        # 2. Ask the Lab Agent
        try:
            answer = self.lab_agent.ask(question.strip())
        except Exception as error:
            logger.error("The agent failed: %s", error)       # technical details for the developer
            return AgentAnswer(text=explain_error(error), sources=[])

        # 3. Check the answer with code
        answer = self.output_guardrails.check_answer(answer)

        # 4. Check the answer with the second agent
        if config.VALIDATE_ANSWERS:
            answer = self.answer_validator.validate(question.strip(), answer)

        return answer
