from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

load_dotenv()

from src.agent.graph import build_graph  # noqa: E402 — after load_dotenv
from src.api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Build the graph once at startup; shared across all requests
    app.state.graph = build_graph()
    yield
    # Nothing to clean up for MemorySaver


app = FastAPI(
    title="Yelnar's Assistant",
    description="AI research agent with web search and multimodal support.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
