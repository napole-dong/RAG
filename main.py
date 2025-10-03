import logging
from wsgiref.simple_server import server_version

from fastapi import FastAPI
import inngest.fast_api
from dotenv import load_dotenv
import uuid
import os
import datetime
from dotenv import load_dotenv

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
    return {"hello": "world"}
app =FastAPI()

inngest.fast_api.serve(app, inngest_clinet, [rag_ingest_pdf])