# Quoted Enhancement Implementation Prompt

Paste this prompt into a fresh Claude Code session.

---

<context>
You are implementing enhancements to Quoted, a voice-to-quote application for contractors located at `/Users/eddiesanjuan/Personal_Assistant/Eddie_Personal_Assistant/quoted`.

The application uses:
- FastAPI backend (Python)
- Anthropic Claude Sonnet for AI
- OpenAI Whisper for transcription
- SQLAlchemy + SQLite (dev) / PostgreSQL (prod)
- Vanilla HTML/CSS/JS frontend

Current architecture flow:
```
Voice → Whisper transcription → Claude (single call) → JSON extraction (regex) → DB → User
```

You are enhancing this to:
```
Voice → Whisper → Multi-Agent Generation → Structured Outputs → Confidence Sampling → User Feedback Loop
```
</context>

<task>
Implement the following enhancements to Quoted. Read all relevant files before making changes. Follow existing code patterns and style.

## Enhancement 1: Structured Outputs

**Goal**: Replace brittle regex JSON extraction with Claude's native structured outputs.

**Files to modify**:
- `backend/services/quote_generator.py`
- `backend/prompts/quote_generation.py`

**Implementation**:

1. Define a Pydantic schema for quote responses:
```python
from pydantic import BaseModel, Field
from typing import List, Optional

class LineItem(BaseModel):
    name: str
    description: Optional[str] = None
    amount: float = Field(ge=0)
    quantity: Optional[float] = Field(default=1, ge=0)
    unit: Optional[str] = None

class QuoteOutput(BaseModel):
    job_type: str
    job_description: str
    customer_name: Optional[str] = None
    customer_address: Optional[str] = None
    customer_phone: Optional[str] = None
    line_items: List[LineItem]
    subtotal: float = Field(ge=0)
    estimated_days: Optional[int] = Field(default=None, ge=1)
    estimated_crew_size: Optional[int] = Field(default=None, ge=1)
    confidence: str = Field(pattern="^(high|medium|low)$")
    assumptions: List[str] = []
    questions: List[str] = []
```

2. Modify `QuoteGenerationService.generate_quote()` to use tool calling for structured output:
   - Create a tool definition that matches the Pydantic schema
   - Force tool use with `tool_choice={"type": "tool", "name": "generate_quote"}`
   - Parse the tool use response directly (no regex needed)

3. Add validation layer using the Pydantic model after extraction.

4. Remove all regex-based JSON extraction code.

**Success criteria**: Quote generation always returns valid JSON matching the schema. No parsing failures.

---

## Enhancement 2: Multi-Agent Quote Generation

**Goal**: Split single LLM call into specialized agents for better accuracy.

**Files to create**:
- `backend/services/agents/__init__.py`
- `backend/services/agents/materials_agent.py`
- `backend/services/agents/labor_agent.py`
- `backend/services/agents/risk_agent.py`
- `backend/services/agents/aggregator.py`

**Files to modify**:
- `backend/services/quote_generator.py`
- `backend/services/__init__.py`

**Implementation**:

1. Create `MaterialsAgent`:
   - Input: transcription, contractor pricing_knowledge
   - Output: list of material line items with costs
   - Uses contractor's material markup percentage
   - Returns structured output via tool calling

2. Create `LaborAgent`:
   - Input: transcription, job complexity indicators, contractor rates
   - Output: labor hours estimate, crew size, timeline
   - Returns structured output via tool calling

3. Create `RiskAgent`:
   - Input: transcription, job type, contractor history
   - Output: risk factors, recommended contingency percentage, confidence assessment
   - Returns structured output via tool calling

4. Create `QuoteAggregator`:
   - Input: outputs from all three agents
   - Validates arithmetic (line items sum to subtotal)
   - Combines into final QuoteOutput
   - Resolves conflicts between agents

5. Modify `QuoteGenerationService.generate_quote()`:
   - Run all three agents in parallel using `asyncio.gather()`
   - Pass results to aggregator
   - For simple quotes (estimated < $2000), use single-agent path for speed
   - For complex quotes, use multi-agent path

**Success criteria**: Complex quotes use multi-agent generation. Agents run in parallel. Final output matches QuoteOutput schema.

---

## Enhancement 3: Confidence Sampling

**Goal**: Estimate confidence using multiple methods instead of LLM self-reporting.

**Files to modify**:
- `backend/services/quote_generator.py`
- `backend/models/database.py` (add confidence_details column)
- `backend/api/quotes.py`

**Implementation**:

1. Add `confidence_details` JSON column to Quote model:
```python
confidence_details = Column(JSON)
# Stores: {sampling_variance, retrieval_score, final_score, level}
```

