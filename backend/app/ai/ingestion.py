"""
PDF Ingestion Pipeline
-----------------------
This module handles:
1. Reading PDF files (workout plans, diet plans)
2. Splitting text into meaningful chunks
3. Creating embeddings (vector representations)
4. Storing them in ChromaDB for semantic search

HOW IT WORKS:
- Your PDF files contain workout routines, diet plans, nutrition info
- We extract text, split it into ~500-token chunks with overlap
- Each chunk is converted to a vector embedding using OpenAI
- Stored in ChromaDB so we can search by meaning, not just keywords
- When a user asks "give me a bulking workout for gym", we find the
  most relevant chunks from your PDFs and feed them to the LLM
"""

import os
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from app.core.config import settings


def get_embeddings():
    return OpenAIEmbeddings(
        model=settings.EMBEDDING_MODEL,
        openai_api_key=settings.OPENAI_API_KEY,
    )


def get_vector_store():
    """Get or create the ChromaDB vector store."""
    return Chroma(
        collection_name="fitness_knowledge",
        embedding_function=get_embeddings(),
        persist_directory=settings.CHROMA_PERSIST_DIR,
    )


def ingest_pdfs(pdf_directory: str | None = None) -> dict:
    """
    Ingest all PDF files from the given directory into the vector store.

    Args:
        pdf_directory: Path to folder containing PDFs. Defaults to configured path.

    Returns:
        Summary dict with count of documents processed.
    """
    pdf_dir = pdf_directory or settings.PDF_UPLOAD_DIR
    os.makedirs(pdf_dir, exist_ok=True)

    # Load all PDFs from the directory
    loader = DirectoryLoader(
        pdf_dir,
        glob="**/*.pdf",
        loader_cls=PyPDFLoader,
        show_progress=True,
    )
    documents = loader.load()

    if not documents:
        return {"status": "no_documents", "count": 0}

    # Add metadata tags based on filename hints
    for doc in documents:
        source = Path(doc.metadata.get("source", "")).stem.lower()
        if "workout" in source or "exercise" in source:
            doc.metadata["category"] = "workout"
        elif "diet" in source or "nutrition" in source or "meal" in source:
            doc.metadata["category"] = "diet"
        else:
            doc.metadata["category"] = "general"

    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = text_splitter.split_documents(documents)

    # Store in vector DB
    vector_store = get_vector_store()
    vector_store.add_documents(chunks)

    return {
        "status": "success",
        "documents_loaded": len(documents),
        "chunks_created": len(chunks),
    }


def ingest_single_pdf(file_path: str, category: str = "general") -> dict:
    """Ingest a single PDF file."""
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    for doc in documents:
        doc.metadata["category"] = category

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    chunks = text_splitter.split_documents(documents)

    vector_store = get_vector_store()
    vector_store.add_documents(chunks)

    return {"status": "success", "chunks_created": len(chunks)}
