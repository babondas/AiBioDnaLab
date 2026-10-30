from source_code.common.data_models import AgentAnswer
from source_code.guardrails.output_guardrails import OutputGuardrails

# Fake answers, one for each situation the proofreader must handle
test_answers = {
    "good answer":      AgentAnswer(text="HbA1c uses a lavender tube.", sources=[], tools_used=["lookup_table_rows"]),
    "empty answer":     AgentAnswer(text="", sources=[], tools_used=["search_lab_documents"]),
    "secret leaked":    AgentAnswer(text="My token is hf_abcdefghijklmnopqrstuvwxyz123", sources=[], tools_used=["search_lab_documents"]),
    "from memory":      AgentAnswer(text="HbA1c usually uses a purple tube.", sources=[], tools_used=[]),
    "honest not found": AgentAnswer(text="I couldn't find this in the BIODNA documents.", sources=[], tools_used=[]),
}

guardrails = OutputGuardrails()
for name, answer in test_answers.items():
    checked = guardrails.check_answer(answer)
    print(f"{name:17}  text: {checked.text}")
    if checked.warning:
        print(f"{'':17}  WARNING: {checked.warning}")