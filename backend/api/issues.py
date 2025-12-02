"""
Issue reporting API for Quoted.
Allows users to report bugs/issues that can be processed by autonomous Claude Code.

Now uses SQLite persistence via DatabaseService (upgraded from in-memory storage).
"""

from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..services.database import get_db_service


router = APIRouter()
db = get_db_service()


# Request/Response models

class IssueCreateRequest(BaseModel):
    """Request to create a new issue."""
    title: str
    description: str
    category: Optional[str] = "bug"  # bug, feature_request, ui_issue, pricing_issue
    severity: Optional[str] = "medium"  # low, medium, high, critical
    page_url: Optional[str] = None
    browser_info: Optional[str] = None
    error_message: Optional[str] = None
    steps_to_reproduce: Optional[str] = None


class IssueResponse(BaseModel):
    """Issue response model."""
    id: str
    created_at: datetime
    title: str
    description: str
    category: Optional[str]
    severity: str
    status: str
    page_url: Optional[str]
    error_message: Optional[str]
    agent_analysis: Optional[str] = None
    agent_solution: Optional[str] = None
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class IssueUpdateRequest(BaseModel):
    """Request to update an issue (for Claude Code agent)."""
    status: Optional[str] = None
    agent_analysis: Optional[str] = None
    agent_solution: Optional[str] = None
    files_modified: Optional[List[str]] = None
    commit_hash: Optional[str] = None


def _issue_to_response(issue) -> IssueResponse:
    """Convert UserIssue model to IssueResponse."""
    return IssueResponse(
        id=issue.id,
        created_at=issue.created_at,
        title=issue.title,
        description=issue.description,
        category=issue.category,
        severity=issue.severity,
        status=issue.status,
        page_url=issue.page_url,
        error_message=issue.error_message,
        agent_analysis=issue.agent_analysis,
        agent_solution=issue.agent_solution,
        resolved_at=issue.resolved_at,
    )


@router.post("/", response_model=IssueResponse)
async def create_issue(request: IssueCreateRequest):
    """
    Report a new issue.

    Users can report bugs, feature requests, or other issues.
    These will be picked up by the autonomous Claude Code agent.
    Issues are persisted to SQLite and survive Railway restarts.
    """
    issue = await db.create_issue(
        title=request.title,
        description=request.description,
        category=request.category or "bug",
        severity=request.severity or "medium",
        page_url=request.page_url,
        browser_info=request.browser_info,
        error_message=request.error_message,
        steps_to_reproduce=request.steps_to_reproduce,
    )

    return _issue_to_response(issue)


@router.get("/", response_model=List[IssueResponse])
async def list_issues(
    status: Optional[str] = None,
    category: Optional[str] = None,
):
    """
    List all issues, optionally filtered by status or category.
    """
    issues = await db.get_all_issues(status=status, category=category)
    return [_issue_to_response(i) for i in issues]


@router.get("/new", response_model=List[IssueResponse])
async def get_new_issues():
    """
    Get all issues with status='new' for the autonomous agent to process.
    This is the endpoint the polling script will call.
    """
    issues = await db.get_new_issues()
    return [_issue_to_response(i) for i in issues]


@router.get("/{issue_id}", response_model=IssueResponse)
async def get_issue(issue_id: str):
    """Get a specific issue by ID."""
    issue = await db.get_issue(issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    return _issue_to_response(issue)


@router.patch("/{issue_id}", response_model=IssueResponse)
async def update_issue(issue_id: str, request: IssueUpdateRequest):
    """
    Update an issue (used by Claude Code agent to report progress).
    """
    # Check issue exists
    existing = await db.get_issue(issue_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Issue not found")

    # Build update kwargs
    update_kwargs = {}

    if request.status:
        update_kwargs["status"] = request.status
        if request.status == "in_progress" and not existing.picked_up_at:
            update_kwargs["picked_up_at"] = datetime.utcnow()
        elif request.status == "resolved":
            update_kwargs["resolved_at"] = datetime.utcnow()

    if request.agent_analysis:
        update_kwargs["agent_analysis"] = request.agent_analysis

    if request.agent_solution:
        update_kwargs["agent_solution"] = request.agent_solution

    if request.files_modified:
        update_kwargs["files_modified"] = request.files_modified

    if request.commit_hash:
        update_kwargs["commit_hash"] = request.commit_hash

    issue = await db.update_issue(issue_id, **update_kwargs)
    return _issue_to_response(issue)


@router.post("/{issue_id}/claim", response_model=IssueResponse)
async def claim_issue(issue_id: str):
    """
    Claim an issue for processing (prevents duplicate work).
    Returns the issue if successfully claimed, 409 if already claimed.
    """
    issue = await db.get_issue(issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    if issue.status != "new":
        raise HTTPException(
            status_code=409,
            detail=f"Issue already claimed (status: {issue.status})"
        )

    issue = await db.update_issue(
        issue_id,
        status="queued",
        picked_up_at=datetime.utcnow(),
    )

    return _issue_to_response(issue)
