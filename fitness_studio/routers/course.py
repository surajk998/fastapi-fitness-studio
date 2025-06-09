import logging
from datetime import time

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

from fastapi import APIRouter, Depends, Response, status

from ..database import course_table, database, get_db_session
from ..models.course import Course

router = APIRouter(prefix="/courses", tags=["courses"])
logger: logging.Logger = logging.getLogger(__name__)


@router.get("/", response_model=Page[Course])
async def get_courses(session=Depends(get_db_session)):
    query = course_table.select()

    return paginate(conn=session, query=query)


@router.get("/info/{course_id}", response_model=Course)
async def get_course_info(course_id: int):
    query = course_table.select().where(course_table.c.id == course_id)
    course = await database.fetch_one(query)

    if not course:
        raise ValueError(f"{course_id = } is invalid")
    logger.info(f"{course = }")
    return course


@router.patch("/{course_id}/update_slot/{slot}", response_model=Course)
async def update_slot_count(course_id: int, slot: int):
    query = course_table.select().where(course_table.c.id == course_id)
    course = await database.fetch_one(query)
    if not course:
        raise ValueError(f"{course_id = } is invalid")

    query = (
        course_table.update().where(course_table.c.id == course_id).values(slot=slot)
    )
    await database.execute(query)

    return Response(content=f"updated slot for {course_id = }")


@router.patch("/{course_id}/update_timing/{timing}", response_model=Course)
async def update_course_timing(course_id: int, timing: time):
    query = course_table.select().where(course_table.c.id == course_id)
    course = await database.fetch_one(query)
    if not course:
        raise ValueError(f"{course_id = } is invalid")

    query = (
        course_table.update()
        .where(course_table.c.id == course_id)
        .values(timing=timing)
    )
    await database.execute(query)

    return Response(content=f"updated timing of {course_id = }")


@router.delete("/remove/{course_id}", response_model=Course)
async def remove_course(course_id: int):
    query = course_table.delete().where(course_table.c.id == course_id)

    return await database.execute(query)


@router.post("/register", response_model=Course)
async def register_course(course: Course):
    query = course_table.insert().values(**course.model_dump())
    logger.info(f"{query = }")
    course_id = await database.execute(query)
    return Response(
        content=f"{course_id = } created", status_code=status.HTTP_201_CREATED
    )
