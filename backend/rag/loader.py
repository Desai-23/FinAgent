import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import chromadb
from chromadb.utils import embedding_functions
from rag.knowledge_base import FINANCE_KNOWLEDGE

# Path to uploads folder and ChromaDB storage
UPLOADS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
CHROMA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chroma_db")

# Use sentence transformers for embeddings — runs locally, no API key needed
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

# Initialize ChromaDB client
chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)

# Get or create the collection
collection = chroma_client.get_or_create_collection(
    name="finagent_knowledge",
    embedding_function=embedding_fn,
    metadata={"hnsw:space": "cosine"}
)


def load_knowledge_base():
    """Load the built-in finance concepts into ChromaDB if not already loaded."""
    existing = collection.get(ids=[item["id"] for item in FINANCE_KNOWLEDGE])
    already_loaded = len(existing["ids"])

    if already_loaded == len(FINANCE_KNOWLEDGE):
        print(f"[RAG] Knowledge base already loaded ({already_loaded} concepts)")
        return

    print(f"[RAG] Loading {len(FINANCE_KNOWLEDGE)} finance concepts into ChromaDB...")

    collection.upsert(
        ids=[item["id"] for item in FINANCE_KNOWLEDGE],
        documents=[item["text"] for item in FINANCE_KNOWLEDGE],
        metadatas=[item["metadata"] for item in FINANCE_KNOWLEDGE],
    )
    print("[RAG] Knowledge base loaded successfully!")


def load_pdf(filepath: str) -> list[str]:
    """Extract text chunks from a PDF file."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(filepath)
        chunks = []
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if text and text.strip():
                # Split into smaller chunks of ~500 chars with overlap
                words = text.split()
                chunk_size = 100  # words per chunk
                overlap = 20
                for i in range(0, len(words), chunk_size - overlap):
                    chunk = " ".join(words[i:i + chunk_size])
                    if len(chunk.strip()) > 50:
                        chunks.append({
                            "text": chunk,
                            "page": page_num + 1,
                        })
        return chunks
    except Exception as e:
        print(f"[RAG] Error reading PDF {filepath}: {e}")
        return []


def load_pdf_into_chroma(filepath: str, filename: str):
    """Load a PDF file into ChromaDB."""
    chunks = load_pdf(filepath)
    if not chunks:
        return 0

    ids = [f"pdf_{filename}_p{c['page']}_c{i}" for i, c in enumerate(chunks)]
    documents = [c["text"] for c in chunks]
    metadatas = [{"source": filename, "page": c["page"], "topic": "uploaded_pdf"} for c in chunks]

    collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
    print(f"[RAG] Loaded {len(chunks)} chunks from {filename}")
    return len(chunks)


def load_html_into_chroma(filepath: str, filename: str):
    """Load an HTML file (like SEC filings) into ChromaDB."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Basic HTML tag stripping
        import re
        text = re.sub(r'<[^>]+>', ' ', content)
        text = re.sub(r'\s+', ' ', text).strip()

        if len(text) < 100:
            return 0

        # Chunk into ~500 word pieces
        words = text.split()
        chunks = []
        chunk_size = 100
        overlap = 20
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            if len(chunk.strip()) > 50:
                chunks.append(chunk)

        if not chunks:
            return 0

        ids = [f"html_{filename}_c{i}" for i in range(len(chunks))]
        documents = chunks
        metadatas = [{"source": filename, "page": 0, "topic": "sec_filing"} for _ in chunks]

        collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
        print(f"[RAG] Loaded {len(chunks)} chunks from {filename}")
        return len(chunks)

    except Exception as e:
        print(f"[RAG] Error reading HTML {filepath}: {e}")
        return 0


def load_all_pdfs():
    """Scan uploads folder and load any PDFs or HTML files found."""
    if not os.path.exists(UPLOADS_DIR):
        os.makedirs(UPLOADS_DIR)
        return

    for filename in os.listdir(UPLOADS_DIR):
        filepath = os.path.join(UPLOADS_DIR, filename)
        if filename.endswith(".pdf"):
            load_pdf_into_chroma(filepath, filename)
        elif filename.endswith(".html") or filename.endswith(".htm"):
            load_html_into_chroma(filepath, filename)


def initialize_rag():
    """Initialize everything — call this once on startup."""
    load_knowledge_base()
    load_all_pdfs()
    print(f"[RAG] Total documents in collection: {collection.count()}")

