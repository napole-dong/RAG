# data_loader.py
from __future__ import annotations

import os
from typing import List

from dotenv import load_dotenv

# Gemini (generate)
import google.generativeai as genai

# Embedding local (không phụ thuộc OpenAI)
from sentence_transformers import SentenceTransformer

# PDF & chunking
from llama_index.readers.file import PDFReader
from llama_index.core.node_parser import SentenceSplitter
from llama_index.readers.file import PyMuPDFReader  # thêm dòng này

load_dotenv()

# ---------- Gemini setup (generate) ----------
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
_gemini = genai.GenerativeModel("gemini-1.5-flash")  # hoặc "gemini-1.5-pro"

# ---------- Embedding model (local) ----------
# Bạn có thể đổi sang model khác nếu muốn dim lớn hơn
_embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
# Lưu ý: model này cho vector ~384 chiều, đã đủ tốt cho demo/đồ án

# ---------- Chunker ----------
splitter = SentenceSplitter(chunk_size=1000, chunk_overlap=200)


def load_and_chunk_pdf(path: str) -> List[str]:
    """
    Đọc PDF và cắt thành các đoạn (chunks) dùng SentenceSplitter.
    Ưu tiên pypdf; nếu file 'méo' thì fallback sang PyMuPDF (fitz).
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"PDF not found: {path}")

    docs = None

    # 1) Thử với PDFReader (pypdf)
    try:
        try:
            docs = PDFReader().load_data(path)          # một số phiên bản nhận path
        except TypeError:
            docs = PDFReader().load_data(file=path)     # số khác nhận file=...
    except Exception:
        # 2) Fallback sang PyMuPDFReader (bền hơn với PDF lỗi)
        try:
            try:
                docs = PyMuPDFReader().load_data(path)
            except TypeError:
                docs = PyMuPDFReader().load_data(file=path)
        except Exception:
            # 3) Fallback cuối cùng: dùng fitz trực tiếp (PyMuPDF thô)
            import fitz  # pymupdf
            text_parts = []
            with fitz.open(path) as pdf:
                for page in pdf:
                    text_parts.append(page.get_text())
            full_text = "\n".join(text_parts)
            # giả lập Document tối thiểu
            from llama_index.core import Document
            docs = [Document(text=full_text)]

    texts = [getattr(d, "text", "") for d in docs if getattr(d, "text", None)]
    chunks: List[str] = []
    for t in texts:
        chunks.extend(splitter.split_texts(t))
    return chunks


def embed_texts(texts: List[str], batch_size: int = 32) -> List[List[float]]:
    """Encode a list of texts into embedding vectors (lists of floats).

    Uses the module-level `_embedder` (SentenceTransformer). Returns a list
    where each element is a plain Python list of floats suitable for upsert to Qdrant.
    """
    if not texts:
        return []

    vectors = []
    # Batch to avoid OOM on large inputs
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        emb = _embedder.encode(batch, show_progress_bar=False)
        # sentence-transformers may return numpy arrays; convert to lists
        try:
            for v in emb.tolist():
                vectors.append(v)
        except Exception:
            # fallback if emb is already a list of lists
            vectors.extend(list(emb))

    return vectors
