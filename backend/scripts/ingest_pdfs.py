"""
CLI Script to ingest your PDF files into the vector database.

Usage:
    python -m scripts.ingest_pdfs              # Ingest all PDFs from default folder
    python -m scripts.ingest_pdfs ./my_pdfs    # Ingest from a specific folder

Place your workout and diet PDF files in the `data/pdfs/` folder and run this script.
The script will:
1. Read all PDF files
2. Split them into searchable chunks
3. Store embeddings in ChromaDB

After running this, the AI will use your PDF content to generate personalized plans.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ai.ingestion import ingest_pdfs


def main():
    pdf_dir = sys.argv[1] if len(sys.argv) > 1 else None

    print("=" * 60)
    print("  Fitness AI - PDF Ingestion Pipeline")
    print("=" * 60)

    if pdf_dir:
        print(f"\n📁 Ingesting PDFs from: {pdf_dir}")
    else:
        print(f"\n📁 Ingesting PDFs from default directory: ./data/pdfs/")

    print("⏳ Processing...")

    result = ingest_pdfs(pdf_dir)

    if result["status"] == "no_documents":
        print("\n⚠️  No PDF files found!")
        print("   Place your workout/diet PDF files in the data/pdfs/ folder")
        print("   Supported: .pdf files")
    else:
        print(f"\n✅ Ingestion complete!")
        print(f"   Documents loaded: {result['documents_loaded']}")
        print(f"   Chunks created:   {result['chunks_created']}")
        print(f"\n   Your AI is now trained on your fitness documents!")

    print("=" * 60)


if __name__ == "__main__":
    main()
