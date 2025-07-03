import os
import logging
from fastapi import FastAPI, Request
from mangum import Mangum

app = FastAPI(
    title="Form Management API",
    description="API for managing form submissions",
    version="1.0.0",
    root_path=os.getenv("API_GATEWAY_STAGE", "")
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

handler = Mangum(app, lifespan="off") 