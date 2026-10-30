import os
import truststore
truststore.inject_into_ssl()
from dotenv import load_dotenv
from huggingface_hub import InferenceClient, whoami

load_dotenv()

token = os.getenv("HF_TOKEN")
model = os.getenv("HF_MODEL")

# Check 1: is the token valid?
print("Logged in as:", whoami(token=token)["name"])

# Check 2: can we use the model?
client = InferenceClient(api_key=token)
response = client.chat_completion(
    model=model,
    messages=[{"role": "user", "content": "In one sentence, what does a pathology lab do?"}],
    max_tokens=100,
)
print("Model:", model)
print("Answer:", response.choices[0].message.content)