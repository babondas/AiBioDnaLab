from source_code.agent.lab_agent import LabAgent
from source_code.rag_pipeline.step3_embedding import EmbeddingModel
from source_code.rag_pipeline.step4_vector_store import VectorStore

print("Loading...")
agent = LabAgent(VectorStore(EmbeddingModel()))

questions = [
    "Which tube is used for HbA1c?",                    # lookup_table_rows
    "What is the critical value for potassium?",        # lookup_table_rows
    "What should I do with a haemolysed sample?",       # search_lab_documents
    "Which documents do you have?",                     # list_lab_documents
    "Who won the cricket match yesterday?",             # nothing found
]
for question in questions:
    print("\n" + "=" * 70)
    print("Q:", question)
    answer = agent.ask(question)
    print("\nA:", answer.text)
    print("\nChunks used:", [f"{s.file_name} ({s.location})" for s in answer.sources])
