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
import json
from pathlib import Path
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from app.core.config import settings


def get_embeddings():
    if not settings.EMBEDDING_MODEL:
        raise RuntimeError("Embeddings are disabled because EMBEDDING_MODEL is not configured.")

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


def get_local_index_path() -> Path:
    """Local keyword-search index used when embeddings are disabled."""
    return Path(settings.CHROMA_PERSIST_DIR).parent / "pdf_knowledge_index.json"


def _split_documents(documents: list[Document]) -> list[Document]:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return text_splitter.split_documents(documents)


def _document_to_record(doc: Document) -> dict:
    return {
        "page_content": doc.page_content,
        "metadata": doc.metadata,
    }


def _record_to_document(record: dict) -> Document:
    return Document(
        page_content=record.get("page_content", ""),
        metadata=record.get("metadata", {}),
    )


def _load_local_index() -> list[dict]:
    path = get_local_index_path()
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("documents", [])


def _save_local_index(records: list[dict]) -> None:
    path = get_local_index_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump({"documents": records}, f, ensure_ascii=False)


def _tokenize(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-zA-Z0-9]{3,}", text.lower())
        if token not in {"the", "and", "for", "with", "this", "that", "from", "your"}
    }


def _score_document(query_terms: set[str], doc: Document) -> int:
    metadata_text = " ".join(str(value) for value in doc.metadata.values())
    metadata_terms = _tokenize(metadata_text)
    content_terms = _tokenize(doc.page_content)
    metadata_score = len(query_terms & metadata_terms) * 3
    content_score = len(query_terms & content_terms)
    return metadata_score + content_score


def search_local_knowledge(query: str, k: int = 6) -> list[Document]:
    """Search extracted PDF chunks without embeddings."""
    query_terms = _tokenize(query)
    if not query_terms:
        return []

    scored_docs = []
    for record in _load_local_index():
        doc = _record_to_document(record)
        score = _score_document(query_terms, doc)
        if score > 0:
            scored_docs.append((score, doc))

    scored_docs.sort(key=lambda item: item[0], reverse=True)

    selected: list[Document] = []
    seen_sources: set[str] = set()
    for _, doc in scored_docs:
        source_key = str(doc.metadata.get("source") or doc.metadata.get("filename") or "")
        if source_key in seen_sources:
            continue
        seen_sources.add(source_key)
        selected.append(doc)
        if len(selected) >= k:
            break

    if len(selected) < k:
        for _, doc in scored_docs:
            if doc in selected:
                continue
            selected.append(doc)
            if len(selected) >= k:
                break

    return selected


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

    chunks = _split_documents(all_documents)

    if not settings.EMBEDDING_MODEL:
        _save_local_index([_document_to_record(chunk) for chunk in chunks])
        return {
            "status": "success",
            "index_type": "local_keyword",
            "pdf_files_found": len(pdf_files),
            "pages_loaded": len(all_documents),
            "chunks_created": len(chunks),
            "breakdown": category_counts,
        }

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

    chunks = _split_documents(documents)

    if not settings.EMBEDDING_MODEL:
        records = _load_local_index()
        source = str(Path(file_path))
        records = [
            record
            for record in records
            if record.get("metadata", {}).get("source") != source
        ]
        records.extend(_document_to_record(chunk) for chunk in chunks)
        _save_local_index(records)
        return {
            "status": "success",
            "index_type": "local_keyword",
            "chunks_created": len(chunks),
        }

    vector_store = get_vector_store()
    vector_store.add_documents(chunks)

    return {"status": "success", "chunks_created": len(chunks)}
