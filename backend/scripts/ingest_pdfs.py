"""
CLI script to ingest PDF files into the app knowledge base.

Usage:
    python -m scripts.ingest_pdfs
    python -m scripts.ingest_pdfs ./my_pdfs
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ai.ingestion import ingest_pdfs


def main():
    pdf_dir = sys.argv[1] if len(sys.argv) > 1 else None

    print("=" * 60)
    print("  Fitness AI - PDF Ingestion Pipeline")
    print("=" * 60)

    if pdf_dir:
        print(f"\nIngesting PDFs from: {pdf_dir}")
    else:
        print("\nIngesting PDFs from default directory: ./data/pdfs/")
        print("\nExpected structure:")
        print("  data/pdfs/")
        print("    DietPlans/")
        print("      3300 calories diet/")
        print("        plan.pdf")
        print("      2500 calories diet/")
        print("        plan.pdf")
        print("    WorkoutPlans/")
        print("      Push Pull Legs/")
        print("        routine.pdf")
        print("      ...")

    print("\nProcessing...")
    result = ingest_pdfs(pdf_dir)

    if result["status"] == "no_documents":
        print("\nNo PDF files found.")
        print("Place your PDF files in the folder structure above.")
    else:
        print("\nIngestion complete.")
        print(f"PDF files found: {result['pdf_files_found']}")
        print(f"Pages loaded:    {result['pages_loaded']}")
        print(f"Chunks created:  {result['chunks_created']}")
        if result.get("index_type"):
            print(f"Index type:      {result['index_type']}")

        print("\nBreakdown by category:")
        for category, count in result["breakdown"].items():
            if count > 0:
                print(f"  {category}: {count} PDF files")

        print("\nYour AI can now use your fitness documents.")

    print("=" * 60)


if __name__ == "__main__":
    main()
