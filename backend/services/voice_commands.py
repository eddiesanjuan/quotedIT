"""
Enhanced Voice Command Service for Quoted (INNOV-4).

Expands voice commands beyond CRM to include:
- Quote management: "Duplicate last quote", "Mark quote as won"
- Task management: "Remind me to call Sarah tomorrow", "Show today's tasks"
- Follow-up control: "Pause follow-ups for Smith", "What needs follow-up?"
- Dashboard queries: "What's my win rate?", "How many quotes this week?"

Design principle: Contractors are driving/working - every command should be
hands-free friendly with clear spoken confirmations.
"""

import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from enum import Enum
from dataclasses import dataclass

import anthropic

from ..config import settings
from .logging import get_logger

logger = get_logger("quoted.voice_commands")


class VoiceCommandType(str, Enum):
    """Types of voice commands."""
    # CRM commands (existing)
    CRM_SEARCH = "crm_search"
    CRM_DETAIL = "crm_detail"
    CRM_STATS = "crm_stats"
    CRM_ADD_NOTE = "crm_add_note"
    CRM_ADD_TAG = "crm_add_tag"
    CRM_DORMANT = "crm_dormant"
    CRM_TOP_CUSTOMERS = "crm_top_customers"

    # Quote commands (INNOV-4 expansion)
    QUOTE_DUPLICATE = "quote_duplicate"
    QUOTE_STATUS = "quote_status"
    QUOTE_WIN = "quote_win"
    QUOTE_LOSS = "quote_loss"
    QUOTE_RECENT = "quote_recent"
    QUOTE_PENDING = "quote_pending"

    # Task commands (INNOV-4 expansion)
    TASK_CREATE = "task_create"
    TASK_TODAY = "task_today"
    TASK_COMPLETE = "task_complete"
    TASK_SNOOZE = "task_snooze"

    # Follow-up commands (INNOV-4 expansion)
    FOLLOWUP_PAUSE = "followup_pause"
    FOLLOWUP_RESUME = "followup_resume"
    FOLLOWUP_STATUS = "followup_status"
    FOLLOWUP_DUE = "followup_due"

    # Dashboard commands (INNOV-4 expansion)
    DASHBOARD_WIN_RATE = "dashboard_win_rate"
    DASHBOARD_QUOTES_SENT = "dashboard_quotes_sent"
    DASHBOARD_REVENUE = "dashboard_revenue"
    DASHBOARD_COMPARISON = "dashboard_comparison"

    # Quote creation (pass to quote generation)
    CREATE_QUOTE = "create_quote"

    # Unknown
    UNKNOWN = "unknown"


@dataclass
class VoiceCommandResult:
    """Result of a voice command execution."""
    command_type: VoiceCommandType
    success: bool
    spoken_response: str  # What to say back to user
    data: Optional[Dict[str, Any]] = None
    action_taken: Optional[str] = None


# Tool definition for Claude command detection
VOICE_COMMAND_TOOL = {
    "name": "detect_voice_command",
    "description": "Detect voice command type and extract parameters from transcription.",
    "input_schema": {
        "type": "object",
        "properties": {
            "command_type": {
                "type": "string",
                "enum": [t.value for t in VoiceCommandType],
                "description": "The detected command type"
            },
            "customer_name": {
                "type": ["string", "null"],
                "description": "Customer name if mentioned"
            },
            "quote_reference": {
                "type": ["string", "null"],
                "description": "Quote reference (last, recent, customer name, job type)"
            },
            "task_title": {
                "type": ["string", "null"],
                "description": "Task title or description"
            },
            "task_due": {
                "type": ["string", "null"],
                "description": "When task is due (today, tomorrow, next week, specific date)"
            },
            "time_period": {
                "type": ["string", "null"],
                "description": "Time period for queries (this week, last month, this year)"
            },
            "note_content": {
                "type": ["string", "null"],
                "description": "Note content for add_note"
            },
            "tag_name": {
                "type": ["string", "null"],
                "description": "Tag name for add_tag"
            },
            "loss_reason": {
                "type": ["string", "null"],
                "description": "Reason for quote loss if provided"
            },
            "is_quote_creation": {
                "type": "boolean",
                "description": "True if this is a request to create a new quote, not manage existing"
            }
        },
        "required": ["command_type", "is_quote_creation"]
    }
}


