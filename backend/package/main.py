from dotenv import load_dotenv; load_dotenv()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router as submissions_router
from mangum import Mangum
import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from .database import Base, engine, SQLALCHEMY_DATABASE_URL
from .models import Submission  # Import all models to register them with Base
import time
from starlette.responses import Response
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from .deps import limiter

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(submissions_router)

# Create all tables at startup
Base.metadata.create_all(bind=engine)

print(f"[Startup] Using database URL: {SQLALCHEMY_DATABASE_URL}")

logger = logging.getLogger("app")

# Rate Limiter
app.state.limiter = limiter

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url} from {request.client.host}")
    start_time = time.time()
    try:
        body = await request.body()
        logger.info(f"Request body: {body.decode('utf-8')}")
    except Exception:
        logger.info("Could not read request body.")

    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    logger.info(f"Response status: {response.status_code} ({process_time:.2f} ms)")

    # Log response body for errors
    if response.status_code >= 400:
        resp_body = b""
        async for chunk in response.body_iterator:
            resp_body += chunk
        logger.error(f"Response body: {resp_body.decode('utf-8')}")
        # Rebuild the response for downstream
        response = Response(content=resp_body, status_code=response.status_code, headers=dict(response.headers), media_type=response.media_type)

    return response

@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=()"
    return response

# Uncomment to enforce HTTPS in production
# app.add_middleware(HTTPSRedirectMiddleware)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body},
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(Exception)
async def internal_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again later."},
    )

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

handler = Mangum(app) 