import logging

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

from fastapi import APIRouter, Depends, Request, Response, status

from ..database import (
    course_table,
    course_user_table,
    database,
    get_db_session,
    user_table,
)
from ..models.classes import CourseUser
from ..models.user import User, UserIn

router = APIRouter(prefix="/users", tags=["users"])
logger: logging.Logger = logging.getLogger(__name__)


@router.get("/", response_model=Page[User])
async def get_users(session=Depends(get_db_session)):
    query = user_table.select()

    return paginate(conn=session, query=query)


@router.get("/info/{user_id}", response_model=User)
async def get_user_info(user_id: int):
    query = user_table.select().where(user_table.c.id == user_id)

    return await database.fetch_one(query)


@router.delete("/remove/{user_id}", response_model=User)
async def remove_user(user_id: int):
    query = user_table.delete().where(user_table.c.id == user_id)

    return await database.execute(query)


@router.post("/register", response_model=UserIn)
async def register_user(user: UserIn):
    query = user_table.insert().values(
        {**user.model_dump(), **{"password": user.password.get_secret_value()}}
    )
    logger.info(f"{query = }")
    user_id = await database.execute(query)
    return Response(
        content=f"{user_id = } created", status_code=status.HTTP_201_CREATED
    )



@router.put("/{user_id}/update_info", response_model=User)
async def update_slot_count(user_id: int, request: Request):
    payload = await request.json()
    query = user_table.select().where(user_table.c.id == user_id)
    user_record = await database.fetch_one(query)
    if not user_record:
        raise ValueError(f"{user_id = } is invalid")

    query = user_table.update().where(user_table.c.id == user_id).values(**payload)
    await database.execute(query)

    return Response(content=f"updated info for {user_id = }")
