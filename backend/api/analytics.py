"""
Analytics API routes for Quoted (DISC-137).

Handles analytics data collection from frontend:
- Exit intent survey submissions
- Future: other conversion funnel events

No authentication required for data collection endpoints.
"""

import hashlib
from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..services.exit_survey import ExitSurveyService
from ..services.database import async_session_factory
from ..services.logging import get_api_logger

logger = get_api_logger()

router = APIRouter()

# Rate limiter - prevent abuse
limiter = Limiter(key_func=get_remote_address)


class ExitSurveyRequest(BaseModel):
    """Exit survey submission request."""
    reasons: List[str]  # e.g., ["not_my_trade", "pricing_high"]
    other_text: Optional[str] = None
    page_url: Optional[str] = None
    session_id: Optional[str] = None


class ExitSurveyResponse(BaseModel):
    """Exit survey submission response."""
    success: bool
    message: str


@router.post("/exit-survey", response_model=ExitSurveyResponse)
async def submit_exit_survey(
    request: Request,
    survey: ExitSurveyRequest
):
    """
    Submit exit intent survey response.

    Called from landing page when visitor completes the exit survey.
    Rate limited to 5 per hour per IP to prevent abuse.

    Triggers:
    - Instant alert if concerning keywords in other_text
    - Inclusion in daily digest email to founder
    """
    try:
        # Get client info
        client_ip = get_remote_address(request)
        ip_hash = hashlib.sha256(client_ip.encode()).hexdigest()[:32] if client_ip else None
        user_agent = request.headers.get("user-agent", "")[:500]
        referrer = request.headers.get("referer", "")[:500]

        # Validate reasons
        valid_reasons = {
            "not_my_trade",
            "pricing_high",
            "no_time",
            "need_examples",
            "other"
        }

        filtered_reasons = [r for r in survey.reasons if r in valid_reasons]
        if not filtered_reasons:
            raise HTTPException(
                status_code=400,
                detail="At least one valid reason is required"
            )

        # Store survey response
        async with async_session_factory() as db:
            survey_record = await ExitSurveyService.create_survey(
                db=db,
                reasons=filtered_reasons,
                other_text=survey.other_text,
                page_url=survey.page_url,
                referrer=referrer,
                user_agent=user_agent,
                ip_hash=ip_hash,
                session_id=survey.session_id
            )

            # Check for concerning keywords and send instant alert
            alert_sent = await ExitSurveyService.check_and_send_alert(
                db=db,
                survey=survey_record
            )

            await db.commit()

            logger.info(
                f"Exit survey submitted: reasons={filtered_reasons}, "
                f"has_other_text={bool(survey.other_text)}, alert_sent={alert_sent}"
            )

        return ExitSurveyResponse(
            success=True,
            message="Thank you for your feedback"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to submit exit survey: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to submit survey"
        )
