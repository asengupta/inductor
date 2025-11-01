import os

import requests

# Your endpoint URL (you get this after creation)

API_URL = os.environ.get("HUGGING_FACE_API_URL")
HUGGING_FACE_API_TOKEN = os.environ.get("HUGGING_FACE_API_TOKEN")

headers = {"Authorization": f"Bearer {HUGGING_FACE_API_TOKEN}"}

def embed_texts(texts):
    response = requests.post(
        API_URL,
        headers=headers,
        json={"inputs": texts}
    )
    return response.json()

# Batch processing
texts = ["def hello():", "class MyClass:", "import numpy"]
embeddings = embed_texts(texts)
print(embeddings)
