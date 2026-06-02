# test_llm.py
import sys
sys.path.insert(0, ".")

def test_llm():
    print("\n" + "="*50)
    print("  TESTING OLLAMA LLM")
    print("="*50 + "\n")

    print("Connecting to Ollama at http://localhost:11434...")
    try:
        from langchain_ollama import ChatOllama
        llm = ChatOllama(
            model="llama3",
            base_url="http://localhost:11434",
            temperature=0.3
        )

        print("Sending test message (may take 30-60s first time)...")
        response = llm.invoke(
            "In exactly one sentence, what causes Late Blight in tomatoes?"
        )

        print("✅ Ollama LLM — WORKING!\n")
        print(f"  Response: {response.content}\n")

    except Exception as e:
        print(f"❌ Ollama LLM — FAILED: {e}")
        print("\nFixes:")
        print("  1. Open new terminal: ollama serve")
        print("  2. Pull model: ollama pull llama3")
        print("  3. Check RAM — llama3 needs 8GB+ free RAM")
        print("  4. Try smaller model: ollama pull mistral")
        print("     Then change OLLAMA_MODEL=mistral in .env")
        import traceback
        traceback.print_exc()

test_llm()