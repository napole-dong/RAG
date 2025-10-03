import pydantic


class RAGChunkAndSrc(pydantic.BaseModel):
    chunk: list[str]
    source_id: str = None

class RAGUpserResult(pydantic.BaseModel):
    inngest: int

class RAGSerchResult(pydantic.BaseModel):
    sources: list[str]
    contexts: list[str]

class RAGQueryResult(pydantic.BaseModel):
    answer: str
    sources: list[str]
    num_contexts: int