2. Create confidence estimation function:
```python
async def estimate_confidence(
    transcription: str,
    quotes: List[QuoteOutput],  # 3 samples
    correction_examples: List[dict]
) -> dict:
    # Calculate price variance across samples
    prices = [q.subtotal for q in quotes]
    mean_price = statistics.mean(prices)
    std_dev = statistics.stdev(prices) if len(prices) > 1 else 0
    coefficient_of_variation = std_dev / mean_price if mean_price > 0 else 1.0

    # Sampling score: low variance = high confidence
    sampling_score = 1.0 if coefficient_of_variation < 0.10 else \
                     0.7 if coefficient_of_variation < 0.15 else \
                     0.4 if coefficient_of_variation < 0.25 else 0.1

    # Retrieval score: more correction examples = higher confidence
    retrieval_score = min(1.0, len(correction_examples) / 5)  # Max out at 5 examples

    # Combined score (weighted)
    final_score = sampling_score * 0.7 + retrieval_score * 0.3

    return {
        "sampling_variance": coefficient_of_variation,
        "retrieval_score": retrieval_score,
        "final_score": final_score,
        "level": "high" if final_score > 0.7 else "medium" if final_score > 0.4 else "low"
    }
```

3. Modify quote generation to:
   - Generate 3 quotes at temperature=0.7 (in parallel)
   - Use median quote as the final output
   - Calculate confidence using the sampling method
   - Store confidence_details in the quote record

4. Update QuoteResponse model to include confidence_details.

**Success criteria**: Every quote has confidence_details stored. Confidence level correlates with actual accuracy over time.

---

## Enhancement 4: User Feedback System

**Goal**: Allow users to provide explicit feedback on quotes without editing them.

**Files to create**:
- `backend/api/feedback.py`

**Files to modify**:
- `backend/models/database.py` (add QuoteFeedback model)
- `backend/services/database.py` (add feedback methods)
- `backend/services/learning.py` (process feedback)
- `backend/main.py` (register router)
- `frontend/index.html` (add feedback UI)

**Implementation**:

1. Create QuoteFeedback database model:
```python
class QuoteFeedback(Base):
    """Explicit user feedback on quote accuracy."""
    __tablename__ = "quote_feedback"

    id = Column(String, primary_key=True, default=generate_uuid)
    quote_id = Column(String, ForeignKey("quotes.id"), nullable=False)
    contractor_id = Column(String, ForeignKey("contractors.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Overall rating
    accuracy_rating = Column(Integer)  # 1-5 stars

    # Aspect ratings (1-5 each, nullable)
    materials_accuracy = Column(Integer)
    labor_accuracy = Column(Integer)
    timeline_accuracy = Column(Integer)

    # What actually happened (optional)
    actual_total = Column(Float)
    actual_days = Column(Integer)

    # Qualitative feedback
    feedback_text = Column(Text)

    # Was quote accepted by customer?
    quote_accepted = Column(Boolean)

    # Specific issues identified
    issues = Column(JSON)  # ["materials_too_high", "missing_line_item", etc.]
```

2. Create feedback API endpoints in `backend/api/feedback.py`:
```python
router = APIRouter()

class FeedbackRequest(BaseModel):
    accuracy_rating: int = Field(ge=1, le=5)
    materials_accuracy: Optional[int] = Field(default=None, ge=1, le=5)
    labor_accuracy: Optional[int] = Field(default=None, ge=1, le=5)
    timeline_accuracy: Optional[int] = Field(default=None, ge=1, le=5)
    actual_total: Optional[float] = None
    actual_days: Optional[int] = None
    feedback_text: Optional[str] = None
    quote_accepted: Optional[bool] = None
    issues: Optional[List[str]] = None

@router.post("/{quote_id}/feedback")
async def submit_feedback(
    quote_id: str,
    request: FeedbackRequest,
    current_user: dict = Depends(get_current_user)
):
    # Validate quote ownership
    # Save feedback
    # Trigger learning if actual values provided
    # Return success

@router.get("/{quote_id}/feedback")
async def get_feedback(
    quote_id: str,
    current_user: dict = Depends(get_current_user)
):
    # Return existing feedback for quote
```

3. Add database methods:
   - `create_quote_feedback()`
   - `get_quote_feedback(quote_id)`
   - `get_feedback_stats(contractor_id)` - aggregate stats

4. Modify `LearningService.process_correction()` to also accept feedback:
   - If `actual_total` provided, treat as implicit correction
   - Use `accuracy_rating` to weight learning (low rating = stronger signal)
   - Store feedback patterns for prompting (e.g., "materials often rated low")

