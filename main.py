from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import ingest, extract

app = FastAPI(
    title="GraphRAG-ATS - Module 1: Document Ingestion",
    description="API for ingesting resumes and performing blind ranking via PII extraction.",
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

@app.get("/", tags=["Health"])
async def root():
    """
    Basic health check endpoint.
    """
    return {"message": "Welcome to GraphRAG-ATS Ingestion API. Go to /docs to test the endpoints."}
