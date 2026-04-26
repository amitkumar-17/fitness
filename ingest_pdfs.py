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
        print("\n   Expected structure:")
        print("   data/pdfs/")
        print("   ├── DietPlans/")
        print("   │   ├── 3300 calories diet/")
        print("   │   │   └── plan.pdf")
        print("   │   └── 2500 calories diet/")
        print("   │       └── plan.pdf")
        print("   └── WorkoutPlans/")
        print("       ├── Push Pull Legs/")
        print("       │   └── routine.pdf")
        print("       └── ...")

    print("\n⏳ Processing...")

    result = ingest_pdfs(pdf_dir)

    if result["status"] == "no_documents":
        print("\n⚠️  No PDF files found!")
        print("   Place your PDF files in the folder structure above.")
    else:
        print(f"\n✅ Ingestion complete!")
        print(f"   PDF files found:  {result['pdf_files_found']}")
        print(f"   Pages loaded:     {result['pages_loaded']}")
        print(f"   Chunks created:   {result['chunks_created']}")
        print(f"\n   Breakdown by category:")
        for cat, count in result['breakdown'].items():
            if count > 0:
                print(f"     {cat}: {count} PDF files")
        print(f"\n   Your AI is now trained on your fitness documents!")

    print("=" * 60)


if __name__ == "__main__":
    main()
