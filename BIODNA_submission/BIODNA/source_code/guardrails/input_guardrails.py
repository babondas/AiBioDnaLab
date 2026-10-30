"""Checks every question BEFORE it reaches the LLM.

    Question
       |
    1. Is it empty?                         -> "Please type a question."
    2. Is it too short or too long?         -> ask for a proper question
    3. Does it contain any words?           -> "1234 ???" is not a question
    4. Does it try to change the rules?     -> prompt injection, blocked
    5. Does it ask for a diagnosis?         -> blocked, refer to a doctor
    6. Does it contain personal data?       -> phone, Aadhaar, email: blocked
       |
    Question is safe to send to the agent

Why: the system prompt asks the LLM to behave, but an LLM can be tricked.
These checks run in our own code, so they cannot be bypassed.

Usage:
    InputGuardrails().check_question(question)    # raises QuestionBlockedError if unsafe
"""
import re

from source_code.common import config
from source_code.common import user_messages as messages
from source_code.common.custom_errors import QuestionBlockedError

# Phrases that try to make the LLM ignore or reveal its rules
PROMPT_INJECTION_PHRASES = [
    "ignore your rules", "ignore your instructions", "ignore previous", "ignore all previous",
    "ignore the above", "forget your instructions", "forget your rules", "disregard your",
    "you are now", "pretend to be", "reveal your", "show your system prompt",
    "system prompt", "developer mode", "jailbreak",
]

# Phrases that ask for a diagnosis, a patient's result interpretation or treatment
DIAGNOSIS_PHRASES = [
    "do i have", "does he have", "does she have", "does my patient have", "am i diabetic",
    "diagnose", "diagnosis", "prescribe", "what medicine", "which medicine", "should i take",
    "my result", "my report", "my test result",
]


class InputGuardrails:

    def check_question(self, question: str):
        """Runs every check in order. Raises QuestionBlockedError at the first problem."""
        question = question.strip()

        self.check_not_empty(question)
        self.check_length(question)
        self.check_has_words(question)
        self.check_no_prompt_injection(question)
        self.check_no_diagnosis_request(question)
        self.check_no_personal_data(question)

    def check_not_empty(self, question: str):
        if question == "":
            raise QuestionBlockedError(messages.QUESTION_IS_EMPTY)

    def check_length(self, question: str):
        if len(question) < config.MIN_QUESTION_LENGTH:
            raise QuestionBlockedError(messages.QUESTION_TOO_SHORT)
        if len(question) > config.MAX_QUESTION_LENGTH:
            raise QuestionBlockedError(messages.QUESTION_TOO_LONG)

    def check_has_words(self, question: str):
        has_a_letter = any(character.isalpha() for character in question)
        if not has_a_letter:
            raise QuestionBlockedError(messages.QUESTION_HAS_NO_WORDS)

    def check_no_prompt_injection(self, question: str):
        if self.contains_any_phrase(question, PROMPT_INJECTION_PHRASES):
            raise QuestionBlockedError(messages.PROMPT_INJECTION_BLOCKED)

    def check_no_diagnosis_request(self, question: str):
        if self.contains_any_phrase(question, DIAGNOSIS_PHRASES):
            raise QuestionBlockedError(messages.DIAGNOSIS_BLOCKED)

    def check_no_personal_data(self, question: str):
        phone_number = r"\b[6-9]\d{9}\b"                     # Indian mobile: 10 digits starting 6-9
        aadhaar_number = r"\b\d{4}\s?\d{4}\s?\d{4}\b"        # 12 digits, spaces optional
        email_address = r"\b[\w.+-]+@[\w-]+\.[\w.]+\b"

        for pattern in [phone_number, aadhaar_number, email_address]:
            if re.search(pattern, question):
                raise QuestionBlockedError(messages.PERSONAL_DATA_BLOCKED)

    def contains_any_phrase(self, question: str, phrases: list[str]) -> bool:
        lowered = question.lower()
        for phrase in phrases:
            if phrase in lowered:
                return True
        return False