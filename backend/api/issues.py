"""
Issue reporting API for Quoted.
Allows users to report bugs/issues that can be processed by autonomous Claude Code.
"""

from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from ..models.database import UserIssue, get_database_url
from ..services.auth import get_current_user_optional


router = APIRouter()


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


class IssueUpdateRequest(BaseModel):
    """Request to update an issue (for Claude Code agent)."""
    status: Optional[str] = None
    agent_analysis: Optional[str] = None
    agent_solution: Optional[str] = None
    files_modified: Optional[List[str]] = None
    commit_hash: Optional[str] = None


# In-memory storage for MVP (will use database in production)
_issues: dict = {}


@router.post("/", response_model=IssueResponse)
async def create_issue(request: IssueCreateRequest):
    """
    Report a new issue.

    Users can report bugs, feature requests, or other issues.
    These will be picked up by the autonomous Claude Code agent.
    """
    import uuid

    issue_id = str(uuid.uuid4())
    now = datetime.utcnow()

    issue = {
        "id": issue_id,
        "created_at": now,
        "updated_at": now,
        "title": request.title,
        "description": request.description,
        "category": request.category,
        "severity": request.severity,
        "status": "new",
        "page_url": request.page_url,
        "browser_info": request.browser_info,
        "error_message": request.error_message,
        "steps_to_reproduce": request.steps_to_reproduce,
        "agent_analysis": None,
        "agent_solution": None,
        "files_modified": None,
        "commit_hash": None,
        "resolved_at": None,
    }

    _issues[issue_id] = issue

    return IssueResponse(**issue)


@router.get("/", response_model=List[IssueResponse])
async def list_issues(
    status: Optional[str] = None,
    category: Optional[str] = None,
):
    """
    List all issues, optionally filtered by status or category.
    """
    issues = list(_issues.values())

    if status:
        issues = [i for i in issues if i["status"] == status]
    if category:
        issues = [i for i in issues if i["category"] == category]

    # Sort by created_at descending (newest first)
    issues.sort(key=lambda x: x["created_at"], reverse=True)

    return [IssueResponse(**i) for i in issues]


@router.get("/new", response_model=List[IssueResponse])
async def get_new_issues():
    """
    Get all issues with status='new' for the autonomous agent to process.
    This is the endpoint the polling script will call.
    """
    new_issues = [i for i in _issues.values() if i["status"] == "new"]
    new_issues.sort(key=lambda x: x["created_at"])  # Oldest first (FIFO)
    return [IssueResponse(**i) for i in new_issues]


@router.get("/{issue_id}", response_model=IssueResponse)
async def get_issue(issue_id: str):
    """Get a specific issue by ID."""
    if issue_id not in _issues:
        raise HTTPException(status_code=404, detail="Issue not found")

    return IssueResponse(**_issues[issue_id])


@router.patch("/{issue_id}", response_model=IssueResponse)
async def update_issue(issue_id: str, request: IssueUpdateRequest):
    """
    Update an issue (used by Claude Code agent to report progress).
    """
    if issue_id not in _issues:
        raise HTTPException(status_code=404, detail="Issue not found")

    issue = _issues[issue_id]

    if request.status:
        issue["status"] = request.status
        if request.status == "in_progress" and not issue.get("picked_up_at"):
            issue["picked_up_at"] = datetime.utcnow()
        elif request.status == "resolved":
            issue["resolved_at"] = datetime.utcnow()

    if request.agent_analysis:
        issue["agent_analysis"] = request.agent_analysis

    if request.agent_solution:
        issue["agent_solution"] = request.agent_solution

    if request.files_modified:
        issue["files_modified"] = request.files_modified

    if request.commit_hash:
        issue["commit_hash"] = request.commit_hash

    issue["updated_at"] = datetime.utcnow()
    _issues[issue_id] = issue

    return IssueResponse(**issue)


@router.post("/{issue_id}/claim")
async def claim_issue(issue_id: str):
    """
    Claim an issue for processing (prevents duplicate work).
    Returns the issue if successfully claimed, 409 if already claimed.
    """
    if issue_id not in _issues:
        raise HTTPException(status_code=404, detail="Issue not found")

    issue = _issues[issue_id]

    if issue["status"] != "new":
        raise HTTPException(
            status_code=409,
            detail=f"Issue already claimed (status: {issue['status']})"
        )

    issue["status"] = "queued"
    issue["picked_up_at"] = datetime.utcnow()
    issue["updated_at"] = datetime.utcnow()
    _issues[issue_id] = issue

    return IssueResponse(**issue)
