"""PDF document loader and text extractor for RAG ingestion.

Handles reading PDF files, extracting text, and structuring them
as documents ready for embedding and indexing.
"""

import logging
import os
import re
from typing import Any, List

logger = logging.getLogger(__name__)


def extract_pdf_text(pdf_path: str) -> str | None:
    """Extract text content from a PDF file.

    Args:
        pdf_path: Absolute path to the PDF file.

    Returns:
        Extracted text content, or None if extraction fails.
    """
    try:
        import fitz  # PyMuPDF
    except ImportError:
        logger.error("PyMuPDF not installed. Run: uv pip install pymupdf")
        return None

    # Open file as bytes to avoid filesystem issues with external volumes
    try:
        with open(pdf_path, "rb") as fh:
            file_bytes = fh.read()
    except Exception as e:
        logger.error(f"Failed to read file {pdf_path}: {e}")
        return None

    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text_parts = []
        num_pages = len(doc)

        for page_num in range(num_pages):
            page = doc.load_page(page_num)
            text = page.get_text()
            if text.strip():
                text_parts.append(text.strip())

        doc.close()
        full_text = "\n\n".join(text_parts)

        logger.info(f"Extracted {len(full_text)} chars from {os.path.basename(pdf_path)} ({num_pages} pages)")
        return full_text

    except Exception as e:
        logger.error(f"Failed to extract text from {pdf_path}: {e}")
        return None


def extract_pdf_metadata(file_path: str) -> dict[str, Any]:
    """Extract metadata from a PDF filename and path.

    Args:
        file_path: Absolute path to the PDF file.

    Returns:
        Metadata dict with title, category, tags.
    """
    filename = os.path.basename(file_path)
    name_without_ext = os.path.splitext(filename)[0]

    # Extract standard number (e.g., GJB 150.3A-2009)
    standard_match = re.match(r'(GJB\s+[\d.]+[A-Z]?(?:-\d{4})?)', name_without_ext)
    standard_no = standard_match.group(1) if standard_match else name_without_ext

    # Determine category from parent folder
    parent_dir = os.path.basename(os.path.dirname(file_path))
    category = parent_dir.replace("国军标", "国军标").replace("GJB", "").strip() or "国军标"

    # Generate tags
    tags = ["国军标", "GJB"]
    if standard_no:
        tags.append(standard_no)

    # Extract topic from filename after standard number
    topic_match = re.search(r'[：:]\s*(.+?)(?:\.pdf)?$', name_without_ext)
    if topic_match:
        tags.append(topic_match.group(1).strip())

    return {
        "standard_no": standard_no,
        "category": category,
        "tags": tags,
        "filename": filename,
        "source_path": file_path,
    }


def load_pdfs_from_directory(dir_path: str) -> List[dict[str, Any]]:
    """Load all PDFs from a directory and extract their content.

    Args:
        dir_path: Directory containing PDF files.

    Returns:
        List of document dicts with id, title, category, tags, content.
    """
    logger.info(f"Loading PDFs from: {dir_path}")

    if not os.path.isdir(dir_path):
        logger.error(f"Directory not found: {dir_path}")
        return []

    documents = []
    doc_id_counter = 0

    # Collect PDF files
    pdf_files = []
    for f in os.listdir(dir_path):
        if f.endswith(".pdf") and not f.startswith("._"):
            pdf_files.append(os.path.join(dir_path, f))

    pdf_files.sort()
    logger.info(f"Found {len(pdf_files)} PDF files")

    for pdf_path in pdf_files:
        doc_id_counter += 1
        metadata = extract_pdf_metadata(pdf_path)
        content = extract_pdf_text(pdf_path)

        if not content:
            logger.warning(f"Skipping {pdf_path}: no text extracted")
            continue

        doc = {
            "id": f"gjb-{doc_id_counter:04d}",
            "title": metadata["standard_no"],
            "category": metadata["category"],
            "tags": metadata["tags"],
            "content": content,
            "filename": metadata["filename"],
        }
        documents.append(doc)

    logger.info(f"Loaded {len(documents)} documents from {dir_path}")
    return documents
