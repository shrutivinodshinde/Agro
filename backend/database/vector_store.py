import chromadb
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from backend.config import get_settings

# FIX: read embedding model name from settings (was hardcoded "sentence-transformers/all-MiniLM-L6-v2")
settings = get_settings()

CHROMA_PATH = "./data/chroma_db"

def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name=settings.HF_MODEL_NAME,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )

def get_vector_store() -> Chroma:
    return Chroma(
        collection_name="plant_disease_knowledge",
        embedding_function=get_embeddings(),
        persist_directory=CHROMA_PATH
    )

def ingest_disease_docs(docs_dir: str = "./data/disease_docs"):
    import os
    if not os.path.exists(docs_dir):
        os.makedirs(docs_dir)
        print(f"Created {docs_dir} — add PDFs here then run again")
        return

    pdf_files = [f for f in os.listdir(docs_dir) if f.endswith('.pdf')]
    if not pdf_files:
        print(f"No PDFs found in {docs_dir}")
        print("Add plant disease PDFs there, then run again")
        return

    loader = DirectoryLoader(
        docs_dir,
        glob="**/*.pdf",
        loader_cls=PyPDFLoader
    )
    docs = loader.load()
    print(f"Loaded {len(docs)} PDF pages from {len(pdf_files)} files")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = splitter.split_documents(docs)
    print(f"Created {len(chunks)} chunks")

    vectorstore = get_vector_store()
    vectorstore.add_documents(chunks)
    # persist() removed — chromadb 0.4+ auto-saves
    print("✅ Knowledge base built!")

if __name__ == "__main__":
    ingest_disease_docs()
