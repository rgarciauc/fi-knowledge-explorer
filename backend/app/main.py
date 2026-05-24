from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .db import close_driver, verify_connectivity
from .routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    verify_connectivity()
    yield
    close_driver()


app = FastAPI(title="SUPER_BANK Knowledge Graph API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.get("/health")
def health() -> dict[str, str]:
    try:
        verify_connectivity()
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Neo4j is unavailable") from exc
    return {"status": "ok", "neo4j": "available"}
