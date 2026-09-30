import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .cache import backend_name
from .config import settings
from .routers import auth, reports, routes, sos

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("accessinav")

app = FastAPI(title="AccessiNav API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        # Handled here (not by exception_handler) so CORS headers still apply.
        log.exception("Unhandled error on %s %s", request.method, request.url.path)
        response = JSONResponse({"error": "Internal server error"}, status_code=500)
    ms = (time.perf_counter() - start) * 1000
    log.info("%s %s -> %s (%.0fms)", request.method, request.url.path, response.status_code, ms)
    return response


app.include_router(auth.router)
app.include_router(reports.router)
app.include_router(routes.router)
app.include_router(sos.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "cache": backend_name()}
