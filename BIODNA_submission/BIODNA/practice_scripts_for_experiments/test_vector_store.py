from pathlib import Path

from source_code.rag_pipeline.step3_embedding import EmbeddingModel
from source_code.rag_pipeline.step4_vector_store import VectorStore
from source_code.rag_pipeline.pipeline_runner import add_uploaded_file_to_knowledge_base

print("Loading embedding model and database...")
vector_store = VectorStore(EmbeddingModel())

# Run all five sample documents through the pipeline
for file in sorted(Path("sample_documents_for_testing/supported_files").iterdir()):
    count = add_uploaded_file_to_knowledge_base(vector_store, file.name, file.read_bytes())
    print(f"Stored {count:3} chunks from {file.name}")

# Show the stored documents and their metadata
print("\nDocuments in the vector database:")
for document in vector_store.list_documents():
    print(f"   {document['file_name']}  ({document['file_type']}, {document['chunks']} chunks, uploaded {document['uploaded_at']})")

# Ask some questions
questions = [
    "Which tube is used for HbA1c?",
    "Does a lipid profile need fasting?",
    "What is the normal haemoglobin range for women?",
    "What should I do with a haemolysed sample?",
    "What is the critical value for potassium?",
    "Who won the cricket match yesterday?",
]
for question in questions:
    print(f"\nQ: {question}")
    results = vector_store.search(question)
    if not results:
        print("   No relevant chunks found")
    for result in results:
        preview = result.text[:70].replace("\n", " ")
        print(f"   {result.score:.3f}  {result.file_name} ({result.location}): {preview}")
