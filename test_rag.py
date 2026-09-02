#!/usr/bin/env python
"""Quick test script to verify RAG application works correctly."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Verify API key is loaded
api_key = os.getenv('GROQ_API_KEY')
if not api_key or api_key == 'your-groq-api-key-here':
    print("[ERROR] Please set your GROQ_API_KEY in the .env file")
    exit(1)

print("[OK] API key loaded successfully")

# Import and test the RAG module
try:
    import rag
    print("[OK] RAG module imported successfully")
except Exception as e:
    print(f"[ERROR] Failed to import RAG module: {e}")
    exit(1)

# Test document loading
try:
    print("\n--- Testing Document Loading ---")
    documents = rag.load_documents()
    print(f"[OK] Loaded {len(documents)} documents:")
    for filename, content in documents:
        print(f"  - {filename} ({len(content)} characters)")
except Exception as e:
    print(f"[ERROR] Failed to load documents: {e}")
    exit(1)

# Test indexing
try:
    print("\n--- Testing Indexing ---")
    rag.build_index()
    print("[OK] Successfully indexed documents")
except Exception as e:
    print(f"[ERROR] Failed to index documents: {e}")
    exit(1)

# Test query
try:
    print("\n--- Testing Query ---")
    test_question = "What information is available?"
    print(f"Question: {test_question}")
    answer, sources = rag.answer_question(test_question)
    print(f"\nAnswer: {answer}")
    print(f"Sources: {sources}")
    print("\n[OK] Query successful!")
except Exception as e:
    print(f"[ERROR] Failed to query: {e}")
    exit(1)

print("\n" + "="*50)
print("[SUCCESS] ALL TESTS PASSED!")
print("="*50)
print("\nYour RAG application is working correctly.")
print("Run: .\\venv\\Scripts\\python.exe rag.py")
