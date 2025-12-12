"""
CRM Voice Command Service (DISC-090).
Handles voice-operated CRM for contractors in trucks.

Supported commands:
- Search: "Show me John Smith" → customer_search
- Detail: "What's the history with Johnson Electric?" → customer_detail
- Stats: "How much have I quoted the Hendersons?" → customer_stats
- Notes: "Add a note to Mike Wilson: Prefers morning" → add_note
- Tags: "Tag Sarah's Bakery as VIP" → add_tag
- Insights: "Which customers haven't had a quote in 6 months?" → dormant_customers
"""

import json
import re
from typing import Optional, Dict, Any, List
from enum import Enum
from pydantic import BaseModel, Field

import anthropic

from ..config import settings
from .customer_service import CustomerService


class CrmIntent(str, Enum):
    """CRM voice command intents."""
    SEARCH = "search"
    DETAIL = "detail"
    STATS = "stats"
    ADD_NOTE = "add_note"
    ADD_TAG = "add_tag"
    DORMANT = "dormant"
    TOP_CUSTOMERS = "top_customers"
    NOT_CRM = "not_crm"


class CrmCommandResult(BaseModel):
    """Result of a CRM voice command."""
    intent: CrmIntent
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


# Tool definition for Claude CRM intent detection
CRM_INTENT_TOOL = {
    "name": "detect_crm_intent",
    "description": "Detect if the voice input is a CRM command and extract relevant parameters.",
    "input_schema": {
        "type": "object",
        "properties": {
            "is_crm_command": {
                "type": "boolean",
                "description": "True if this is a CRM-related command, False if it's a quote request"
            },
            "intent": {
                "type": "string",
                "enum": ["search", "detail", "stats", "add_note", "add_tag", "dormant", "top_customers", "not_crm"],
                "description": "The detected CRM intent"
            },
            "customer_query": {
                "type": ["string", "null"],
                "description": "Customer name or search term if mentioned"
            },
            "note_content": {
                "type": ["string", "null"],
                "description": "Note content for add_note intent"
            },
            "tag_name": {
                "type": ["string", "null"],
                "description": "Tag name for add_tag intent"
            },
            "days_dormant": {
                "type": ["integer", "null"],
                "description": "Number of days for dormant customer query (default 90)"
            }
        },
        "required": ["is_crm_command", "intent"]
    }
}


