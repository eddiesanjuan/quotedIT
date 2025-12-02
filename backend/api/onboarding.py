"""
Onboarding API routes for Quoted.
Handles the setup interview process for new contractors.

Now persists to database instead of in-memory storage.
"""

from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from ..services import get_onboarding_service, get_database_service
from ..services.auth import get_current_contractor
from ..services.analytics import analytics_service
from ..models.database import Contractor
from ..prompts import get_setup_system_prompt


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


def _conversation_to_response(conversation) -> dict:
    """Convert database SetupConversation to API response format."""
    session_data = conversation.session_data or {}
    return {
        "session_id": conversation.id,
        "contractor_name": session_data.get("contractor_name", ""),
        "primary_trade": session_data.get("primary_trade", ""),
        "status": conversation.status,
        "initial_message": session_data.get("initial_message", ""),
        "messages": conversation.messages or [],
        "started_at": conversation.created_at.isoformat() if conversation.created_at else "",
    }


@router.post("/start", response_model=SetupSessionResponse)
async def start_setup(request: StartSetupRequest):
    """
    Start a new setup interview session.

    Returns the initial message and session info.
    """
    try:
        onboarding_service = get_onboarding_service()
        db = get_database_service()

        # Generate the initial session data
        session = await onboarding_service.start_setup(
            contractor_name=request.contractor_name,
            primary_trade=request.primary_trade,
        )

        # Persist to database
        conversation = await db.create_setup_conversation(
            messages=session.get("messages", []),
            session_data={
                "contractor_name": session.get("contractor_name"),
                "primary_trade": session.get("primary_trade"),
                "initial_message": session.get("initial_message"),
            },
        )

        # Return response with DB-generated ID
        return SetupSessionResponse(
            session_id=conversation.id,
            contractor_name=request.contractor_name,
            primary_trade=request.primary_trade,
            status=conversation.status,
            initial_message=session.get("initial_message", ""),
            messages=conversation.messages or [],
            started_at=conversation.created_at.isoformat() if conversation.created_at else datetime.utcnow().isoformat(),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/continue", response_model=SetupSessionResponse)
async def continue_setup(session_id: str, request: ContinueSetupRequest):
    """
    Continue an ongoing setup conversation.

    Send the contractor's response and get the next AI message.
    """
    db = get_database_service()

    # Fetch from database
    conversation = await db.get_setup_conversation(session_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        onboarding_service = get_onboarding_service()

        # Reconstruct session format for the service
        session_data = conversation.session_data or {}
        contractor_name = session_data.get("contractor_name", "")
        primary_trade = session_data.get("primary_trade", "")

        # Regenerate system prompt (not stored in DB)
        system_prompt = get_setup_system_prompt(contractor_name, primary_trade)

        session = {
            "session_id": conversation.id,
            "contractor_name": contractor_name,
            "primary_trade": primary_trade,
            "system_prompt": system_prompt,
            "status": conversation.status,
            "initial_message": session_data.get("initial_message", ""),
            "messages": conversation.messages or [],
            "started_at": conversation.created_at.isoformat() if conversation.created_at else "",
        }

        # Continue the conversation
        updated_session = await onboarding_service.continue_setup(
            session=session,
            user_message=request.message,
        )

        # Update database
        await db.update_setup_conversation(
            conversation_id=session_id,
            messages=updated_session.get("messages", []),
            session_data={
                **session_data,
                "initial_message": updated_session.get("initial_message", session_data.get("initial_message")),
            },
        )

        # Fetch updated conversation
        conversation = await db.get_setup_conversation(session_id)

        return SetupSessionResponse(**_conversation_to_response(conversation))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/complete", response_model=PricingModelResponse)
async def complete_setup(
    session_id: str,
    contractor: Contractor = Depends(get_current_contractor),
):
    """
    Complete the setup and extract the pricing model.
    Requires authentication. Saves pricing model to the contractor's record.

    Call this when the interview is done to get the structured pricing model.
    """
    db = get_database_service()

    conversation = await db.get_setup_conversation(session_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Session not found")

    if len(conversation.messages or []) < 4:
        raise HTTPException(
            status_code=400,
            detail="Interview too short. Please continue the conversation first."
        )

    try:
        onboarding_service = get_onboarding_service()

        # Reconstruct session format
        session_data = conversation.session_data or {}
        session = {
            "session_id": conversation.id,
            "contractor_name": session_data.get("contractor_name", ""),
            "primary_trade": session_data.get("primary_trade", ""),
            "status": conversation.status,
            "initial_message": session_data.get("initial_message", ""),
            "messages": conversation.messages or [],
            "started_at": conversation.created_at.isoformat() if conversation.created_at else "",
        }

        pricing_model = await onboarding_service.extract_pricing_model(session)

        # Update setup_conversation - mark as complete and store extracted data
        await db.update_setup_conversation(
            conversation_id=session_id,
            status="completed",
            extracted_data=pricing_model,
        )

        # Save pricing model to the contractor's record in pricing_models table
        existing_pricing = await db.get_pricing_model(contractor.id)
        if existing_pricing:
            # Update existing pricing model
            await db.update_pricing_model(
                contractor_id=contractor.id,
                labor_rate_hourly=pricing_model.get("labor_rate_hourly"),
                helper_rate_hourly=pricing_model.get("helper_rate_hourly"),
                material_markup_percent=pricing_model.get("material_markup_percent", 20.0),
                minimum_job_amount=pricing_model.get("minimum_job_amount"),
                pricing_knowledge=pricing_model.get("pricing_knowledge", {}),
                pricing_notes=pricing_model.get("pricing_notes"),
            )
        else:
            # Create new pricing model
            await db.create_pricing_model(
                contractor_id=contractor.id,
                labor_rate_hourly=pricing_model.get("labor_rate_hourly"),
                helper_rate_hourly=pricing_model.get("helper_rate_hourly"),
                material_markup_percent=pricing_model.get("material_markup_percent", 20.0),
                minimum_job_amount=pricing_model.get("minimum_job_amount"),
                pricing_knowledge=pricing_model.get("pricing_knowledge", {}),
                pricing_notes=pricing_model.get("pricing_notes"),
            )

        # Track onboarding completion
        try:
            analytics_service.track_event(
                user_id=str(contractor.user_id),
                event_name="onboarding_completed",
                properties={
                    "contractor_id": str(contractor.id),
                    "primary_trade": contractor.primary_trade,
                    "has_labor_rate": pricing_model.get("labor_rate_hourly") is not None,
                    "has_material_markup": pricing_model.get("material_markup_percent") is not None,
                    "message_count": len(conversation.messages or []),
                }
            )
        except Exception as e:
            print(f"Warning: Failed to track onboarding completion: {e}")

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
    db = get_database_service()

    conversation = await db.get_setup_conversation(session_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Session not found")

    return SetupSessionResponse(**_conversation_to_response(conversation))


@router.get("/{session_id}/messages")
async def get_messages(session_id: str):
    """Get all messages from a setup session."""
    db = get_database_service()

    conversation = await db.get_setup_conversation(session_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": conversation.id,
        "messages": conversation.messages or [],
        "status": conversation.status,
    }


@router.get("/industries")
async def get_industries():
    """
    Get available industries/trades for selection.
    Returns list of industries with display info for UI.
    """
    # Use the same trade defaults from onboarding service
    onboarding_service = get_onboarding_service()

    # Map of trade keys to display info
    industries = [
        {"key": "deck_builder", "display_name": "Deck Builder", "icon": "🏗️", "category": "Construction"},
        {"key": "painter", "display_name": "Painter", "icon": "🎨", "category": "Finishing"},
        {"key": "fence_installer", "display_name": "Fence Installer", "icon": "🚧", "category": "Outdoor"},
        {"key": "landscaper", "display_name": "Landscaper", "icon": "🌳", "category": "Outdoor"},
        {"key": "electrician", "display_name": "Electrician", "icon": "⚡", "category": "Electrical"},
        {"key": "plumber", "display_name": "Plumber", "icon": "🔧", "category": "Plumbing"},
        {"key": "hvac", "display_name": "HVAC", "icon": "❄️", "category": "HVAC"},
        {"key": "roofer", "display_name": "Roofer", "icon": "🏠", "category": "Construction"},
        {"key": "flooring", "display_name": "Flooring", "icon": "📐", "category": "Finishing"},
        {"key": "tile", "display_name": "Tile Installer", "icon": "🔲", "category": "Finishing"},
        {"key": "concrete", "display_name": "Concrete", "icon": "🏗️", "category": "Construction"},
        {"key": "framing", "display_name": "Framing", "icon": "🔨", "category": "Construction"},
        {"key": "drywall", "display_name": "Drywall", "icon": "🧱", "category": "Finishing"},
        {"key": "window_door", "display_name": "Window & Door", "icon": "🚪", "category": "Installation"},
        {"key": "siding", "display_name": "Siding", "icon": "🏡", "category": "Exterior"},
        {"key": "gutters", "display_name": "Gutters", "icon": "💧", "category": "Exterior"},
        {"key": "insulation", "display_name": "Insulation", "icon": "🧊", "category": "Installation"},
        {"key": "garage_door", "display_name": "Garage Door", "icon": "🚗", "category": "Installation"},
        {"key": "pool_spa", "display_name": "Pool & Spa", "icon": "🏊", "category": "Outdoor"},
        {"key": "masonry", "display_name": "Masonry", "icon": "🧱", "category": "Construction"},
        {"key": "tree_service", "display_name": "Tree Service", "icon": "🌲", "category": "Outdoor"},
        {"key": "pressure_washing", "display_name": "Pressure Washing", "icon": "💦", "category": "Cleaning"},
        {"key": "closet_organizer", "display_name": "Closet Organizer", "icon": "🗄️", "category": "Organization"},
        {"key": "cabinet_maker", "display_name": "Cabinet Maker", "icon": "🪑", "category": "Finishing"},
        {"key": "general_contractor", "display_name": "General Contractor", "icon": "👷", "category": "General"},
    ]

    return {
        "industries": industries,
        "count": len(industries),
    }


@router.get("/")
async def list_sessions():
    """List all sessions (for debugging/demo)."""
    # Note: This returns empty for now - would need a list_setup_conversations method
    # Keeping backward compatibility but encouraging use of specific session endpoints
    return {
        "sessions": [],
        "count": 0,
        "note": "Use specific session_id endpoints. Session list not implemented for database storage.",
    }
