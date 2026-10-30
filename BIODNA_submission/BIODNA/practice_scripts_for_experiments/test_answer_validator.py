from source_code.agent.answer_validator import AnswerValidator
from source_code.common.data_models import AgentAnswer, SearchResult

# One real passage from the test catalog
passage = SearchResult(
    text="test_code: BIO001 | test_name: HbA1c | container: Lavender top (K2 EDTA) | turnaround_time_hours: 24",
    file_name="BIODNA_Test_Catalog.csv", file_type="csv", location="row 5",
    chunk_number=5, uploaded_at="", score=1.0,
)
question = "Which tube is used for HbA1c?"

answers_to_check = {
    "correct answer": "HbA1c uses a Lavender top (K2 EDTA) tube.",
    "wrong answer":   "HbA1c uses a Grey top (sodium fluoride) tube and takes 6 hours.",
}

validator = AnswerValidator()
for name, text in answers_to_check.items():
    answer = AgentAnswer(text=text, sources=[passage], tools_used=["lookup_table_rows"])
    checked = validator.validate(question, answer)
    print(f"\n{name}: {text}")
    print(f"   validated: {checked.validated}")
    print(f"   warning:   {checked.warning or '-'}")
