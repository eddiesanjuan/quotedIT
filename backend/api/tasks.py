"""
Task API endpoints for Quoted CRM (DISC-092).
Handles task/reminder CRUD, listing, and management operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta

from ..services.auth import get_db, get_current_user
from ..models.database import Task, Customer, Quote, Contractor

router = APIRouter()


# Response/Request Models

class TaskBase(BaseModel):
    """Base task fields."""
    title: str
    description: Optional[str] = None
    priority: Optional[str] = "normal"  # low, normal, high, urgent
    due_date: Optional[datetime] = None
    reminder_time: Optional[datetime] = None
    customer_id: Optional[str] = None
    quote_id: Optional[str] = None


class TaskResponse(BaseModel):
    """Task response model."""
    id: str
    title: str
    description: Optional[str]
    priority: str
    task_type: str
    due_date: Optional[datetime]
    reminder_time: Optional[datetime]
    status: str
    completed_at: Optional[datetime]
    customer_id: Optional[str]
    quote_id: Optional[str]
    customer_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Paginated task list response."""
    tasks: List[TaskResponse]
    total: int
    overdue_count: int
    today_count: int
    upcoming_count: int


class TaskCreateRequest(BaseModel):
    """Create task request."""
    title: str
    description: Optional[str] = None
    priority: Optional[str] = "normal"
    task_type: Optional[str] = "other"  # follow_up, quote, call, site_visit, material_order, reminder, other
    due_date: Optional[datetime] = None
    reminder_time: Optional[datetime] = None
    customer_id: Optional[str] = None
    quote_id: Optional[str] = None


class TaskUpdateRequest(BaseModel):
    """Update task request."""
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None
    reminder_time: Optional[datetime] = None
    status: Optional[str] = None


class QuickTaskRequest(BaseModel):
    """Quick task creation (e.g., from voice)."""
    title: str
    due_in_days: Optional[int] = None  # "in 3 days" → due_in_days=3
    customer_name: Optional[str] = None  # Will search and link to customer


# Helper to get contractor

async def get_contractor(user: dict, db: AsyncSession) -> Contractor:
    """Get contractor for current user."""
    result = await db.execute(
        select(Contractor).where(Contractor.user_id == user["id"])
    )
    contractor = result.scalar_one_or_none()
    if not contractor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contractor profile not found"
        )
    return contractor


def task_to_response(task: Task, customer_name: str = None) -> TaskResponse:
    """Convert Task model to response."""
    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        priority=task.priority or "normal",
        task_type=task.task_type or "other",
        due_date=task.due_date,
        reminder_time=task.reminder_time,
        status=task.status or "pending",
        completed_at=task.completed_at,
        customer_id=task.customer_id,
        quote_id=task.quote_id,
        customer_name=customer_name,
        created_at=task.created_at,
        updated_at=task.updated_at
    )


# Endpoints