5. Add feedback UI to frontend after quote display:
```html
<div class="feedback-section" id="feedbackSection" style="display: none;">
    <h4>How accurate was this quote?</h4>

    <div class="star-rating" id="accuracyRating">
        <span data-value="1">☆</span>
        <span data-value="2">☆</span>
        <span data-value="3">☆</span>
        <span data-value="4">☆</span>
        <span data-value="5">☆</span>
    </div>

    <div class="aspect-ratings">
        <label>Materials: <select id="materialsRating">...</select></label>
        <label>Labor: <select id="laborRating">...</select></label>
        <label>Timeline: <select id="timelineRating">...</select></label>
    </div>

    <div class="actual-values">
        <label>Actual total (optional): <input type="number" id="actualTotal"></label>
        <label>Actual days (optional): <input type="number" id="actualDays"></label>
    </div>

    <div class="feedback-text">
        <label>Comments: <textarea id="feedbackText"></textarea></label>
    </div>

    <div class="quick-issues">
        <label><input type="checkbox" value="materials_too_high"> Materials too high</label>
        <label><input type="checkbox" value="materials_too_low"> Materials too low</label>
        <label><input type="checkbox" value="labor_too_high"> Labor too high</label>
        <label><input type="checkbox" value="labor_too_low"> Labor too low</label>
        <label><input type="checkbox" value="missing_line_item"> Missing line item</label>
    </div>

    <button onclick="submitFeedback()">Submit Feedback</button>
</div>
```

6. Show feedback section after quote is generated (not immediately, but after user reviews).

**Success criteria**: Users can submit feedback without editing quotes. Feedback is stored and used for learning. Feedback stats available per contractor.

---

## Enhancement 5: Active Learning (Clarifying Questions)

**Goal**: Proactively ask clarifying questions when confidence is low.

**Files to modify**:
- `backend/services/quote_generator.py`
- `backend/api/quotes.py`
- `frontend/index.html`

**Implementation**:

1. Modify quote generation response to include clarifying questions when confidence is low:
```python
class QuoteGenerationResponse(BaseModel):
    quote: QuoteOutput
    confidence: dict
    needs_clarification: bool
    clarifying_questions: Optional[List[dict]] = None
    # Each question: {id, question, type, options}
    # Types: "select", "number", "text", "boolean"
```

2. Generate clarifying questions based on uncertainty:
```python
async def generate_clarifying_questions(
    transcription: str,
    quote: QuoteOutput,
    confidence: dict
) -> List[dict]:
    if confidence["level"] == "high":
        return []

    # Ask Claude to identify what's uncertain
    questions = await self.client.messages.create(
        model="claude-sonnet-4-20250514",
        system="You identify what information is missing from a job description...",
        messages=[...],
        tools=[{
            "name": "generate_questions",
            "input_schema": {
                "type": "object",
                "properties": {
                    "questions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "question": {"type": "string"},
                                "type": {"enum": ["select", "number", "text", "boolean"]},
                                "options": {"type": "array", "items": {"type": "string"}},
                                "impacts": {"type": "string"}  # What this affects
                            }
                        }
                    }
                }
            }
        }],
        tool_choice={"type": "tool", "name": "generate_questions"}
    )
    return questions
```

3. Create endpoint to regenerate quote with clarifications:
```python
@router.post("/{quote_id}/clarify")
async def clarify_quote(
    quote_id: str,
    clarifications: dict,  # {question_id: answer}
    current_user: dict = Depends(get_current_user)
):
    # Get original quote
    # Append clarifications to transcription
    # Regenerate with additional context
    # Return updated quote with higher confidence
```

4. Add clarification UI to frontend:
   - When `needs_clarification` is true, show questions before full quote
   - Let user answer questions or skip
   - Regenerate quote with answers

**Success criteria**: Low-confidence quotes prompt clarifying questions. Answering questions improves confidence. Users can skip if they want the rough estimate.

</task>

<constraints>
- Preserve all existing functionality
- Follow existing code style and patterns
- Use existing service factory pattern (`get_*_service()`)
- Do not change database URL or authentication logic
- Do not install new dependencies unless necessary
- Keep the single-agent path for simple quotes (speed)
- Run agents in parallel where possible
</constraints>

<verification>
After each enhancement, verify:

1. **Structured Outputs**: Run `python -c "from backend.services import get_quote_service; ..."` to test quote generation returns valid JSON.

2. **Multi-Agent**: Check that complex quote generation logs show parallel agent execution.

3. **Confidence Sampling**: Verify `confidence_details` is populated in database after quote generation.

4. **User Feedback**: Test feedback submission via API and verify it appears in database.

5. **Active Learning**: Generate a quote with vague transcription, verify clarifying questions appear.
</verification>

<execution_order>
1. Enhancement 1 (Structured Outputs) - Foundation for everything else
2. Enhancement 4 (User Feedback) - New capability, independent
3. Enhancement 3 (Confidence Sampling) - Needed for active learning
4. Enhancement 2 (Multi-Agent) - Improves accuracy
5. Enhancement 5 (Active Learning) - Depends on confidence sampling
</execution_order>

<files_to_read_first>
Before starting, read these files to understand existing patterns:
- backend/services/quote_generator.py
- backend/services/learning.py
- backend/prompts/quote_generation.py
- backend/api/quotes.py
- backend/models/database.py
- backend/services/__init__.py
- frontend/index.html (quote display section)
</files_to_read_first>
