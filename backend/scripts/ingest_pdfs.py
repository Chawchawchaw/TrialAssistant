#!/usr/bin/env python3
"""Script to ingest PDF documents into the Milvus knowledge base.

Usage:
    python scripts/ingest_pdfs.py /path/to/pdf/folder
"""

import logging
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)-30s | %(levelname)-6s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/ingest_pdfs.py <pdf_directory>")
        print("Example: python scripts/ingest_pdfs.py /Volumes/ExFAT/RAG测试/国军标/GJB\\ 150-2009")
        sys.exit(1)

    pdf_dir = sys.argv[1]

    if not os.path.isdir(pdf_dir):
        print(f"Error: Directory not found: {pdf_dir}")
        sys.exit(1)

    from app.services.document_loader import load_pdfs_from_directory
    from app.services.rag_service import drop_and_rebuild_collection

    print(f"\n{'='*60}")
    print(f"📄 加载PDF文档: {pdf_dir}")
    print(f"{'='*60}")

    documents = load_pdfs_from_directory(pdf_dir)

    if not documents:
        print("❌ 未加载到任何文档，退出。")
        sys.exit(1)

    print(f"\n✅ 加载了 {len(documents)} 篇文档")

    print(f"\n{'='*60}")
    print(f"🔧 重建知识库并导入到 Milvus...")
    print(f"{'='*60}")

    result = drop_and_rebuild_collection(documents)

    if result.get("status") == "success":
        print(f"\n✅ 知识库初始化成功！")
        print(f"   文档数: {result.get('documents', 0)}")
        print(f"   分块数: {result.get('chunks_count', 0)}")
        print(f"\n{'='*60}")
        print(f"🚀 知识库已就绪，可以启动服务了！")
        print(f"{'='*60}")
    else:
        print(f"\n❌ 知识库初始化失败: {result.get('error', '未知错误')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
