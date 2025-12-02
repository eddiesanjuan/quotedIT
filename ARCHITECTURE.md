# Quoted Architecture & Learning System

**Last Updated**: December 2024

This document provides comprehensive documentation for future Claude instances working on Quoted. It explains the core learning system, data structures, file locations, and how to modify any part of the system.

---

## Table of Contents

1. [System Overview](#system-overview)
2. [The Learning System (Core Innovation)](#the-learning-system-core-innovation)
3. [Data Structures](#data-structures)
4. [File Map](#file-map)
5. [The Three Main Flows](#the-three-main-flows)
6. [Modification Guide](#modification-guide)
7. [API Reference](#api-reference)

---

## System Overview

Quoted is a voice-to-quote application for contractors (and any business type). The user speaks a job description, and the system generates a structured quote. The key innovation is **per-category learning through prompt injection**.

### Core Concept

```
User speaks → Transcription → Category Detection → Quote Generation → User Edits → Learning → Better Future Quotes
```

The system learns from user corrections and stores learnings per-category. When generating future quotes in the same category, those learnings are injected into the prompt.

### Technology Stack

- **Backend**: FastAPI (Python)
- **Database**: SQLite with SQLAlchemy (async)
- **AI**: Anthropic Claude API
- **Transcription**: Whisper (OpenAI)
- **Frontend**: Vanilla HTML/CSS/JS (no framework)
- **Deployment**: Railway

---

## The Learning System (Core Innovation)

### How Learning Works

The learning system uses **prompt injection** rather than fine-tuning or embeddings:

1. **User edits a quote** → corrections detected
2. **AI analyzes corrections** → extracts learnings as text statements
3. **Learnings stored per-category** → in `pricing_knowledge.categories[category].learned_adjustments[]`
4. **Future quotes in same category** → learnings injected at top of prompt as "CRITICAL: Apply These Adjustments"

### Why This Approach?

- **No fine-tuning needed**: Works immediately with any model
- **Transparent**: Learnings are human-readable text
- **Per-category**: Different adjustments for different work types
- **Composable**: Works with few-shot learning from correction examples

### Learning Storage Structure

```python
pricing_knowledge = {
    "categories": {
        "brand_strategy": {
            "display_name": "Brand Strategy",
            "typical_price_range": [5000, 15000],
            "pricing_unit": "per_project",
            "base_rate": 8000,
            "notes": "Includes discovery, strategy, identity",
            "learned_adjustments": [  # <-- THE KEY: text statements
                "Add 25% for rush (< 48 hours)",
                "Include follow-up call in base price",
                "Reduce Research by ~15%"
            ],
            "samples": 12,
            "confidence": 0.82
        },
        "website_design": {
            "display_name": "Website Design",
            "learned_adjustments": [
                "Always include hosting setup in quote",
                "Increase Design by ~20% for e-commerce"
            ],
            "samples": 8,
            "confidence": 0.72
        }
    },
    "global_rules": [
        "Round all prices to nearest $50",
        "Always mention 50% deposit requirement"
    ]
}
```

### Prompt Injection Example

When generating a quote for "brand_strategy", the prompt includes:

```
## CRITICAL: Apply These Learned Adjustments for "Brand Strategy"

Based on 12 past corrections, YOU MUST apply these adjustments to your quote:

- Add 25% for rush (< 48 hours)
- Include follow-up call in base price
- Reduce Research by ~15%

Confidence: 82% (based on 12 corrections)

IMPORTANT: These are real corrections the contractor made. Apply them to get the pricing right.
```

---

## Data Structures

### PricingModel (Database)

```python
class PricingModel(Base):
    __tablename__ = "pricing_models"

    id = Column(String, primary_key=True)
    contractor_id = Column(String, ForeignKey("contractors.id"))

    # Core rates
    labor_rate_hourly = Column(Float)
    helper_rate_hourly = Column(Float)
    material_markup_percent = Column(Float, default=20.0)
    minimum_job_amount = Column(Float)

    # THE LEARNING STORAGE (JSON blob)
    pricing_knowledge = Column(JSON, default=dict)

    # General notes (backward compatibility)
    pricing_notes = Column(Text)
```

### pricing_knowledge Structure

```python
{
    "categories": {
        "<category_snake_case>": {
            "display_name": str,            # Human readable name
            "typical_price_range": [low, high],  # Optional
            "pricing_unit": str,            # per_hour, per_project, flat
            "base_rate": float,             # Optional base rate
            "notes": str,                   # What's included
            "learned_adjustments": [str],   # THE KEY - list of text learnings
            "samples": int,                 # Number of corrections processed
            "confidence": float             # 0.0-1.0, increases with corrections
        }
    },
    "global_rules": [str]  # Rules that apply to ALL categories
}
```

### SetupConversation (Database)

```python
class SetupConversation(Base):
    __tablename__ = "setup_conversations"

    id = Column(String, primary_key=True)
    contractor_id = Column(String, nullable=True)  # Nullable for pre-signup

    session_data = Column(JSON)  # contractor_name, primary_trade, initial_message
    messages = Column(JSON)       # List of {role, content}
    extracted_data = Column(JSON) # Extracted pricing model
    status = Column(String)       # in_progress, completed
```

### Quote (Database)

```python
class Quote(Base):
    __tablename__ = "quotes"

    # ... standard fields ...

    job_type = Column(String)           # The detected category
    was_edited = Column(Boolean)        # Whether user corrected it
    edit_details = Column(JSON)         # What changed (for learning)
    ai_generated_total = Column(Float)  # Original AI estimate
```

---

## File Map

### API Layer (`backend/api/`)

| File | Purpose | Key Functions |
|------|---------|---------------|
| `quotes.py` | Quote generation & editing API | `generate_quote()`, `update_quote()` (learning trigger) |
| `onboarding.py` | Setup interview API | `start_setup()`, `continue_setup()`, `complete_setup()` |
| `auth.py` | Authentication | JWT token handling |

### Services Layer (`backend/services/`)

| File | Purpose | Key Functions |
|------|---------|---------------|
| `quote_generator.py` | AI quote generation | `generate_quote()`, `detect_or_create_category()` |
| `learning.py` | Process corrections, extract learnings | `process_correction()` |
| `database.py` | All DB operations | `apply_learnings_to_pricing_model()` |
| `transcription.py` | Whisper transcription | `transcribe()` |
| `onboarding.py` | Interview AI conversation | `start_setup()`, `continue_setup()` |

### Prompts Layer (`backend/prompts/`)

| File | Purpose | Key Functions |
|------|---------|---------------|
| `quote_generation.py` | Quote generation prompts | `get_quote_generation_prompt()` - **includes learning injection** |
| `setup_interview.py` | Onboarding interview prompts | `get_setup_system_prompt()`, `get_pricing_extraction_prompt()` |

### Models Layer (`backend/models/`)

| File | Purpose |
|------|---------|
| `database.py` | SQLAlchemy models (User, Contractor, PricingModel, Quote, etc.) |

### Frontend (`frontend/`)

| File | Purpose |
|------|---------|
| `landing.html` | Landing page with logo spinner |
| `app.html` | Main app (quote generation) |
| `onboarding.html` | Setup interview UI |

---

## The Three Main Flows

### Flow 1: Onboarding Interview

```
User starts setup → AI asks about pricing → User responds → AI extracts categories → Stored in pricing_model
```

**Key Files**:
- `backend/api/onboarding.py` - API endpoints
- `backend/services/onboarding.py` - Interview AI logic
- `backend/prompts/setup_interview.py` - Interview prompts
- `backend/services/database.py` - `create_setup_conversation()`, `update_setup_conversation()`

**Data Flow**:
1. `POST /onboarding/start` → Creates SetupConversation in DB
2. `POST /onboarding/{id}/continue` → Updates messages in DB
3. `POST /onboarding/{id}/complete` → Extracts pricing model with categories

### Flow 2: Quote Generation

```
Transcription → Detect Category → Get Correction Examples → Generate Quote (with learnings injected)
```

**Key Files**:
- `backend/api/quotes.py` - `generate_quote()` endpoint
- `backend/services/quote_generator.py` - `generate_quote()`, `detect_or_create_category()`
- `backend/prompts/quote_generation.py` - `get_quote_generation_prompt()` **<-- LEARNING INJECTION HAPPENS HERE**

**Data Flow**:
1. `POST /quotes/generate` with transcription
2. `detect_or_create_category()` - Uses Haiku to match/create category
3. `get_correction_examples()` - Gets past corrections for this category
4. `get_quote_generation_prompt()` - Builds prompt with:
   - Category-specific `learned_adjustments` (lines 35-59)
   - Pricing knowledge
   - Correction examples (few-shot)
5. Claude generates structured quote
6. Quote saved to DB

### Flow 3: Learning Loop

```
User edits quote → Corrections detected → AI extracts learnings → Stored per-category → Future quotes use learnings
```

**Key Files**:
- `backend/api/quotes.py` - `update_quote()` endpoint (lines 417-533) **<-- LEARNING TRIGGER**
- `backend/services/learning.py` - `process_correction()` - Analyzes what changed
- `backend/services/database.py` - `apply_learnings_to_pricing_model()` **<-- STORES LEARNINGS**

**Data Flow**:
1. `PUT /quotes/{id}` with edits
2. Compare original vs final quote
3. `learning.process_correction()` - Claude analyzes changes, returns:
   ```python
   {
       "pricing_adjustments": [...],
       "new_pricing_rules": [...],
       "overall_tendency": "..."
   }
   ```
4. `database.apply_learnings_to_pricing_model()`:
   - Converts adjustments to text statements
   - Stores in `pricing_knowledge["categories"][category]["learned_adjustments"]`
   - Updates samples/confidence

---

## Modification Guide

### To Change How Learnings Are Stored

**File**: `backend/services/database.py`
**Function**: `apply_learnings_to_pricing_model()` (lines 194-324)

This function:
- Accepts `contractor_id`, `learnings`, and `category`
- Converts structured learnings to text statements
- Stores in `pricing_knowledge["categories"][category]["learned_adjustments"]`

### To Change How Learnings Are Injected Into Prompts

**File**: `backend/prompts/quote_generation.py`
**Function**: `get_quote_generation_prompt()` (lines 10-180)
**Injection Section**: Lines 35-59

```python
if detected_category and "categories" in pricing_knowledge:
    categories = pricing_knowledge.get("categories", {})
    if detected_category in categories:
        cat_data = categories[detected_category]
        learned_adjustments = cat_data.get("learned_adjustments", [])
        # ... builds category_learnings_str ...
```

### To Change Category Detection

**File**: `backend/services/quote_generator.py`
**Function**: `detect_or_create_category()` (lines 145-239)

Uses Claude Haiku for fast classification. Matches against existing categories or creates new ones.

### To Change The Interview

**File**: `backend/prompts/setup_interview.py`

Key functions:
- `get_setup_system_prompt()` - The AI's instructions
- `get_setup_initial_message()` - First message to user
- `get_pricing_extraction_prompt()` - Extracts structured data from conversation

### To Change The Quote Prompt

**File**: `backend/prompts/quote_generation.py`
**Function**: `get_quote_generation_prompt()`

The prompt includes (in order):
1. System context
2. Transcription
3. **Category-specific learned adjustments** (injected here)
4. Pricing information
5. Global rules
6. Terms
7. Correction examples (few-shot)
8. Output format instructions

### To Add New Database Fields

**File**: `backend/models/database.py`

Add column to relevant model, then run migration or recreate DB.

---

## API Reference

### Onboarding Endpoints

```
POST /onboarding/start
  Body: { contractor_name, primary_trade }
  Returns: SetupSessionResponse

POST /onboarding/{session_id}/continue
  Body: { message }
  Returns: SetupSessionResponse

POST /onboarding/{session_id}/complete
  Returns: PricingModelResponse (extracted pricing data)

POST /onboarding/quick
  Body: { contractor_name, primary_trade, labor_rate, material_markup, minimum_job }
  Returns: PricingModelResponse (skip interview)
```

### Quote Endpoints

```
POST /quotes/generate
  Body: { transcription }
  Returns: QuoteResponse

POST /quotes/generate-from-audio
  Body: multipart/form-data with audio file
  Returns: QuoteResponse

GET /quotes/{quote_id}
  Returns: QuoteResponse

PUT /quotes/{quote_id}  # <-- LEARNING TRIGGER
  Body: { line_items, job_description, correction_notes, ... }
  Returns: QuoteResponse (learning happens here)

POST /quotes/{quote_id}/pdf
  Returns: PDF file
```

---

## Debugging Tips

### Check What Learnings Are Stored

```python
# In Python console or test:
pricing_model = await db.get_pricing_model(contractor_id)
print(pricing_model.pricing_knowledge)
```

### Check What's Injected Into Prompts

Add logging to `get_quote_generation_prompt()`:
```python
print(f"Category learnings for {detected_category}:")
print(category_learnings_str)
```

### Test Category Detection

```python
result = await quote_service.detect_or_create_category(
    transcription="I need a brand strategy project",
    pricing_knowledge=pricing_model.pricing_knowledge
)
print(result)  # {'category': 'brand_strategy', 'is_new': False, ...}
```

---

## Key Design Decisions

1. **Text-based learnings**: Learnings are stored as human-readable text statements, not numeric adjustments. This allows for complex rules like "Add 25% for rush jobs" rather than just percentage offsets.

2. **Per-category isolation**: Each category has its own learnings. A learning from "brand_strategy" doesn't affect "website_design" quotes.

3. **Prompt injection over fine-tuning**: Learnings are injected into the prompt context rather than fine-tuning the model. This is:
   - Immediate (no training delay)
   - Transparent (can see exactly what's being used)
   - Reversible (can remove learnings)

4. **Dual learning sources**: System uses both:
   - `learned_adjustments` (structured text statements)
   - `correction_examples` (few-shot examples of past edits)

5. **Dynamic categories**: Categories are created/detected by AI rather than hardcoded. The AI can create new categories as needed.

---

## Common Modification Scenarios

### "I want to change the maximum number of learnings per category"

File: `backend/services/database.py`
Line: ~294
```python
if len(cat_data["learned_adjustments"]) > 20:  # Change this number
```

### "I want to change how learnings are formatted in the prompt"

File: `backend/prompts/quote_generation.py`
Lines: 47-59 (the `category_learnings_str` construction)

### "I want to add a new field to quotes"

1. Add column to `Quote` model in `backend/models/database.py`
2. Update `quote_to_response()` in `backend/api/quotes.py`
3. Update `QuoteResponse` Pydantic model in `backend/api/quotes.py`

### "I want to change the interview questions"

File: `backend/prompts/setup_interview.py`
Function: `get_setup_system_prompt()`

---

## Summary

The Quoted learning system is built on a simple but powerful principle: **store learnings as text, inject them into prompts**. This creates a transparent, debuggable, and immediately-effective learning loop that improves quote accuracy over time.

When in doubt:
- **Storage**: `backend/services/database.py` → `apply_learnings_to_pricing_model()`
- **Injection**: `backend/prompts/quote_generation.py` → `get_quote_generation_prompt()`
- **Detection**: `backend/services/quote_generator.py` → `detect_or_create_category()`
- **Learning Trigger**: `backend/api/quotes.py` → `update_quote()` endpoint
