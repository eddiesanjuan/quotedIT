"""
Onboarding API routes for Quoted.
Handles the setup interview process for new contractors.
"""

from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..services import get_onboarding_service


router = APIRouter()


# Request/Response models

class StartSetupRequest(BaseModel):
    """Request to start setup interview."""
    contractor_name: str
    primary_trade: str


class SetupSessionResponse(BaseModel):
    """Setup session response."""
    session_id: str
    contractor_name: str
    primary_trade: str
    status: str
    initial_message: str
    messages: List[dict]
    started_at: str


class ContinueSetupRequest(BaseModel):
    """Request to continue setup conversation."""
    message: str


class QuickSetupRequest(BaseModel):
    """Request for quick setup (skip interview)."""
    contractor_name: str
    primary_trade: str
    labor_rate: float
    material_markup: float = 20.0
    minimum_job: float = 500.0
    pricing_notes: Optional[str] = None


class PricingModelResponse(BaseModel):
    """Extracted pricing model response."""
    labor_rate_hourly: Optional[float] = None
    helper_rate_hourly: Optional[float] = None
    material_markup_percent: Optional[float] = None
    minimum_job_amount: Optional[float] = None
    pricing_knowledge: dict = {}
    pricing_notes: Optional[str] = None
    terms: Optional[dict] = None
    job_types: Optional[List[dict]] = None
    confidence_summary: Optional[str] = None
    follow_up_questions: Optional[List[str]] = None


# In-memory session storage
_sessions = {}


@router.post("/start", response_model=SetupSessionResponse)
async def start_setup(request: StartSetupRequest):
    """
    Start a new setup interview session.

    Returns the initial message and session info.
    """
    try:
        onboarding_service = get_onboarding_service()

        session = await onboarding_service.start_setup(
            contractor_name=request.contractor_name,
            primary_trade=request.primary_trade,
        )

        _sessions[session["session_id"]] = session

        return SetupSessionResponse(**session)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/continue", response_model=SetupSessionResponse)
async def continue_setup(session_id: str, request: ContinueSetupRequest):
    """
    Continue an ongoing setup conversation.

    Send the contractor's response and get the next AI message.
    """
    if session_id not in _sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        onboarding_service = get_onboarding_service()

        session = await onboarding_service.continue_setup(
            session=_sessions[session_id],
            user_message=request.message,
        )

        _sessions[session_id] = session

        return SetupSessionResponse(**session)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/complete", response_model=PricingModelResponse)
async def complete_setup(session_id: str):
    """
    Complete the setup and extract the pricing model.

    Call this when the interview is done to get the structured pricing model.
    """
    if session_id not in _sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = _sessions[session_id]

    if len(session.get("messages", [])) < 4:
        raise HTTPException(
            status_code=400,
            detail="Interview too short. Please continue the conversation first."
        )

    try:
        onboarding_service = get_onboarding_service()

        pricing_model = await onboarding_service.extract_pricing_model(session)

        # Mark session as complete
        session["status"] = "completed"
        session["completed_at"] = datetime.utcnow().isoformat()
        session["extracted_model"] = pricing_model
        _sessions[session_id] = session

        return PricingModelResponse(**pricing_model)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quick", response_model=PricingModelResponse)
async def quick_setup(request: QuickSetupRequest):
    """
    Quick setup without the full interview.

    For contractors who want to get started fast with just basic pricing.
    """
    try:
        onboarding_service = get_onboarding_service()

        pricing_model = await onboarding_service.quick_setup(
            contractor_name=request.contractor_name,
            primary_trade=request.primary_trade,
            labor_rate=request.labor_rate,
            material_markup=request.material_markup,
            minimum_job=request.minimum_job,
            pricing_notes=request.pricing_notes,
        )

        return PricingModelResponse(**pricing_model)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}", response_model=SetupSessionResponse)
async def get_session(session_id: str):
    """Get the current state of a setup session."""
    if session_id not in _sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    return SetupSessionResponse(**_sessions[session_id])


@router.get("/{session_id}/messages")
async def get_messages(session_id: str):
    """Get all messages from a setup session."""
    if session_id not in _sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": session_id,
        "messages": _sessions[session_id].get("messages", []),
        "status": _sessions[session_id].get("status", "unknown"),
    }


@router.get("/")
async def list_sessions():
    """List all sessions (for debugging/demo)."""
    return {
        "sessions": [
            {
                "session_id": s["session_id"],
                "contractor_name": s.get("contractor_name"),
                "status": s.get("status"),
                "message_count": len(s.get("messages", [])),
            }
            for s in _sessions.values()
        ],
        "count": len(_sessions),
    }