class VoiceCommandService:
    """
    Enhanced voice command service supporting all command types.

    Key design: Every response should be speakable.
    """

    COMMAND_PATTERNS = {
        # Quote patterns
        "duplicate": ["duplicate", "copy", "clone", "make another"],
        "quote_status": ["status of", "what happened", "where is"],
        "mark_won": ["won", "got it", "accepted", "customer accepted"],
        "mark_lost": ["lost", "didn't get", "rejected", "went with someone else"],
        "recent_quotes": ["recent quotes", "latest quotes", "last few quotes"],
        "pending_quotes": ["pending", "waiting on", "outstanding"],

        # Task patterns
        "task_create": ["remind me", "task", "todo", "don't forget"],
        "task_today": ["today's tasks", "what's on", "my tasks", "to do today"],
        "task_complete": ["done", "finished", "completed", "mark complete"],
        "task_snooze": ["snooze", "delay", "push back", "later"],

        # Follow-up patterns
        "followup_pause": ["pause follow", "stop follow", "hold off"],
        "followup_resume": ["resume follow", "start follow", "continue follow"],
        "followup_status": ["follow up status", "what follow ups"],
        "followup_due": ["needs follow up", "due for follow up"],

        # Dashboard patterns
        "win_rate": ["win rate", "how many won", "conversion"],
        "quotes_sent": ["how many quotes", "quotes sent", "quotes this"],
        "revenue": ["revenue", "total sales", "how much made", "earnings"],
        "comparison": ["compared to", "versus", "vs last"],
    }

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.model = "claude-sonnet-4-20250514"

    def _quick_pattern_match(self, text: str) -> Optional[str]:
        """Quick pattern matching for common commands."""
        text_lower = text.lower()
        for pattern_type, keywords in self.COMMAND_PATTERNS.items():
            if any(kw in text_lower for kw in keywords):
                return pattern_type
        return None

    async def detect_command(self, transcription: str) -> Dict[str, Any]:
        """
        Use Claude to detect voice command and extract parameters.
        """
        prompt = f"""You are a voice command parser for a contractor quoting app. Analyze this voice input and determine what the user wants to do.

COMMAND CATEGORIES:

1. QUOTE CREATION (is_quote_creation=true):
   - Requests to generate a new quote: "I need a quote for a deck", "Quote for painting"
   - These go to the quote generator, not handled here

2. QUOTE MANAGEMENT (is_quote_creation=false):
   - quote_duplicate: "Duplicate last quote", "Copy the Johnson quote"
   - quote_status: "What's the status on the deck quote?", "Did Smith accept?"
   - quote_win: "I got the Johnson job", "Mark that quote as won"
   - quote_loss: "Lost the deck job to a competitor", "Didn't get the Smith quote"
   - quote_recent: "Show my recent quotes", "Last 5 quotes"
   - quote_pending: "What quotes are still pending?", "Outstanding quotes"

3. TASK MANAGEMENT:
   - task_create: "Remind me to call Johnson tomorrow", "Task: follow up with Sarah next week"
   - task_today: "What are my tasks today?", "What's on my list?"
   - task_complete: "I finished the site visit", "Mark call to Johnson complete"
   - task_snooze: "Snooze the reminder until tomorrow"

4. FOLLOW-UP CONTROL:
   - followup_pause: "Pause follow-ups for the Smith quote"
   - followup_resume: "Resume follow-ups for deck job"
   - followup_status: "What's the follow-up status on pending quotes?"
   - followup_due: "Which quotes need follow-up today?"

5. DASHBOARD QUERIES:
   - dashboard_win_rate: "What's my win rate?", "How many quotes did I close?"
   - dashboard_quotes_sent: "How many quotes this month?", "Quotes sent last week?"
   - dashboard_revenue: "How much did I quote this year?", "Total revenue from won quotes"
   - dashboard_comparison: "How does this month compare to last?", "Year over year?"

6. CRM COMMANDS:
   - crm_search: "Show me John Smith", "Find customer"
   - crm_detail: "History with Johnson Electric"
   - crm_stats: "How much have I quoted the Hendersons?"
   - crm_add_note: "Add note to Mike Wilson: prefers mornings"
   - crm_add_tag: "Tag Sarah's Bakery as VIP"
   - crm_dormant: "Customers I haven't quoted in 6 months"
   - crm_top_customers: "Who are my best customers?"

Voice input: "{transcription}"

Determine command type and extract parameters."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                tools=[VOICE_COMMAND_TOOL],
                tool_choice={"type": "tool", "name": "detect_voice_command"},
                messages=[{"role": "user", "content": prompt}]
            )

            for block in response.content:
                if block.type == "tool_use":
                    return block.input

            return {
                "command_type": VoiceCommandType.UNKNOWN.value,
                "is_quote_creation": False
            }

        except Exception as e:
            logger.error(f"Voice command detection error: {e}")
            return {
                "command_type": VoiceCommandType.UNKNOWN.value,
                "is_quote_creation": False
            }

    async def execute(
        self,
        db,
        contractor_id: str,
        user_id: str,
        command_data: Dict[str, Any]
    ) -> VoiceCommandResult:
        """Execute a voice command."""
        command_type = VoiceCommandType(command_data.get("command_type", "unknown"))

        try:
            # Route to appropriate handler
            if command_type.value.startswith("crm_"):
                return await self._handle_crm_command(db, contractor_id, command_type, command_data)
            elif command_type.value.startswith("quote_"):
                return await self._handle_quote_command(db, contractor_id, command_type, command_data)
            elif command_type.value.startswith("task_"):
                return await self._handle_task_command(db, contractor_id, command_type, command_data)
            elif command_type.value.startswith("followup_"):
                return await self._handle_followup_command(db, contractor_id, command_type, command_data)
            elif command_type.value.startswith("dashboard_"):
                return await self._handle_dashboard_command(db, contractor_id, command_type, command_data)
            else:
                return VoiceCommandResult(
                    command_type=command_type,
                    success=False,
                    spoken_response="I didn't understand that command. Try saying 'show my tasks' or 'recent quotes'."
                )

        except Exception as e:
            logger.error(f"Voice command execution error: {e}")
            return VoiceCommandResult(
                command_type=command_type,
                success=False,
                spoken_response="Sorry, something went wrong. Please try again."
            )

    async def _handle_crm_command(
        self, db, contractor_id: str, command_type: VoiceCommandType, data: Dict
    ) -> VoiceCommandResult:
        """Handle CRM-related voice commands."""
        from .crm_voice import crm_voice_service

        # Map to CRM intent
        intent_map = {
            VoiceCommandType.CRM_SEARCH: "search",
            VoiceCommandType.CRM_DETAIL: "detail",
            VoiceCommandType.CRM_STATS: "stats",
            VoiceCommandType.CRM_ADD_NOTE: "add_note",
            VoiceCommandType.CRM_ADD_TAG: "add_tag",
            VoiceCommandType.CRM_DORMANT: "dormant",
            VoiceCommandType.CRM_TOP_CUSTOMERS: "top_customers",
        }

        intent_result = {
            "intent": intent_map.get(command_type, "search"),
            "customer_query": data.get("customer_name"),
            "note_content": data.get("note_content"),
            "tag_name": data.get("tag_name"),
        }

        result = await crm_voice_service.execute_command(db, contractor_id, intent_result)

        return VoiceCommandResult(
            command_type=command_type,
            success=result.success,
            spoken_response=result.message,
            data=result.data
        )

    async def _handle_quote_command(
        self, db, contractor_id: str, command_type: VoiceCommandType, data: Dict
    ) -> VoiceCommandResult:
        """Handle quote management voice commands."""
        from ..models.database import Quote
        from sqlalchemy import select, desc

        if command_type == VoiceCommandType.QUOTE_RECENT:
            result = await db.execute(
                select(Quote)
                .where(Quote.contractor_id == contractor_id)
                .order_by(desc(Quote.created_at))
                .limit(5)
            )
            quotes = result.scalars().all()

            if not quotes:
                return VoiceCommandResult(
                    command_type=command_type,
                    success=True,
                    spoken_response="You don't have any quotes yet."
                )

            spoken = f"Your last {len(quotes)} quotes: "
            for q in quotes:
                status = q.status or "draft"
                spoken += f"{q.customer_name or 'Unknown'}, {q.job_type or 'project'}, ${q.total:,.0f}, {status}. "

            return VoiceCommandResult(
                command_type=command_type,
                success=True,
                spoken_response=spoken,
                data={"quotes": [{"id": q.id, "customer": q.customer_name, "total": q.total, "status": q.status} for q in quotes]}
            )

        elif command_type == VoiceCommandType.QUOTE_PENDING:
            result = await db.execute(
                select(Quote)
                .where(Quote.contractor_id == contractor_id, Quote.status.in_(["sent", "viewed"]))
                .order_by(desc(Quote.sent_at))
                .limit(10)
            )
            quotes = result.scalars().all()

            if not quotes:
                return VoiceCommandResult(
                    command_type=command_type,
                    success=True,
                    spoken_response="No pending quotes waiting for response."
                )

            spoken = f"You have {len(quotes)} pending quotes: "
            for q in quotes[:5]:
                days = (datetime.utcnow() - q.sent_at).days if q.sent_at else 0
                spoken += f"{q.customer_name or 'Unknown'}, ${q.total:,.0f}, sent {days} days ago. "

            return VoiceCommandResult(
                command_type=command_type,
                success=True,
                spoken_response=spoken,
                data={"pending_count": len(quotes)}
            )

        elif command_type == VoiceCommandType.QUOTE_WIN:
            # Find quote to mark as won
            quote_ref = data.get("quote_reference") or data.get("customer_name")
            quote = await self._find_quote(db, contractor_id, quote_ref)

            if not quote:
                return VoiceCommandResult(
                    command_type=command_type,
                    success=False,
                    spoken_response="I couldn't find that quote. Which quote did you win?"
                )

            # Mark as won
            quote.status = "won"
            quote.outcome = "won"
            await db.commit()

            return VoiceCommandResult(
                command_type=command_type,
                success=True,
                spoken_response=f"Great! Marked the {quote.customer_name} quote as won. ${quote.total:,.0f} - nice work!",
                action_taken=f"Quote {quote.id} marked as won"
            )

        elif command_type == VoiceCommandType.QUOTE_LOSS:
            quote_ref = data.get("quote_reference") or data.get("customer_name")
            quote = await self._find_quote(db, contractor_id, quote_ref)

            if not quote:
                return VoiceCommandResult(
                    command_type=command_type,
                    success=False,
                    spoken_response="I couldn't find that quote. Which quote did you lose?"
                )

            # Mark as lost
            quote.status = "lost"
            quote.outcome = "lost"
            quote.outcome_notes = data.get("loss_reason")
            await db.commit()

            return VoiceCommandResult(
                command_type=command_type,
                success=True,
                spoken_response=f"Marked the {quote.customer_name} quote as lost. On to the next one!",
                action_taken=f"Quote {quote.id} marked as lost"
            )

        elif command_type == VoiceCommandType.QUOTE_DUPLICATE:
            quote_ref = data.get("quote_reference") or data.get("customer_name")
            quote = await self._find_quote(db, contractor_id, quote_ref)

            if not quote:
                return VoiceCommandResult(
                    command_type=command_type,
                    success=False,
                    spoken_response="I couldn't find that quote to duplicate."
                )

            # Create duplicate
            new_quote = Quote(
                contractor_id=contractor_id,
                customer_name=quote.customer_name,
                customer_email=quote.customer_email,
                customer_phone=quote.customer_phone,
                customer_address=quote.customer_address,
                job_type=quote.job_type,
                job_description=quote.job_description,
                line_items=quote.line_items,
                subtotal=quote.subtotal,
                total=quote.total,
                estimated_days=quote.estimated_days,
                status="draft",
                duplicate_source_quote_id=quote.id,
            )
            db.add(new_quote)
            await db.commit()
            await db.refresh(new_quote)

            return VoiceCommandResult(
                command_type=command_type,
                success=True,
                spoken_response=f"Duplicated the {quote.customer_name} quote. It's ready in your drafts.",
                action_taken=f"Created quote {new_quote.id}",
                data={"new_quote_id": new_quote.id}
            )

        return VoiceCommandResult(
            command_type=command_type,
            success=False,
            spoken_response="I'm not sure what to do with that quote command."
        )

    async def _handle_task_command(
        self, db, contractor_id: str, command_type: VoiceCommandType, data: Dict
    ) -> VoiceCommandResult:
        """Handle task management voice commands."""
        from ..models.database import Task
        from sqlalchemy import select, and_

        if command_type == VoiceCommandType.TASK_TODAY:
            today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            tomorrow = today + timedelta(days=1)

            result = await db.execute(
                select(Task)
                .where(
                    Task.contractor_id == contractor_id,
                    Task.status == "pending",
                    Task.due_date >= today,
                    Task.due_date < tomorrow
                )
                .order_by(Task.priority.desc())
            )
            tasks = result.scalars().all()

            if not tasks:
                return VoiceCommandResult(
                    command_type=command_type,
                    success=True,
                    spoken_response="No tasks scheduled for today. Enjoy!"
                )

            spoken = f"You have {len(tasks)} tasks today: "
            for t in tasks[:5]:
                spoken += f"{t.title}. "

            return VoiceCommandResult(
                command_type=command_type,
                success=True,
                spoken_response=spoken,
                data={"task_count": len(tasks)}
            )

        elif command_type == VoiceCommandType.TASK_CREATE:
            title = data.get("task_title") or "Follow up"
            due_str = data.get("task_due") or "tomorrow"

            # Parse due date
            due_date = self._parse_due_date(due_str)

            task = Task(
                contractor_id=contractor_id,
                title=title,
                due_date=due_date,
                priority="normal",
                task_type="reminder",
                status="pending",
            )
            db.add(task)
            await db.commit()

            due_spoken = "today" if due_date.date() == datetime.utcnow().date() else due_str

            return VoiceCommandResult(
                command_type=command_type,
                success=True,
                spoken_response=f"Got it! I'll remind you to {title} {due_spoken}.",
                action_taken=f"Created task: {title}"
            )

        elif command_type == VoiceCommandType.TASK_COMPLETE:
            # Find most recent pending task matching description
            result = await db.execute(
                select(Task)
                .where(Task.contractor_id == contractor_id, Task.status == "pending")
                .order_by(Task.due_date)
                .limit(1)
            )
            task = result.scalar_one_or_none()

            if not task:
                return VoiceCommandResult(
                    command_type=command_type,
                    success=False,
                    spoken_response="No pending tasks to complete."
                )

            task.status = "completed"
            task.completed_at = datetime.utcnow()
            await db.commit()

            return VoiceCommandResult(
                command_type=command_type,
                success=True,
                spoken_response=f"Marked '{task.title}' as complete. Nice work!",
                action_taken=f"Completed task: {task.title}"
            )

        return VoiceCommandResult(
            command_type=command_type,
            success=False,
            spoken_response="I'm not sure what to do with that task command."
        )

    async def _handle_followup_command(
        self, db, contractor_id: str, command_type: VoiceCommandType, data: Dict
    ) -> VoiceCommandResult:
        """Handle follow-up voice commands."""
        from .follow_up import FollowUpService
        from ..models.database import FollowUpSequence
        from sqlalchemy import select

        if command_type == VoiceCommandType.FOLLOWUP_DUE:
            result = await db.execute(
                select(FollowUpSequence)
                .where(
                    FollowUpSequence.contractor_id == contractor_id,
                    FollowUpSequence.status == "active",
                    FollowUpSequence.next_follow_up_at <= datetime.utcnow() + timedelta(days=1)
                )
            )
            due_sequences = result.scalars().all()

            if not due_sequences:
                return VoiceCommandResult(
                    command_type=command_type,
                    success=True,
                    spoken_response="No follow-ups due in the next 24 hours."
                )

            return VoiceCommandResult(
                command_type=command_type,
                success=True,
                spoken_response=f"You have {len(due_sequences)} quotes due for follow-up soon.",
                data={"due_count": len(due_sequences)}
            )

        elif command_type == VoiceCommandType.FOLLOWUP_PAUSE:
            customer = data.get("customer_name") or data.get("quote_reference")
            quote = await self._find_quote(db, contractor_id, customer)

            if not quote:
                return VoiceCommandResult(
                    command_type=command_type,
                    success=False,
                    spoken_response="I couldn't find that quote. Which quote should I pause follow-ups for?"
                )

            success = await FollowUpService.pause_sequence(db, quote.id)

            if success:
                return VoiceCommandResult(
                    command_type=command_type,
                    success=True,
                    spoken_response=f"Paused follow-ups for the {quote.customer_name} quote.",
                    action_taken=f"Paused follow-up for quote {quote.id}"
                )
            else:
                return VoiceCommandResult(
                    command_type=command_type,
                    success=False,
                    spoken_response="No active follow-up sequence to pause for that quote."
                )

        elif command_type == VoiceCommandType.FOLLOWUP_RESUME:
            customer = data.get("customer_name") or data.get("quote_reference")
            quote = await self._find_quote(db, contractor_id, customer)

            if not quote:
                return VoiceCommandResult(
                    command_type=command_type,
                    success=False,
                    spoken_response="I couldn't find that quote."
                )

            success = await FollowUpService.resume_sequence(db, quote.id)

            if success:
                return VoiceCommandResult(
                    command_type=command_type,
                    success=True,
                    spoken_response=f"Resumed follow-ups for the {quote.customer_name} quote.",
                    action_taken=f"Resumed follow-up for quote {quote.id}"
                )
            else:
                return VoiceCommandResult(
                    command_type=command_type,
                    success=False,
                    spoken_response="No paused follow-up sequence to resume."
                )

        return VoiceCommandResult(
            command_type=command_type,
            success=False,
            spoken_response="I'm not sure what to do with that follow-up command."
        )

    async def _handle_dashboard_command(
        self, db, contractor_id: str, command_type: VoiceCommandType, data: Dict
    ) -> VoiceCommandResult:
        """Handle dashboard query voice commands."""
        from ..models.database import Quote
        from sqlalchemy import select, func, Integer

        time_period = data.get("time_period", "this month")
        start_date, end_date = self._parse_time_period(time_period)

        if command_type == VoiceCommandType.DASHBOARD_WIN_RATE:
            # Get quotes in period
            result = await db.execute(
                select(
                    func.count(Quote.id).label("total"),
                    func.sum(func.cast(Quote.outcome == "won", Integer)).label("won")
                )
                .where(
                    Quote.contractor_id == contractor_id,
                    Quote.created_at >= start_date,
                    Quote.created_at < end_date,
                    Quote.outcome.isnot(None)
                )
            )
            row = result.first()
            total = row.total or 0
            won = row.won or 0
            win_rate = (won / total * 100) if total > 0 else 0

            return VoiceCommandResult(
                command_type=command_type,
                success=True,
                spoken_response=f"Your win rate {time_period}: {win_rate:.0f}%. You won {won} out of {total} quotes.",
                data={"win_rate": win_rate, "won": won, "total": total}
            )

        elif command_type == VoiceCommandType.DASHBOARD_QUOTES_SENT:
            result = await db.execute(
                select(func.count(Quote.id))
                .where(
                    Quote.contractor_id == contractor_id,
                    Quote.sent_at >= start_date,
                    Quote.sent_at < end_date
                )
            )
            count = result.scalar() or 0

            return VoiceCommandResult(
                command_type=command_type,
                success=True,
                spoken_response=f"You sent {count} quotes {time_period}.",
                data={"quotes_sent": count}
            )

        elif command_type == VoiceCommandType.DASHBOARD_REVENUE:
            result = await db.execute(
                select(func.sum(Quote.total))
                .where(
                    Quote.contractor_id == contractor_id,
                    Quote.outcome == "won",
                    Quote.accepted_at >= start_date,
                    Quote.accepted_at < end_date
                )
            )
            revenue = result.scalar() or 0

            return VoiceCommandResult(
                command_type=command_type,
                success=True,
                spoken_response=f"Won quotes {time_period} totaled ${revenue:,.0f}.",
                data={"revenue": revenue}
            )

        return VoiceCommandResult(
            command_type=command_type,
            success=False,
            spoken_response="I'm not sure what dashboard info you're looking for."
        )

    async def _find_quote(self, db, contractor_id: str, reference: Optional[str]):
        """Find a quote by reference (customer name, 'last', job type)."""
        from ..models.database import Quote
        from sqlalchemy import select, desc, or_

        if not reference:
            # Get most recent quote
            result = await db.execute(
                select(Quote)
                .where(Quote.contractor_id == contractor_id)
                .order_by(desc(Quote.created_at))
                .limit(1)
            )
            return result.scalar_one_or_none()

        ref_lower = reference.lower()

        if ref_lower in ["last", "latest", "most recent"]:
            result = await db.execute(
                select(Quote)
                .where(Quote.contractor_id == contractor_id)
                .order_by(desc(Quote.created_at))
                .limit(1)
            )
            return result.scalar_one_or_none()

        # Search by customer name or job type
        result = await db.execute(
            select(Quote)
            .where(
                Quote.contractor_id == contractor_id,
                or_(
                    Quote.customer_name.ilike(f"%{reference}%"),
                    Quote.job_type.ilike(f"%{reference}%")
                )
            )
            .order_by(desc(Quote.created_at))
            .limit(1)
        )
        return result.scalar_one_or_none()

    def _parse_due_date(self, due_str: str) -> datetime:
        """Parse natural language due date."""
        now = datetime.utcnow()
        due_lower = due_str.lower()

        if "today" in due_lower:
            return now.replace(hour=17, minute=0, second=0, microsecond=0)
        elif "tomorrow" in due_lower:
            return (now + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
        elif "next week" in due_lower:
            return (now + timedelta(days=7)).replace(hour=9, minute=0, second=0, microsecond=0)
        elif "friday" in due_lower:
            days_until_friday = (4 - now.weekday()) % 7
            if days_until_friday == 0:
                days_until_friday = 7
            return (now + timedelta(days=days_until_friday)).replace(hour=9, minute=0, second=0, microsecond=0)
        else:
            # Default to tomorrow
            return (now + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)

    def _parse_time_period(self, period: str) -> tuple:
        """Parse natural language time period."""
        now = datetime.utcnow()
        period_lower = period.lower()

        if "this week" in period_lower:
            start = now - timedelta(days=now.weekday())
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=7)
        elif "last week" in period_lower:
            start = now - timedelta(days=now.weekday() + 7)
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=7)
        elif "this month" in period_lower:
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if now.month == 12:
                end = start.replace(year=now.year + 1, month=1)
            else:
                end = start.replace(month=now.month + 1)
        elif "last month" in period_lower:
            if now.month == 1:
                start = now.replace(year=now.year - 1, month=12, day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                start = now.replace(month=now.month - 1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif "this year" in period_lower:
            start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end = start.replace(year=now.year + 1)
        else:
            # Default to this month
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if now.month == 12:
                end = start.replace(year=now.year + 1, month=1)
            else:
                end = start.replace(month=now.month + 1)

        return start, end


# Singleton instance
voice_command_service = VoiceCommandService()
