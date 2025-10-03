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


app =FastAPI()
inngest.fast_api.serve(app, inngest_clinet, [rag_ingest_pdf])
