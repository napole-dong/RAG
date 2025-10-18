import logging

from wsgiref.simple_server import server_version
import inngest
from fastapi import FastAPI
import inngest.fast_api
from dotenv import load_dotenv
import uuid
import os
import datetime
from dotenv import load_dotenv
from data_loader import load_and_chunk_pdf, embed_texts
from vecto_db import QdrantStorage
from custom_types import RAGQueryResult,RAGSerchResult,RAGUpserResult,RAGChunkAndSrc

load_dotenv()


inngest_clinet= inngest.Inngest(
    app_id="rag_app",
    logger=logging.getLogger("uvicorn"),
    is_production=False,
    serializer=inngest.PydanticSerializer()
)

@inngest_clinet.create_function(
    fn_id="RAG: Ingest PDF",
    trigger=inngest.TriggerEvent(event="rag/ingest_pdf")
)
async def rag_ingest_pdf(ctx: inngest.Context):
    def _load(ctx: inngest.Context) -> RAGChunkAndSrc:
        pdf_path = ctx.event.data["pdf_path"]
        source_id =ctx.event.data.get("source_id", pdf_path)
        chunks = load_and_chunk_pdf(pdf_path)
        return RAGChunkAndSrc(chunk=chunks, source_id=source_id)

    def _upsert(chunks_and_src: RAGChunkAndSrc) -> RAGUpserResult:
        chunks = chunks_and_src.chunks
        source_id = chunks_and_src.source_id
        vecs = embed_texts(chunks)
        ids = [str(uuid.uuid5(uuid.NAMESPACE_URL, f"{source_id}:{i}")) for i in range(len(chunks))]
        payloads = [{"source": source_id, "text": chunks[i]} for i in range (len(chunks))]
        QdrantStorage().upsert(ids, vecs, payloads)
        return RAGUpserResult(inngest=len(chunks))



    chunks_and_src = await ctx.step.run("load-and-chunk",lambda: _load(ctx), output_type=RAGChunkAndSrc)
    inngested = await ctx.step.run("load-and-chunk",lambda: _upsert(chunks_and_src), output_type=RAGUpserResult)
    return inngested.model.dump()


from fastapi import BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Optional


class IngestRequest(BaseModel):
    pdf_path: str
    source_id: Optional[str] = None


app = FastAPI()
inngest.fast_api.serve(app, inngest_clinet, [rag_ingest_pdf])


def _do_ingest(pdf_path: str, source_id: Optional[str] = None):
    # ensure path is inside /app when running in container
    if not pdf_path.startswith("/"):
        pdf_path = os.path.join(os.getcwd(), pdf_path)
    # load, chunk, embed, upsert
    chunks = load_and_chunk_pdf(pdf_path)
    vecs = embed_texts(chunks)
    ids = [str(uuid.uuid5(uuid.NAMESPACE_URL, f"{source_id or pdf_path}:{i}")) for i in range(len(chunks))]
    payloads = [{"source": source_id or pdf_path, "text": chunks[i]} for i in range(len(chunks))]
    QdrantStorage().upsert(ids, vecs, payloads)
    return {"chunks": len(chunks), "vectors": len(vecs)}


@app.post('/ingest')
def ingest_pdf(req: IngestRequest, background_tasks: BackgroundTasks):
    # validate file exists
    path = req.pdf_path
    if not path.startswith('/'):
        path = os.path.join(os.getcwd(), path)
    if not os.path.isfile(path):
        raise HTTPException(status_code=400, detail=f"PDF not found: {req.pdf_path}")

    # Run in background to avoid blocking client for long jobs
    background_tasks.add_task(_do_ingest, path, req.source_id)
    return {"status": "started", "pdf_path": req.pdf_path, "source_id": req.source_id}


class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5


@app.post('/query')
def query_pdf(req: QueryRequest):
    # embed the query
    qvecs = embed_texts([req.query])
    if not qvecs:
        raise HTTPException(status_code=400, detail="Failed to embed query")
    qvec = qvecs[0]
    # search qdrant
    results = QdrantStorage().search(qvec, top_k=req.top_k)
    return {"query": req.query, "top_k": req.top_k, "results": results}