class CrmVoiceService:
    """
    Service for handling CRM voice commands.
    Uses Claude to understand intent and CustomerService to execute.
    """

    # CRM trigger keywords for quick pre-filtering
    CRM_KEYWORDS = [
        "customer", "who did", "show me", "find", "search",
        "add note", "add a note", "note to", "tag as", "mark as",
        "how much", "total", "history with", "dormant", "inactive",
        "haven't quoted", "top customers", "best customers", "vip"
    ]

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.model = "claude-sonnet-4-20250514"  # Fast model for intent detection

    def is_likely_crm_command(self, text: str) -> bool:
        """
        Quick pre-filter to check if text might be CRM-related.
        Avoids expensive API calls for obvious quote requests.
        """
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.CRM_KEYWORDS)

    async def detect_intent(self, transcription: str) -> Dict[str, Any]:
        """
        Use Claude to detect CRM intent from voice transcription.

        Args:
            transcription: The transcribed voice input

        Returns:
            Dict with intent detection results
        """
        # Quick pre-filter
        if not self.is_likely_crm_command(transcription):
            return {
                "is_crm_command": False,
                "intent": CrmIntent.NOT_CRM,
                "customer_query": None,
                "note_content": None,
                "tag_name": None,
                "days_dormant": None
            }

        prompt = f"""You are a CRM assistant for a contractor quoting app. Analyze this voice input and determine if it's a CRM command or a quote request.

CRM commands include:
- Searching for a customer: "Show me John Smith", "Find Johnson Electric"
- Getting customer history: "What's the history with the Hendersons?", "Tell me about Mike Wilson"
- Customer stats: "How much have I quoted Sarah's Bakery?", "What's my total with ABC Corp?"
- Adding notes: "Add a note to Mike Wilson: he prefers morning appointments"
- Adding tags: "Tag Sarah's Bakery as VIP", "Mark Johnson Electric as commercial"
- Dormant customers: "Which customers haven't had a quote in 6 months?", "Show me inactive customers"
- Top customers: "Who are my top customers?", "Best customers by revenue"

Quote requests are about specific jobs, like:
- "I need a quote for a new deck, 400 square feet"
- "Fence repair for John Smith, about 50 linear feet"

Voice input: "{transcription}"

Determine the intent and extract relevant parameters."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                tools=[CRM_INTENT_TOOL],
                tool_choice={"type": "tool", "name": "detect_crm_intent"},
                messages=[{"role": "user", "content": prompt}]
            )

            # Extract tool use result
            for block in response.content:
                if block.type == "tool_use":
                    return block.input

            # Fallback if no tool use
            return {
                "is_crm_command": False,
                "intent": CrmIntent.NOT_CRM
            }

        except Exception as e:
            print(f"CRM intent detection error: {e}")
            return {
                "is_crm_command": False,
                "intent": CrmIntent.NOT_CRM
            }

    async def execute_command(
        self,
        db,
        contractor_id: str,
        intent_result: Dict[str, Any]
    ) -> CrmCommandResult:
        """
        Execute a CRM command based on detected intent.

        Args:
            db: Database session
            contractor_id: Contractor ID for scoping
            intent_result: Result from detect_intent()

        Returns:
            CrmCommandResult with success/failure and data
        """
        intent = intent_result.get("intent", "not_crm")
        customer_query = intent_result.get("customer_query")
        note_content = intent_result.get("note_content")
        tag_name = intent_result.get("tag_name")
        days_dormant = intent_result.get("days_dormant", 90)

        try:
            if intent == "search" or intent == "detail":
                return await self._handle_search(db, contractor_id, customer_query)
            elif intent == "stats":
                return await self._handle_stats(db, contractor_id, customer_query)
            elif intent == "add_note":
                return await self._handle_add_note(db, contractor_id, customer_query, note_content)
            elif intent == "add_tag":
                return await self._handle_add_tag(db, contractor_id, customer_query, tag_name)
            elif intent == "dormant":
                return await self._handle_dormant(db, contractor_id, days_dormant)
            elif intent == "top_customers":
                return await self._handle_top_customers(db, contractor_id)
            else:
                return CrmCommandResult(
                    intent=CrmIntent.NOT_CRM,
                    success=False,
                    message="This doesn't appear to be a CRM command. Try creating a quote instead."
                )

        except Exception as e:
            print(f"CRM command execution error: {e}")
            return CrmCommandResult(
                intent=CrmIntent(intent) if intent in [i.value for i in CrmIntent] else CrmIntent.NOT_CRM,
                success=False,
                message=f"Error executing command: {str(e)}"
            )

    async def _handle_search(
        self,
        db,
        contractor_id: str,
        query: Optional[str]
    ) -> CrmCommandResult:
        """Search for customers by name/phone/email."""
        if not query:
            return CrmCommandResult(
                intent=CrmIntent.SEARCH,
                success=False,
                message="I didn't catch the customer name. Who are you looking for?"
            )

        customers = await CustomerService.search_customers(
            db=db,
            contractor_id=contractor_id,
            query=query,
            limit=5
        )

        if not customers:
            return CrmCommandResult(
                intent=CrmIntent.SEARCH,
                success=True,
                message=f"No customers found matching '{query}'.",
                data={"customers": [], "query": query}
            )

        # Format response
        if len(customers) == 1:
            c = customers[0]
            message = f"Found {c.name}. {c.quote_count} quotes totaling ${c.total_quoted:,.0f}."
            if c.phone:
                message += f" Phone: {c.phone}."
        else:
            message = f"Found {len(customers)} customers matching '{query}':\n"
            for i, c in enumerate(customers, 1):
                message += f"{i}. {c.name} - {c.quote_count} quotes, ${c.total_quoted:,.0f}\n"

        return CrmCommandResult(
            intent=CrmIntent.SEARCH,
            success=True,
            message=message,
            data={
                "customers": [
                    {
                        "id": c.id,
                        "name": c.name,
                        "phone": c.phone,
                        "email": c.email,
                        "quote_count": c.quote_count,
                        "total_quoted": c.total_quoted,
                        "total_won": c.total_won,
                        "status": c.status
                    }
                    for c in customers
                ],
                "query": query
            }
        )

    async def _handle_stats(
        self,
        db,
        contractor_id: str,
        query: Optional[str]
    ) -> CrmCommandResult:
        """Get stats for a specific customer."""
        if not query:
            return CrmCommandResult(
                intent=CrmIntent.STATS,
                success=False,
                message="I didn't catch the customer name. Who do you want stats for?"
            )

        customers = await CustomerService.search_customers(
            db=db,
            contractor_id=contractor_id,
            query=query,
            limit=1
        )

        if not customers:
            return CrmCommandResult(
                intent=CrmIntent.STATS,
                success=False,
                message=f"No customer found matching '{query}'."
            )

        c = customers[0]
        win_rate = (c.total_won / c.total_quoted * 100) if c.total_quoted > 0 else 0

        message = f"{c.name}: {c.quote_count} quotes totaling ${c.total_quoted:,.0f}. "
        message += f"Won ${c.total_won:,.0f} ({win_rate:.0f}% win rate). "
        if c.last_quote_at:
            message += f"Last quote: {c.last_quote_at.strftime('%B %d, %Y')}."

        return CrmCommandResult(
            intent=CrmIntent.STATS,
            success=True,
            message=message,
            data={
                "customer": {
                    "id": c.id,
                    "name": c.name,
                    "quote_count": c.quote_count,
                    "total_quoted": c.total_quoted,
                    "total_won": c.total_won,
                    "win_rate": win_rate,
                    "first_quote_at": c.first_quote_at.isoformat() if c.first_quote_at else None,
                    "last_quote_at": c.last_quote_at.isoformat() if c.last_quote_at else None
                }
            }
        )

    async def _handle_add_note(
        self,
        db,
        contractor_id: str,
        query: Optional[str],
        note_content: Optional[str]
    ) -> CrmCommandResult:
        """Add a note to a customer."""
        if not query:
            return CrmCommandResult(
                intent=CrmIntent.ADD_NOTE,
                success=False,
                message="I didn't catch the customer name. Who should I add a note to?"
            )
        if not note_content:
            return CrmCommandResult(
                intent=CrmIntent.ADD_NOTE,
                success=False,
                message="What note should I add?"
            )

        customers = await CustomerService.search_customers(
            db=db,
            contractor_id=contractor_id,
            query=query,
            limit=1
        )

        if not customers:
            return CrmCommandResult(
                intent=CrmIntent.ADD_NOTE,
                success=False,
                message=f"No customer found matching '{query}'."
            )

        c = customers[0]
        await CustomerService.add_note(
            db=db,
            contractor_id=contractor_id,
            customer_id=c.id,
            note=note_content
        )
        await db.commit()

        return CrmCommandResult(
            intent=CrmIntent.ADD_NOTE,
            success=True,
            message=f"Added note to {c.name}: \"{note_content}\"",
            data={"customer_id": c.id, "customer_name": c.name, "note": note_content}
        )

    async def _handle_add_tag(
        self,
        db,
        contractor_id: str,
        query: Optional[str],
        tag_name: Optional[str]
    ) -> CrmCommandResult:
        """Add a tag to a customer."""
        if not query:
            return CrmCommandResult(
                intent=CrmIntent.ADD_TAG,
                success=False,
                message="I didn't catch the customer name. Who should I tag?"
            )
        if not tag_name:
            return CrmCommandResult(
                intent=CrmIntent.ADD_TAG,
                success=False,
                message="What tag should I add?"
            )

        customers = await CustomerService.search_customers(
            db=db,
            contractor_id=contractor_id,
            query=query,
            limit=1
        )

        if not customers:
            return CrmCommandResult(
                intent=CrmIntent.ADD_TAG,
                success=False,
                message=f"No customer found matching '{query}'."
            )

        c = customers[0]
        await CustomerService.add_tag(
            db=db,
            contractor_id=contractor_id,
            customer_id=c.id,
            tag=tag_name
        )
        await db.commit()

        return CrmCommandResult(
            intent=CrmIntent.ADD_TAG,
            success=True,
            message=f"Tagged {c.name} as '{tag_name}'.",
            data={"customer_id": c.id, "customer_name": c.name, "tag": tag_name}
        )

    async def _handle_dormant(
        self,
        db,
        contractor_id: str,
        days: int = 90
    ) -> CrmCommandResult:
        """Get dormant customers."""
        customers = await CustomerService.get_dormant_customers(
            db=db,
            contractor_id=contractor_id,
            days=days,
            limit=10
        )

        if not customers:
            return CrmCommandResult(
                intent=CrmIntent.DORMANT,
                success=True,
                message=f"Great news! No customers have been dormant for {days}+ days.",
                data={"customers": [], "days": days}
            )

        message = f"Found {len(customers)} customers with no quotes in {days}+ days:\n"
        for c in customers[:5]:
            days_since = (datetime.utcnow() - c.last_quote_at).days if c.last_quote_at else 999
            message += f"- {c.name}: {days_since} days since last quote (${c.total_quoted:,.0f} lifetime)\n"

        return CrmCommandResult(
            intent=CrmIntent.DORMANT,
            success=True,
            message=message,
            data={
                "customers": [
                    {
                        "id": c.id,
                        "name": c.name,
                        "last_quote_at": c.last_quote_at.isoformat() if c.last_quote_at else None,
                        "total_quoted": c.total_quoted
                    }
                    for c in customers
                ],
                "days": days
            }
        )

    async def _handle_top_customers(
        self,
        db,
        contractor_id: str
    ) -> CrmCommandResult:
        """Get top customers by revenue."""
        customers = await CustomerService.get_top_customers(
            db=db,
            contractor_id=contractor_id,
            by="total_quoted",
            limit=5
        )

        if not customers:
            return CrmCommandResult(
                intent=CrmIntent.TOP_CUSTOMERS,
                success=True,
                message="No customers found yet. Create some quotes to build your customer list!",
                data={"customers": []}
            )

        message = "Your top customers by total quoted:\n"
        for i, c in enumerate(customers, 1):
            message += f"{i}. {c.name}: ${c.total_quoted:,.0f} ({c.quote_count} quotes)\n"

        return CrmCommandResult(
            intent=CrmIntent.TOP_CUSTOMERS,
            success=True,
            message=message,
            data={
                "customers": [
                    {
                        "id": c.id,
                        "name": c.name,
                        "total_quoted": c.total_quoted,
                        "quote_count": c.quote_count
                    }
                    for c in customers
                ]
            }
        )


# Import datetime at module level
from datetime import datetime

# Singleton instance
crm_voice_service = CrmVoiceService()
