# app/main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.api import endpoints
from app.config import get_logger

# Initialize logging
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI()

# Include routes
app.include_router(endpoints.router)
app.include_router(endpoints.dev_router, prefix="/dev", tags=["Development"])


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "An internal server error occurred."},
    )
