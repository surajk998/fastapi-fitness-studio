import logging

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from fastapi import APIRouter, Depends, Query, Response, status

from ..database import (
    course_table,
    course_user_table,
    database,
    get_db_session,
    user_table,
)
from ..models.classes import CourseInstructor, CourseUser
from .errors import SlotLimitExceedException

router = APIRouter()
logger: logging.Logger = logging.getLogger(__name__)


@router.get("/classes", response_model=Page[CourseInstructor], tags=["classes"])
async def get_all_courses_with_instructor(
    course_id: int = Query(None, description="course id to be filtered"),
    session=Depends(get_db_session),
):
    query = (
        select(
            course_user_table.c.id,
            course_user_table.c.user_id,
            course_user_table.c.course_id,
            (course_table.c.slot - course_user_table.c.booked_slot).label(
                "available_slot"
            ),
            (user_table.c.first_name + " " + user_table.c.last_name).label(
                "instructor_name"
            ),
            course_table.c.name.label("course_name"),
            course_table.c.description.label("course_description"),
            course_table.c.timing.label("course_timing"),
        )
        .join(user_table, onclause=(course_user_table.c.user_id == user_table.c.id))
        .join(
            course_table, onclause=(course_user_table.c.course_id == course_table.c.id)
        )
        .where(user_table.c.instructor == True)
        .order_by(course_user_table.c.id)
    )

    if course_id:
        query.where(course_user_table.c.course_id == course_id)

    return paginate(conn=session, query=query.group_by(course_user_table.c.course_id))


@router.get("/bookings", response_model=Page[CourseUser], tags=["bookings"])
async def get_all_courses_with_users(
    course_id: int = Query(None, description="course id to be filtered"),
    user_email: int = Query(None, description="user email id to be filtered"),
    session=Depends(get_db_session),
):
    query = (
        select(
            course_user_table.c.id,
            course_user_table.c.user_id,
            course_user_table.c.course_id,
            (course_table.c.slot - course_user_table.c.booked_slot).label(
                "available_slot"
            ),
            (user_table.c.first_name + " " + user_table.c.last_name).label("user_name"),
            course_table.c.name.label("course_name"),
            course_table.c.description.label("course_description"),
            course_table.c.timing.label("course_timing"),
        )
        .join(user_table, onclause=(course_user_table.c.user_id == user_table.c.id))
        .join(
            course_table, onclause=(course_user_table.c.course_id == course_table.c.id)
        )
        .where(user_table.c.instructor == False)
        .order_by(course_user_table.c.id)
    )

    if user_email:
        query.where(user_table.c.email == user_email)

    if course_id:
        query.where(course_user_table.c.course_id == course_id)

    return paginate(conn=session, query=query.group_by(course_user_table.c.course_id))


@router.post("/book", response_model=CourseUser, tags=["bookings"])
async def add_course(
    course_id: int = Query(None, description="course id"),
    user_id: int = Query(None, description="user id"),
):
    logger.info(f"{course_id = }\n{user_id = }")

    query = course_table.select().where(course_table.c.id == course_id)
    course = await database.fetch_one(query)
    if not course:
        raise ValueError(f"{course_id = } is invalid.")

    query = user_table.select().where(user_table.c.id == user_id)
    user = await database.fetch_one(query)
    if not user:
        raise ValueError(f"{user_id = } is invalid.")

    query = course_user_table.insert().values(course_id=course.id, user_id=user_id)

    course_user_obj = await database.execute(query)
    if course_user_obj.booked_slot >= course.slot:
        raise SlotLimitExceedException(
            f"No available slots for {course.name} at {course.timing}"
        )
    query = (
        course_user_table.update()
        .where(course_user_table.c.id == course_user_obj.id)
        .values(booked_slot=course_user_obj.booked_slot + 1)
    )
    await database.execute(query)

    return Response(
        content=f"{course_user_obj = } slot booked", status_code=status.HTTP_201_CREATED
    )


@router.put("/book", response_model=CourseUser, tags=["bookings"])
async def remove_course(
    course_id: int = Query(None, description="course id"),
    user_id: int = Query(None, description="user id"),
):
    logger.info(f"{course_id = }\n{user_id = }")

    query = course_table.select().where(course_table.c.id == course_id)
    course = await database.fetch_one(query)
    if not course:
        raise ValueError(f"{course_id = } is invalid.")

    query = user_table.select().where(user_table.c.id == user_id)
    user = await database.fetch_one(query)
    if not user:
        raise ValueError(f"{user_id = } is invalid.")

    query = course_user_table.select().where(
        course_user_table.c.course_id == course.id,
        course_user_table.c.user_id == user_id,
    )
    course_user_obj = await database.execute(query)
    if course_user_obj.booked_slot == 0:
        query = course_user_table.delete().where(
            course_user_table.c.id == course_user_obj.id
        )
    else:
        query = (
            course_user_table.update()
            .where(course_user_table.c.id == course_user_obj.id)
            .values(booked_slot=course_user_obj.booked_slot - 1)
        )

    await database.execute(query)
    return Response(
        content=f"{course_user_obj = } slot removed", status_code=status.HTTP_200_OK
    )
