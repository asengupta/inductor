import numpy as np
from transformers import AutoModel, AutoTokenizer
import torch
import torch.nn.functional as F

checkpoint = "codesage/codesage-large-v2"
device = "cpu"  # for GPU usage or "cpu" for CPU usage

# Note: CodeSage requires adding eos token at the end of each tokenized sequence

# tokenizer = AutoTokenizer.from_pretrained(checkpoint, trust_remote_code=True, add_eos_token=True)
#
# model = AutoModel.from_pretrained(checkpoint, trust_remote_code=True).to(device)
#
# inputs = tokenizer.encode("def print_hello_world():\tprint('Hello World!')", return_tensors="pt").to(device)
# queries = ['Calculate the n-th factorial']
# tokenised_queries = tokenizer.encode("Calculate the n-th factorial", return_tensors="pt").to(device)
# code_emb = model(inputs)
# query_emb = model(tokenised_queries)
#
# code_embedding = code_emb[0].mean(dim=0)  # Average pooling across sequence length
# query_embedding = query_emb[0].mean(dim=0)  # Average pooling across sequence length
#
# code_embedding_normalized = F.normalize(code_embedding, p=2, dim=0)
# query_embedding_normalized = F.normalize(query_embedding, p=2, dim=0)
#
# print("Code embedding shape:", code_emb[0].shape)
# print("Query embedding shape:", query_emb[0].shape)

from sentence_transformers import SentenceTransformer

# queries = ['Calculate the factorial of a number']
queries = ['This line processes an order and handles errors and also displays status']
# code_snippets = ['def fact(n):\n if n < 0:\n  raise ValueError\n return 1 if n == 0 else n * fact(n - 1)']
code_snippets = ['''PROCESS-ORDER.
                 MULTIPLY ITEM-COUNT BY ITEM-PRICE
                 GIVING ORDER-TOTAL.
                 IF ORDER-TOTAL > 0
                 MOVE "PROCESSED" TO ORDER-STATUS
                 ELSE
                 MOVE "ERROR" TO ORDER-STATUS
                 END-IF.
                 DISPLAY "ORDER " ORDER-ID " TOTAL: $" ORDER-TOTAL.
                 DISPLAY "STATUS: " ORDER-STATUS.
                 STOP RUN.''']

# model = SentenceTransformer("nomic-ai/nomic-embed-code")
# model = SentenceTransformer("codesage/codesage-large-v2", trust_remote_code=True)
# model = SentenceTransformer("nomic-ai/nomic-embed-text-v1.5", trust_remote_code=True)
model = SentenceTransformer("jinaai/jina-embeddings-v4", trust_remote_code=True)
query_emb = model.encode(queries, task="retrieval", prompt_name="query")
code_emb = model.encode(code_snippets, task="retrieval", prompt_name="query")

query_embedding = query_emb[0]
code_embedding = code_emb[0]
similarity = model.similarity(query_embedding, code_embedding)
print("Code embedding shape:", code_embedding.shape)
print("Query embedding shape:", query_embedding.shape)

normalised_query_embedding = query_embedding / np.linalg.norm(query_embedding)
normalised_code_embedding = code_embedding / np.linalg.norm(code_embedding)

similarity_np = np.dot(normalised_query_embedding, normalised_code_embedding)
per_dim_contrib = normalised_query_embedding * normalised_code_embedding

topk = np.argsort(per_dim_contrib)[-10:]   # top 10 contributing dimensions
# for k in topk:
#     print(f"{k}-{per_dim_contrib[k]}")
print("Top contributing dims:", topk)
print("Top contrib values:", per_dim_contrib[topk])

print(similarity)
