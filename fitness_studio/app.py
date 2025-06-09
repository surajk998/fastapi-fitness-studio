import logging
from contextlib import asynccontextmanager

from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import Response
from fastapi_pagination import add_pagination

from fastapi import FastAPI, HTTPException, status

from .database import database
from .logger_config import configure_logging
from .routers.classes import router as classes_router
from .routers.course import router as course_router
from .routers.errors import SlotLimitExceedException
from .routers.user import router as user_router

logger: logging.Logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    await database.connect()
    yield
    await database.disconnect()


openapi_tags: list[dict[str, str]] = [
    {"name": "bookings", "description": "apis related to booking slots"},
    {"name": "classes", "description": "apis related to available fitness classes"},
    {"name": "courses", "description": "apis related to available fitness courses"},
    {"name": "users", "description": "apis related to user"},
]


app = FastAPI(version="1.0.0", lifespan=lifespan, openapi_tags=openapi_tags)


@app.get("/health", include_in_schema=False)
def health_check() -> Response:
    return Response(content="Status is live", status_code=status.HTTP_200_OK)


@app.exception_handler(HTTPException)
async def http_exceptions(request, exc) -> Response:
    logger.error(f"HTTPException: {exc.status_code} - {exc.detail}", exc_info=True)
    return await http_exception_handler(request, exc)


@app.exception_handler(ValueError)
async def value_error_exception(request, exc) -> Response:
    logger.error(f"ValueError:- {str(exc)}", exc_info=True)
    exc.detail = "Bad Request"
    exc.status_code = 400
    return await http_exception_handler(request, exc)


@app.exception_handler(SlotLimitExceedException)
async def slot_limit_exceed_exception(request, exc) -> Response:
    logger.error(f"SlotLimitExceedException:- {str(exc)}", exc_info=True)
    exc.detail = "Expection Failed - Slot Unavailable"
    exc.status_code = 417
    return await http_exception_handler(request, exc)


app.include_router(user_router)
app.include_router(course_router)
app.include_router(classes_router)

add_pagination(app)
