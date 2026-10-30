import truststore
truststore.inject_into_ssl()

import os
import numpy as np
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

embeddings = HuggingFaceEmbeddings(model_name=os.getenv("EMBEDDING_MODEL"))

question = "Which tube is used for HbA1c?"
sentences = [
    "HbA1c samples must be collected in a lavender-top EDTA tube.",
    "Lipid profile requires 10 to 12 hours of fasting.",
    "Used needles must be disposed of in a sharps container.",
]

question_vector = embeddings.embed_query(question)
sentence_vectors = embeddings.embed_documents(sentences)

print("Numbers per embedding:", len(question_vector))
print()
for sentence, vector in zip(sentences, sentence_vectors):
    score = np.dot(question_vector, vector) / (np.linalg.norm(question_vector) * np.linalg.norm(vector))
    print(f"{score:.3f}  {sentence}")