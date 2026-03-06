from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import ingest, extract, match, dispatch, analytics, bulk_process, admin

app = FastAPI(
    title="GraphRAG-ATS - Full Pipeline",
    description="API for context-aware resume matching with LLM feedback and automated email dispatch.",
    version="1.0.0"
)

# Optional: Disable CORS restrictions during local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest.router, prefix="/api/v1", tags=["document-ingestion"])
app.include_router(extract.router, prefix="/api/v1", tags=["entity-extraction"])
app.include_router(match.router, prefix="/api/v1", tags=["matching-engine"])
app.include_router(dispatch.router, prefix="/api/v1", tags=["recruitment-pipeline"])
app.include_router(analytics.router, prefix="/api/v1", tags=["analytics"])
app.include_router(bulk_process.router, prefix="/api/v1", tags=["bulk"])
app.include_router(admin.router, prefix="/api/v1", tags=["admin"])

@app.get("/", tags=["Health"])
async def root():
    """
    Basic health check endpoint.
    """
    return {"message": "Welcome to GraphRAG-ATS Ingestion API. Go to /docs to test the endpoints."}