@router.get("", response_model=TaskListResponse)
async def list_tasks(
    view: str = Query("all", description="View: all, today, overdue, upcoming, completed"),
    customer_id: Optional[str] = Query(None, description="Filter by customer"),
    task_type: Optional[str] = Query(None, description="Filter by task type"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get paginated list of tasks.

    Views:
    - all: All pending tasks
    - today: Tasks due today
    - overdue: Tasks past due date
    - upcoming: Tasks due in next 7 days
    - completed: Completed tasks
    """
    contractor = await get_contractor(user, db)
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    week_end = today_start + timedelta(days=7)

    # Base query
    base_query = select(Task).where(Task.contractor_id == contractor.id)

    # Apply view filter
    if view == "today":
        base_query = base_query.where(
            and_(
                Task.status == "pending",
                Task.due_date >= today_start,
                Task.due_date < today_end
            )
        )
    elif view == "overdue":
        base_query = base_query.where(
            and_(
                Task.status == "pending",
                Task.due_date < today_start
            )
        )
    elif view == "upcoming":
        base_query = base_query.where(
            and_(
                Task.status == "pending",
                Task.due_date >= today_end,
                Task.due_date < week_end
            )
        )
    elif view == "completed":
        base_query = base_query.where(Task.status == "completed")
    else:  # all
        base_query = base_query.where(Task.status == "pending")

    # Apply customer filter
    if customer_id:
        base_query = base_query.where(Task.customer_id == customer_id)

    # Apply task type filter
    if task_type:
        base_query = base_query.where(Task.task_type == task_type)

    # Apply priority filter
    if priority:
        base_query = base_query.where(Task.priority == priority)

    # Get total count
    count_result = await db.execute(
        select(func.count()).select_from(base_query.subquery())
    )
    total = count_result.scalar() or 0

    # Count overdue, today, upcoming for badge counts
    overdue_result = await db.execute(
        select(func.count(Task.id)).where(
            and_(
                Task.contractor_id == contractor.id,
                Task.status == "pending",
                Task.due_date < today_start
            )
        )
    )
    overdue_count = overdue_result.scalar() or 0

    today_result = await db.execute(
        select(func.count(Task.id)).where(
            and_(
                Task.contractor_id == contractor.id,
                Task.status == "pending",
                Task.due_date >= today_start,
                Task.due_date < today_end
            )
        )
    )
    today_count = today_result.scalar() or 0

    upcoming_result = await db.execute(
        select(func.count(Task.id)).where(
            and_(
                Task.contractor_id == contractor.id,
                Task.status == "pending",
                Task.due_date >= today_end,
                Task.due_date < week_end
            )
        )
    )
    upcoming_count = upcoming_result.scalar() or 0

    # Apply sorting - overdue first, then by due date
    base_query = base_query.order_by(
        Task.due_date.asc().nullslast(),
        Task.created_at.desc()
    )

    # Apply pagination
    base_query = base_query.limit(limit).offset(offset)

    # Execute query
    result = await db.execute(base_query)
    tasks = result.scalars().all()

    # Get customer names for tasks with customer_id
    customer_ids = [t.customer_id for t in tasks if t.customer_id]
    customer_names = {}
    if customer_ids:
        cust_result = await db.execute(
            select(Customer.id, Customer.name).where(Customer.id.in_(customer_ids))
        )
        customer_names = {row[0]: row[1] for row in cust_result.fetchall()}

    return TaskListResponse(
        tasks=[
            task_to_response(t, customer_names.get(t.customer_id))
            for t in tasks
        ],
        total=total,
        overdue_count=overdue_count,
        today_count=today_count,
        upcoming_count=upcoming_count
    )


@router.get("/summary")
async def get_task_summary(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get task count summary for badges."""
    contractor = await get_contractor(user, db)
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    week_end = today_start + timedelta(days=7)

    # Count pending tasks
    pending_result = await db.execute(
        select(func.count(Task.id)).where(
            and_(
                Task.contractor_id == contractor.id,
                Task.status == "pending"
            )
        )
    )
    pending = pending_result.scalar() or 0

    # Count overdue
    overdue_result = await db.execute(
        select(func.count(Task.id)).where(
            and_(
                Task.contractor_id == contractor.id,
                Task.status == "pending",
                Task.due_date < today_start
            )
        )
    )
    overdue = overdue_result.scalar() or 0

    # Count due today
    today_result = await db.execute(
        select(func.count(Task.id)).where(
            and_(
                Task.contractor_id == contractor.id,
                Task.status == "pending",
                Task.due_date >= today_start,
                Task.due_date < today_end
            )
        )
    )
    today = today_result.scalar() or 0

    # Count upcoming (next 7 days)
    upcoming_result = await db.execute(
        select(func.count(Task.id)).where(
            and_(
                Task.contractor_id == contractor.id,
                Task.status == "pending",
                Task.due_date >= today_end,
                Task.due_date < week_end
            )
        )
    )
    upcoming = upcoming_result.scalar() or 0

    return {
        "pending": pending,
        "overdue": overdue,
        "today": today,
        "upcoming": upcoming,
        "urgent_count": overdue + today  # Badge count for nav
    }


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single task."""
    contractor = await get_contractor(user, db)

    result = await db.execute(
        select(Task).where(
            and_(
                Task.id == task_id,
                Task.contractor_id == contractor.id
            )
        )
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Get customer name if linked
    customer_name = None
    if task.customer_id:
        cust_result = await db.execute(
            select(Customer.name).where(Customer.id == task.customer_id)
        )
        customer_name = cust_result.scalar()

    return task_to_response(task, customer_name)


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    request: TaskCreateRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new task."""
    contractor = await get_contractor(user, db)

    task = Task(
        contractor_id=contractor.id,
        title=request.title,
        description=request.description,
        priority=request.priority or "normal",
        task_type=request.task_type or "other",
        due_date=request.due_date,
        reminder_time=request.reminder_time,
        customer_id=request.customer_id,
        quote_id=request.quote_id,
        status="pending"
    )

    db.add(task)
    await db.commit()
    await db.refresh(task)

    # Get customer name if linked
    customer_name = None
    if task.customer_id:
        cust_result = await db.execute(
            select(Customer.name).where(Customer.id == task.customer_id)
        )
        customer_name = cust_result.scalar()

    return task_to_response(task, customer_name)


@router.post("/quick", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_quick_task(
    request: QuickTaskRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Quick task creation for voice commands.

    Supports natural language like "Remind me to call Johnson in 3 days"
    """
    contractor = await get_contractor(user, db)

    # Calculate due date from due_in_days
    due_date = None
    if request.due_in_days:
        due_date = datetime.utcnow() + timedelta(days=request.due_in_days)

    # Find customer by name if provided
    customer_id = None
    customer_name = None
    if request.customer_name:
        from ..services.customer_service import CustomerService
        customers = await CustomerService.search_customers(
            db=db,
            contractor_id=contractor.id,
            query=request.customer_name,
            limit=1
        )
        if customers:
            customer_id = customers[0].id
            customer_name = customers[0].name

    task = Task(
        contractor_id=contractor.id,
        title=request.title,
        due_date=due_date,
        customer_id=customer_id,
        status="pending",
        priority="normal"
    )

    db.add(task)
    await db.commit()
    await db.refresh(task)

    return task_to_response(task, customer_name)


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    request: TaskUpdateRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a task."""
    contractor = await get_contractor(user, db)

    result = await db.execute(
        select(Task).where(
            and_(
                Task.id == task_id,
                Task.contractor_id == contractor.id
            )
        )
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Update fields
    if request.title is not None:
        task.title = request.title
    if request.description is not None:
        task.description = request.description
    if request.priority is not None:
        task.priority = request.priority
    if request.due_date is not None:
        task.due_date = request.due_date
    if request.reminder_time is not None:
        task.reminder_time = request.reminder_time
    if request.status is not None:
        task.status = request.status
        if request.status == "completed":
            task.completed_at = datetime.utcnow()

    task.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(task)

    # Get customer name if linked
    customer_name = None
    if task.customer_id:
        cust_result = await db.execute(
            select(Customer.name).where(Customer.id == task.customer_id)
        )
        customer_name = cust_result.scalar()

    return task_to_response(task, customer_name)


@router.post("/{task_id}/complete", response_model=TaskResponse)
async def toggle_task_complete(
    task_id: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Toggle a task's completion status (complete ↔ pending)."""
    contractor = await get_contractor(user, db)

    result = await db.execute(
        select(Task).where(
            and_(
                Task.id == task_id,
                Task.contractor_id == contractor.id
            )
        )
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Toggle status
    if task.status == "completed":
        task.status = "pending"
        task.completed_at = None
    else:
        task.status = "completed"
        task.completed_at = datetime.utcnow()
    task.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(task)

    # Get customer name if linked
    customer_name = None
    if task.customer_id:
        cust_result = await db.execute(
            select(Customer.name).where(Customer.id == task.customer_id)
        )
        customer_name = cust_result.scalar()

    return task_to_response(task, customer_name)


@router.post("/{task_id}/snooze", response_model=TaskResponse)
async def snooze_task(
    task_id: str,
    days: int = Query(1, ge=1, le=30, description="Days to snooze"),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Snooze a task by X days."""
    contractor = await get_contractor(user, db)

    result = await db.execute(
        select(Task).where(
            and_(
                Task.id == task_id,
                Task.contractor_id == contractor.id
            )
        )
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Push due date forward
    if task.due_date:
        task.due_date = task.due_date + timedelta(days=days)
    else:
        task.due_date = datetime.utcnow() + timedelta(days=days)

    task.status = "pending"  # Reset from snoozed if needed
    task.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(task)

    # Get customer name if linked
    customer_name = None
    if task.customer_id:
        cust_result = await db.execute(
            select(Customer.name).where(Customer.id == task.customer_id)
        )
        customer_name = cust_result.scalar()

    return task_to_response(task, customer_name)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a task."""
    contractor = await get_contractor(user, db)

    result = await db.execute(
        select(Task).where(
            and_(
                Task.id == task_id,
                Task.contractor_id == contractor.id
            )
        )
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    await db.delete(task)
    await db.commit()
