"""
PDF Ingestion Pipeline
-----------------------
This module handles:
1. Reading PDF files (workout plans, diet plans)
2. Splitting text into meaningful chunks
3. Creating embeddings (vector representations)
4. Storing them in ChromaDB for semantic search

EXPECTED FOLDER STRUCTURE:
    data/pdfs/
    ├── DietPlans/
    │   ├── 3300 calories diet/
    │   │   └── plan.pdf
    │   ├── 2500 calories diet/
    │   │   └── plan.pdf
    │   └── ...
    └── WorkoutPlans/
        ├── Push Pull Legs/
        │   └── routine.pdf
        ├── Full Body Home/
        │   └── routine.pdf
        └── ...

Metadata extracted per chunk:
  - category: "diet" or "workout" (from top-level folder name)
  - subcategory: subfolder name, e.g. "3300 calories diet" (plan label)
  - calories: extracted calorie number if present in folder name
  - filename: original PDF filename
  - source: full file path
"""

import os
import re
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
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


def _extract_metadata_from_path(file_path: str, base_dir: str) -> dict:
    """
    Extract rich metadata from the folder structure.

    Given: data/pdfs/DietPlans/3300 calories diet/plan.pdf
    Returns: {
        "category": "diet",
        "subcategory": "3300 calories diet",
        "calories": 3300,
        "filename": "plan.pdf",
    }
    """
    rel_path = Path(file_path).relative_to(base_dir)
    parts = rel_path.parts  # e.g. ("DietPlans", "3300 calories diet", "plan.pdf")

    metadata = {"filename": parts[-1] if parts else "unknown"}

    # Detect category from top-level folder name
    if len(parts) >= 2:
        top_folder = parts[0].lower().replace(" ", "").replace("_", "")
        if "diet" in top_folder or "nutrition" in top_folder or "meal" in top_folder:
            metadata["category"] = "diet"
        elif "workout" in top_folder or "exercise" in top_folder or "training" in top_folder:
            metadata["category"] = "workout"
        else:
            metadata["category"] = "general"
    else:
        metadata["category"] = "general"

    # Extract subcategory from subfolder name (e.g. "3300 calories diet")
    if len(parts) >= 3:
        metadata["subcategory"] = parts[1]

        # Try to extract calorie number from subfolder name
        calorie_match = re.search(r"(\d{3,5})\s*cal", parts[1], re.IGNORECASE)
        if calorie_match:
            metadata["calories"] = int(calorie_match.group(1))
    elif len(parts) >= 2:
        # PDF directly in category folder (no subfolder)
        metadata["subcategory"] = Path(parts[-1]).stem

    return metadata


def _discover_pdfs(base_dir: str) -> list[Path]:
    """Recursively find all PDF files under base_dir."""
    base = Path(base_dir)
    return sorted(base.rglob("*.pdf"))


def ingest_pdfs(pdf_directory: str | None = None) -> dict:
    """
    Ingest all PDF files from the given directory into the vector store.
    Walks through DietPlans/ and WorkoutPlans/ subfolders, extracting
    metadata from the folder structure.

    Args:
        pdf_directory: Path to folder containing PDFs. Defaults to configured path.

    Returns:
        Summary dict with count of documents processed and breakdown by category.
    """
    pdf_dir = pdf_directory or settings.PDF_UPLOAD_DIR
    os.makedirs(pdf_dir, exist_ok=True)

    pdf_files = _discover_pdfs(pdf_dir)
    if not pdf_files:
        return {"status": "no_documents", "count": 0}

    all_documents = []
    category_counts = {"diet": 0, "workout": 0, "general": 0}

    for pdf_path in pdf_files:
        # Extract metadata from folder structure
        meta = _extract_metadata_from_path(str(pdf_path), pdf_dir)

        # Load the PDF
        loader = PyPDFLoader(str(pdf_path))
        docs = loader.load()

        # Enrich each page's metadata
        for doc in docs:
            doc.metadata.update(meta)
            # Prepend context to the chunk so embeddings capture the metadata
            context_prefix = f"[Category: {meta['category']}]"
            if "subcategory" in meta:
                context_prefix += f" [Plan: {meta['subcategory']}]"
            if "calories" in meta:
                context_prefix += f" [Calories: {meta['calories']}]"
            doc.page_content = f"{context_prefix}\n{doc.page_content}"

        all_documents.extend(docs)
        category_counts[meta["category"]] = category_counts.get(meta["category"], 0) + 1

    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = text_splitter.split_documents(all_documents)

    # Store in vector DB
    vector_store = get_vector_store()
    vector_store.add_documents(chunks)

    return {
        "status": "success",
        "pdf_files_found": len(pdf_files),
        "pages_loaded": len(all_documents),
        "chunks_created": len(chunks),
        "breakdown": category_counts,
    }


def ingest_single_pdf(file_path: str, category: str = "general", subcategory: str | None = None) -> dict:
    """Ingest a single PDF file with optional metadata."""
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    for doc in documents:
        doc.metadata["category"] = category
        doc.metadata["filename"] = Path(file_path).name
        if subcategory:
            doc.metadata["subcategory"] = subcategory
        context_prefix = f"[Category: {category}]"
        if subcategory:
            context_prefix += f" [Plan: {subcategory}]"
        doc.page_content = f"{context_prefix}\n{doc.page_content}"

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    chunks = text_splitter.split_documents(documents)

    vector_store = get_vector_store()
    vector_store.add_documents(chunks)

    return {"status": "success", "chunks_created": len(chunks)}
