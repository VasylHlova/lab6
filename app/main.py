from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import time

from app.utils.logger import setup_logging
from app.db.database import create_db_and_tables
from app.api import books, authors

logger = setup_logging()


# Define the lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting database initialization")
    # Run the synchronous function - FastAPI will handle this correctly in lifespan
    create_db_and_tables()
    logger.info("Database initialization completed")
    logger.info("Application Started")

    # Yield control back to FastAPI to handle requests
    yield

    # Shutdown logic
    logger.info("Application Shutdown")


# Create the FastAPI app with the lifespan handler
app = FastAPI(
    title="Library Management System API",
    description="API for managing a library system with books, authors etc.",
    version="0.0.1",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(
        f"Path: {request.url.path} | "
        f"Method: {request.method} | "
        f"Status: {response.status_code} | "
        f"Duration: {process_time:.4f}s"
    )
    return response


# Include routers
app.include_router(books.router, prefix="/api/books", tags=["books"])
app.include_router(authors.router, prefix="/api/authors", tags=["authors"])


@app.get("/")
def root():
    return {"message": "Welcome to Library Management System API"}