from data_loader import load_and_chunk_pdf, embed_texts
from vecto_db import QdrantStorage
import uuid

pdf_path = '/app/sample.pdf'
chunks = load_and_chunk_pdf(pdf_path)
print('chunks count:', len(chunks))
vecs = embed_texts(chunks)
print('vecs count:', len(vecs), 'dim:', len(vecs[0]) if vecs else 0)
ids = [str(uuid.uuid5(uuid.NAMESPACE_URL, f"sample.pdf:{i}")) for i in range(len(chunks))]
payloads = [{'source':'sample.pdf','text':chunks[i]} for i in range(len(chunks))]
QdrantStorage().upsert(ids, vecs, payloads)
print('upsert done')
