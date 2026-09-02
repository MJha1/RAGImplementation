import os
import glob
import chromadb
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env file (needs GROQ_API_KEY)
load_dotenv()

# Groq client for generating answers (reads GROQ_API_KEY from the environment).
client = Groq()

# The Groq chat model used to write answers. Run `client.models.list()` or see
# https://console.groq.com/docs/models for the models your key can access.
CHAT_MODEL = "openai/gpt-oss-120b"

# ChromaDB stores the document vectors on disk in ./chroma.
# It embeds text for us using a small model that runs locally (all-MiniLM-L6-v2),
# so embeddings need no API key and cost nothing. Groq has no embeddings API,
# which is why the embeddings are handled here instead of by Groq.
chroma_client = chromadb.PersistentClient(path="./chroma")
collection = chroma_client.get_or_create_collection("my_docs")


# Load the documents
def load_documents(folder="docs"):
    documents = []
    for path in glob.glob(os.path.join(folder, "*.txt")):
        with open(path, "r", encoding="utf-8") as f:
            documents.append((os.path.basename(path), f.read()))
    return documents


# Chunk the text into smaller pieces for embedding
def chunk_text(text, chunk_size=500, overlap=100):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


def build_index():
    documents = load_documents()
    all_chunks, metadatas, ids = [], [], []
    for filename, text in documents:
        for i, chunk in enumerate(chunk_text(text)):
            all_chunks.append(chunk)
            metadatas.append({"source": filename, "chunk": i})
            ids.append(f"{filename}-{i}")
    if not all_chunks:
        print("No documents found in ./docs — add some .txt files first.")
        return
    # Chroma embeds the chunks locally as it stores them. upsert lets us re-run
    # this safely without erroring on chunks that are already indexed.
    collection.upsert(documents=all_chunks, metadatas=metadatas, ids=ids)
    print(f"Indexed {len(all_chunks)} chunks from {len(documents)} document(s).")


def retrieve(question, n_results=3):
    # Chroma embeds the question locally and finds the closest chunks.
    results = collection.query(query_texts=[question], n_results=n_results)
    return results["documents"][0], results["metadatas"][0]


def answer_question(question):
    chunks, metadatas = retrieve(question)
    context = "\n\n".join(chunks)
    prompt = f"""Answer the question using ONLY the context below.
If the context doesn't contain the answer, say "I don't know based on the provided documents."

Context:
{context}

Question: {question}
"""
    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    answer = response.choices[0].message.content
    sources = ", ".join(sorted({m["source"] for m in metadatas}))
    return answer, sources


if __name__ == "__main__":
    build_index()
    print("\nAsk questions about your documents (type 'quit' to exit).\n")
    while True:
        question = input("You: ")
        if question.lower() in {"quit", "exit"}:
            break
        answer, sources = answer_question(question)
        print(f"\nAnswer: {answer}")
        print(f"(sources: {sources})\n")
