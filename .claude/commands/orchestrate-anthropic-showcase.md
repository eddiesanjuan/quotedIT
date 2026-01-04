# Orchestrate Anthropic Showcase

Transform Quoted into an Anthropic showcase product demonstrating interpretable AI, honest uncertainty, and human-AI collaboration.

## Quick Start

```bash
/orchestrate-anthropic-showcase              # Start or continue
/orchestrate-anthropic-showcase --status     # Check progress
/orchestrate-anthropic-showcase --phase=N    # Jump to phase
/orchestrate-anthropic-showcase --reset      # Start fresh
```

## Phase Structure

| Phase | Name | Agents | Focus |
|-------|------|--------|-------|
| 0 | Context & Branch | 1 | Load state, create feature branch |
| 1 | Backend Wiring | 4 | Wire existing services to API endpoints |
| 2 | Confidence UI | 3 | Confidence badges, tooltips, visual indicators |
| 3 | Explanation UI | 3 | Pricing transparency, reasoning display |
| 4 | Learning Dashboard | 3 | Progress visualization, velocity metrics |
| 5 | Correction Feedback | 2 | Structured feedback loops, learning capture |
| 6 | Integration Testing | 2 | Pre-PR comprehensive testing |
| 7 | PR & Preview | 2 | Create PR, test Railway preview |
| 8 | Merge & Deploy | 1 | Merge to main, monitor deployment |
| 9 | Production QA | 3 | Full production verification |
| 10 | Documentation | 2 | Update docs, capture metrics |

**Total: 26 agents across 11 phases**

---

## Tool Arsenal

### GitHub CLI
```bash
gh repo view                    # Verify repo access
gh pr create --title "..." --body "..."   # Create PR
gh pr merge --squash            # Merge after approval
gh pr view --web                # Open PR in browser
```

### Railway CLI
```bash
railway logs -n 100             # View recent logs
railway logs --filter "error"   # Filter for errors
railway status                  # Check deployment status
railway variables               # Check env vars
```

### Claude Chrome Extension (MCP)
```javascript
mcp__claude-in-chrome__tabs_context_mcp     // Get tab context
mcp__claude-in-chrome__tabs_create_mcp      // Create new tab
mcp__claude-in-chrome__navigate             // Navigate to URL
mcp__claude-in-chrome__computer             // Screenshot, click, type
mcp__claude-in-chrome__read_page            // Read page accessibility tree
mcp__claude-in-chrome__read_console_messages // Check for JS errors
mcp__claude-in-chrome__read_network_requests // Monitor API calls
```

---

## Phase 0: Context & Branch Setup

**Agent Count**: 1
**Priority**: CRITICAL
**Dependencies**: None

### Agent 0A: Initialize Orchestration

**Target**: Git repository, state files

TASK: Load context and create feature branch for all Anthropic showcase work.

PROCEDURE:
1. Read state file: `.claude/anthropic-showcase-state.md`
2. Read current engineering state: `ENGINEERING_STATE.md`
3. Check git status for clean working directory
4. Create feature branch:
   ```bash
   git checkout -b feat/anthropic-showcase-learning
   git push -u origin feat/anthropic-showcase-learning
   ```
5. Update state file with branch name and start timestamp

VERIFICATION:
- Branch exists locally and on remote
- State file updated with `branch: feat/anthropic-showcase-learning`
- Working directory is clean

SUCCESS GATE: Branch created and pushed before proceeding to Phase 1.

---

## Phase 1: Backend Wiring

**Agent Count**: 4
**Priority**: CRITICAL
**Dependencies**: Phase 0 complete

**Key Insight**: Services exist but aren't exposed via API. Wire them up.

### Agent 1A: Confidence API Endpoint

**Target**: `backend/api/learning.py`
**Services**: `backend/services/pricing_confidence.py`

TASK: Add GET `/api/learning/confidence/{category}` endpoint.

IMPLEMENTATION:
```python
from backend.services.pricing_confidence import PricingConfidenceService

@router.get("/confidence/{category}")
async def get_category_confidence(
    category: str,
    contractor_id: str = Depends(get_current_contractor_id),
    db: AsyncSession = Depends(get_db)
):
    """Get confidence metrics for a job category."""
    service = PricingConfidenceService()

    # Load contractor's pricing model
    contractor = await db.execute(
        select(Contractor).where(Contractor.id == contractor_id)
    )
    contractor = contractor.scalar_one_or_none()
    if not contractor or not contractor.pricing_model:
        return {"confidence": 0.5, "display": "learning", "message": "Building your pricing model"}

    result = service.get_confidence_display(
        pricing_model=contractor.pricing_model,
        category=category
    )
    return result
```

VERIFICATION:
```bash
curl -X GET "http://localhost:8000/api/learning/confidence/bathroom_remodel" \
  -H "Authorization: Bearer $TOKEN"
# Expected: {"confidence": 0.72, "display": "medium", "message": "...", "tooltip": "..."}
```

### Agent 1B: Explanation API Endpoint

**Target**: `backend/api/learning.py`
**Services**: `backend/services/pricing_explanation.py`

TASK: Add GET `/api/learning/explanation/{quote_id}` endpoint.

IMPLEMENTATION:
```python
from backend.services.pricing_explanation import PricingExplanationService

@router.get("/explanation/{quote_id}")
async def get_quote_explanation(
    quote_id: str,
    contractor_id: str = Depends(get_current_contractor_id),
    db: AsyncSession = Depends(get_db)
):
    """Get pricing explanation for a specific quote."""
    # Load quote
    quote = await db.execute(
        select(Quote).where(
            Quote.id == quote_id,
            Quote.contractor_id == contractor_id
        )
    )
    quote = quote.scalar_one_or_none()
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")

    # Load contractor's pricing model
    contractor = await db.execute(
        select(Contractor).where(Contractor.id == contractor_id)
    )
    contractor = contractor.scalar_one_or_none()

    service = PricingExplanationService()
    explanation = service.generate_explanation(
        quote=quote,
        pricing_model=contractor.pricing_model if contractor else None
    )
    return explanation.to_dict()
```

VERIFICATION:
```bash
curl -X GET "http://localhost:8000/api/learning/explanation/quote_abc123" \
  -H "Authorization: Bearer $TOKEN"
# Expected: {"components": [...], "patterns_applied": [...], "uncertainty_notes": [...]}
```

### Agent 1C: Overall Progress API Enhancement

**Target**: `backend/api/learning.py`

TASK: Enhance `/api/learning/progress` to include confidence and explanation summaries.

IMPLEMENTATION:
```python
@router.get("/progress")
async def get_learning_progress(
    contractor_id: str = Depends(get_current_contractor_id),
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive learning progress with confidence metrics."""
    contractor = await db.execute(
        select(Contractor).where(Contractor.id == contractor_id)
    )
    contractor = contractor.scalar_one_or_none()

    if not contractor or not contractor.pricing_model:
        return {
            "categories": [],
            "overall_confidence": 0.5,
            "quotes_total": 0,
            "learning_velocity": "starting",
            "next_milestone": "Complete your first quote"
        }

    pricing_model = contractor.pricing_model
    pricing_knowledge = pricing_model.get("pricing_knowledge", {})
    categories = pricing_knowledge.get("categories", {})

    confidence_service = PricingConfidenceService()

    category_summaries = []
    for cat_name, cat_data in categories.items():
        confidence = confidence_service.calculate_confidence(
            pricing_model=pricing_model,
            category=cat_name
        )
        category_summaries.append({
            "name": cat_name,
            "confidence": confidence.overall_confidence,
            "display": confidence_service.get_confidence_display(pricing_model, cat_name),
            "quote_count": cat_data.get("acceptance_count", 0) + cat_data.get("correction_count", 0),
            "last_activity": cat_data.get("last_acceptance_at") or cat_data.get("last_correction_at")
        })

    # Calculate overall confidence (weighted by quote count)
    total_quotes = sum(c["quote_count"] for c in category_summaries)
    if total_quotes > 0:
        overall = sum(c["confidence"] * c["quote_count"] for c in category_summaries) / total_quotes
    else:
        overall = 0.5

    return {
        "categories": category_summaries,
        "overall_confidence": overall,
        "quotes_total": total_quotes,
        "learning_velocity": _calculate_velocity(category_summaries),
        "next_milestone": _get_next_milestone(overall, total_quotes)
    }

def _calculate_velocity(categories):
    """Calculate learning velocity based on recent activity."""
    # Implementation based on last_activity timestamps
    pass

def _get_next_milestone(confidence, quote_count):
    """Determine next milestone for user motivation."""
    if quote_count < 5:
        return f"Complete {5 - quote_count} more quotes to establish baseline"
    if confidence < 0.6:
        return "Send quotes without edits to boost confidence"
    if confidence < 0.8:
        return "You're getting accurate! A few more will reach high confidence"
    return "Expert level reached - your AI knows your pricing well"
```

VERIFICATION:
```bash
curl -X GET "http://localhost:8000/api/learning/progress" \
  -H "Authorization: Bearer $TOKEN"
# Expected: Enhanced response with confidence metrics per category
```

### Agent 1D: Acceptance Signal Verification

**Target**: `backend/api/share.py` (lines 226, 582)

TASK: Verify acceptance learning is properly wired and add logging.

PROCEDURE:
1. Read `backend/api/share.py` lines 220-240 and 575-590
2. Verify `db.apply_acceptance_to_pricing_model()` is called correctly
3. Add structured logging for acceptance signals:
   ```python
   import logging
   logger = logging.getLogger(__name__)

   # After acceptance processing
   logger.info(f"Acceptance signal processed: contractor={contractor_id}, category={quote.job_type}, signal_type=sent")
   ```
4. Add PostHog event tracking:
   ```python
   posthog.capture(
       distinct_id=contractor_id,
       event="acceptance_learning_triggered",
       properties={
           "category": quote.job_type,
           "signal_type": "sent",
           "quote_total": quote.total
       }
   )
   ```

VERIFICATION:
```bash
# Check Railway logs after sending a quote
railway logs -n 50 --filter "acceptance"
# Expected: "Acceptance signal processed: ..."
```

**PHASE 1 GATE**: All 4 endpoints tested locally with curl before proceeding.

---

## Phase 2: Confidence UI Components

**Agent Count**: 3
**Priority**: HIGH
**Dependencies**: Phase 1 complete

### Agent 2A: Confidence Badge Component

**Target**: `frontend/index.html`

TASK: Create reusable confidence badge component using safe DOM methods.

IMPLEMENTATION:
```javascript
// Add to frontend/index.html in <script> section

function createConfidenceBadge(confidence, display, tooltip) {
    const badge = document.createElement('span');
    badge.className = `confidence-badge confidence-${display}`;
    badge.title = tooltip || '';

    const icon = document.createElement('span');
    icon.className = 'confidence-icon';
    icon.textContent = getConfidenceIcon(display);

    const text = document.createElement('span');
    text.className = 'confidence-text';
    text.textContent = `${Math.round(confidence * 100)}%`;

    badge.appendChild(icon);
    badge.appendChild(text);

    return badge;
}

function getConfidenceIcon(display) {
    const icons = {
        'high': '✓',
        'medium': '◐',
        'low': '○',
        'learning': '📚'
    };
    return icons[display] || '○';
}

// CSS styles to add
const confidenceStyles = `
.confidence-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 500;
}
.confidence-high { background: #dcfce7; color: #166534; }
.confidence-medium { background: #fef3c7; color: #92400e; }
.confidence-low { background: #fee2e2; color: #991b1b; }
.confidence-learning { background: #e0e7ff; color: #3730a3; }
`;
```

VERIFICATION:
- Badge renders correctly for all 4 states
- Tooltip shows on hover
- Accessible (has title attribute)

### Agent 2B: Quote Card Confidence Integration

**Target**: `frontend/index.html` - quote rendering functions

TASK: Add confidence badge to quote cards in the quote list.

IMPLEMENTATION:
1. Find the function that renders quote cards (likely `renderQuote` or similar)
2. After rendering quote, fetch confidence and add badge:
```javascript
async function renderQuoteWithConfidence(quote, container) {
    // Existing quote rendering...
    const quoteCard = renderQuoteCard(quote);

    // Fetch confidence for this quote's category
    try {
        const response = await fetch(`/api/learning/confidence/${encodeURIComponent(quote.job_type)}`, {
            headers: { 'Authorization': `Bearer ${getToken()}` }
        });
        if (response.ok) {
            const confidence = await response.json();
            const badge = createConfidenceBadge(
                confidence.confidence,
                confidence.display,
                confidence.tooltip
            );

            // Find header section of quote card and append badge
            const header = quoteCard.querySelector('.quote-header');
            if (header) {
                header.appendChild(badge);
            }
        }
    } catch (err) {
        console.warn('Could not load confidence:', err);
    }

    container.appendChild(quoteCard);
}
```

VERIFICATION:
- Each quote card shows confidence badge
- Badge reflects actual category confidence
- Graceful degradation if API fails

### Agent 2C: Real-time Confidence Update

**Target**: `frontend/index.html`

TASK: Update confidence badge after quote actions (send, edit).

IMPLEMENTATION:
```javascript
// After sending a quote successfully
async function onQuoteSent(quote) {
    // Existing success handling...

    // Trigger confidence refresh
    await refreshCategoryConfidence(quote.job_type);

    // Show learning feedback toast
    showToast('Your AI is learning from this quote!', 'info');
}

async function refreshCategoryConfidence(category) {
    const response = await fetch(`/api/learning/confidence/${encodeURIComponent(category)}`, {
        headers: { 'Authorization': `Bearer ${getToken()}` }
    });
    if (response.ok) {
        const confidence = await response.json();
        // Update all badges for this category
        document.querySelectorAll(`[data-category="${category}"] .confidence-badge`).forEach(badge => {
            updateBadgeDisplay(badge, confidence);
        });
    }
}
```

VERIFICATION:
- Confidence updates visually after sending quote
- Toast notification appears
- No console errors

**PHASE 2 GATE**: Confidence badges visible and functional on quote cards.

---

## Phase 3: Explanation UI

**Agent Count**: 3
**Priority**: HIGH
**Dependencies**: Phase 2 complete

### Agent 3A: Explanation Panel Component

**Target**: `frontend/index.html`

TASK: Create expandable explanation panel for quote pricing.

IMPLEMENTATION:
```javascript
function createExplanationPanel(explanation) {
    const panel = document.createElement('div');
    panel.className = 'explanation-panel collapsed';

    // Header with toggle
    const header = document.createElement('button');
    header.className = 'explanation-header';
    header.setAttribute('aria-expanded', 'false');

    const headerText = document.createElement('span');
    headerText.textContent = 'How was this priced?';

    const headerIcon = document.createElement('span');
    headerIcon.className = 'explanation-toggle-icon';
    headerIcon.textContent = '▼';

    header.appendChild(headerText);
    header.appendChild(headerIcon);

    // Content
    const content = document.createElement('div');
    content.className = 'explanation-content';

    // Components breakdown
    if (explanation.components && explanation.components.length > 0) {
        const componentsSection = createComponentsSection(explanation.components);
        content.appendChild(componentsSection);
    }

    // Patterns applied
    if (explanation.patterns_applied && explanation.patterns_applied.length > 0) {
        const patternsSection = createPatternsSection(explanation.patterns_applied);
        content.appendChild(patternsSection);
    }

    // Uncertainty notes
    if (explanation.uncertainty_notes && explanation.uncertainty_notes.length > 0) {
        const uncertaintySection = createUncertaintySection(explanation.uncertainty_notes);
        content.appendChild(uncertaintySection);
    }

    header.addEventListener('click', () => {
        const isExpanded = panel.classList.toggle('expanded');
        panel.classList.toggle('collapsed', !isExpanded);
        header.setAttribute('aria-expanded', isExpanded);
        headerIcon.textContent = isExpanded ? '▲' : '▼';
    });

    panel.appendChild(header);
    panel.appendChild(content);

    return panel;
}

function createComponentsSection(components) {
    const section = document.createElement('div');
    section.className = 'explanation-section';

    const title = document.createElement('h4');
    title.textContent = 'Price Breakdown';
    section.appendChild(title);

    const list = document.createElement('ul');
    list.className = 'components-list';

    components.forEach(comp => {
        const item = document.createElement('li');
        item.className = 'component-item';

        const name = document.createElement('span');
        name.className = 'component-name';
        name.textContent = comp.name;

        const price = document.createElement('span');
        price.className = 'component-price';
        price.textContent = formatCurrency(comp.price);

        const source = document.createElement('span');
        source.className = 'component-source';
        source.textContent = `(${comp.source})`;

        item.appendChild(name);
        item.appendChild(price);
        item.appendChild(source);
        list.appendChild(item);
    });

    section.appendChild(list);
    return section;
}
```

VERIFICATION:
- Panel expands/collapses on click
- Components show name, price, source
- Accessible (aria-expanded)

### Agent 3B: Quote Detail Explanation Integration

**Target**: Quote detail view in `frontend/index.html`

TASK: Fetch and display explanation when viewing quote details.

IMPLEMENTATION:
```javascript
async function showQuoteDetails(quoteId) {
    // Existing quote detail loading...
    const quote = await fetchQuote(quoteId);
    renderQuoteDetails(quote);

    // Fetch and render explanation
    try {
        const response = await fetch(`/api/learning/explanation/${quoteId}`, {
            headers: { 'Authorization': `Bearer ${getToken()}` }
        });
        if (response.ok) {
            const explanation = await response.json();
            const panel = createExplanationPanel(explanation);

            const detailsContainer = document.getElementById('quote-details');
            if (detailsContainer) {
                detailsContainer.appendChild(panel);
            }
        }
    } catch (err) {
        console.warn('Could not load explanation:', err);
    }
}
```

VERIFICATION:
- Explanation panel appears in quote details
- Shows accurate pricing breakdown
- Graceful handling of missing data

### Agent 3C: Inline Explanation Tooltips

**Target**: Line items in quote view

TASK: Add hover tooltips showing why each line item is priced as shown.

IMPLEMENTATION:
```javascript
function addLineItemTooltips(lineItems, explanation) {
    if (!explanation || !explanation.components) return;

    lineItems.forEach((itemEl, index) => {
        const component = explanation.components[index];
        if (!component) return;

        const tooltip = document.createElement('div');
        tooltip.className = 'line-item-tooltip';
        tooltip.setAttribute('role', 'tooltip');

        const sourceText = document.createElement('p');
        sourceText.textContent = `Source: ${component.source}`;

        if (component.confidence) {
            const confText = document.createElement('p');
            confText.textContent = `Confidence: ${Math.round(component.confidence * 100)}%`;
            tooltip.appendChild(confText);
        }

        tooltip.appendChild(sourceText);

        // Position tooltip on hover
        itemEl.addEventListener('mouseenter', (e) => {
            tooltip.style.display = 'block';
            positionTooltip(tooltip, e.target);
        });

        itemEl.addEventListener('mouseleave', () => {
            tooltip.style.display = 'none';
        });

        itemEl.appendChild(tooltip);
    });
}
```

VERIFICATION:
- Hovering line item shows source tooltip
- Tooltip positions correctly
- Accessible (role="tooltip")

**PHASE 3 GATE**: Explanation UI complete with panel and tooltips.

---

## Phase 4: Learning Dashboard

**Agent Count**: 3
**Priority**: HIGH
**Dependencies**: Phase 3 complete

### Agent 4A: Dashboard Page Structure

**Target**: Create `frontend/learning.html` or add section to `index.html`

TASK: Create learning dashboard layout with progress visualization.

IMPLEMENTATION:
```html
<!-- Add to index.html as a new tab/section, or create learning.html -->
<div id="learning-dashboard" class="dashboard-section" style="display: none;">
    <div class="dashboard-header">
        <h2>Your AI Learning Progress</h2>
        <p class="dashboard-subtitle">See how your pricing AI improves with every quote</p>
    </div>

    <div class="dashboard-overview">
        <div class="stat-card overall-confidence">
            <div class="stat-value" id="overall-confidence-value">--</div>
            <div class="stat-label">Overall Confidence</div>
            <div class="stat-sublabel" id="confidence-description">Loading...</div>
        </div>

        <div class="stat-card quotes-count">
            <div class="stat-value" id="total-quotes-value">--</div>
            <div class="stat-label">Quotes Analyzed</div>
        </div>

        <div class="stat-card learning-velocity">
            <div class="stat-value" id="velocity-value">--</div>
            <div class="stat-label">Learning Velocity</div>
        </div>
    </div>

    <div class="category-breakdown">
        <h3>Confidence by Category</h3>
        <div id="category-list" class="category-list">
            <!-- Populated by JS -->
        </div>
    </div>

    <div class="next-milestone">
        <h3>Next Milestone</h3>
        <p id="milestone-text">Loading...</p>
    </div>
</div>
```

VERIFICATION:
- Dashboard layout renders correctly
- All placeholder elements exist
- Responsive on mobile (375px)

### Agent 4B: Dashboard Data Loading

**Target**: `frontend/index.html` JavaScript

TASK: Load and display learning progress data.

IMPLEMENTATION:
```javascript
async function loadLearningDashboard() {
    const dashboard = document.getElementById('learning-dashboard');
    if (!dashboard) return;

    try {
        const response = await fetch('/api/learning/progress', {
            headers: { 'Authorization': `Bearer ${getToken()}` }
        });

        if (!response.ok) throw new Error('Failed to load progress');

        const data = await response.json();

        // Update overall confidence
        const confValue = document.getElementById('overall-confidence-value');
        if (confValue) {
            confValue.textContent = `${Math.round(data.overall_confidence * 100)}%`;
            confValue.className = `stat-value confidence-${getConfidenceLevel(data.overall_confidence)}`;
        }

        // Update description
        const confDesc = document.getElementById('confidence-description');
        if (confDesc) {
            confDesc.textContent = getConfidenceDescription(data.overall_confidence);
        }

        // Update quotes count
        const quotesValue = document.getElementById('total-quotes-value');
        if (quotesValue) {
            quotesValue.textContent = data.quotes_total.toString();
        }

        // Update velocity
        const velocityValue = document.getElementById('velocity-value');
        if (velocityValue) {
            velocityValue.textContent = formatVelocity(data.learning_velocity);
        }

        // Update milestone
        const milestoneText = document.getElementById('milestone-text');
        if (milestoneText) {
            milestoneText.textContent = data.next_milestone;
        }

        // Render category breakdown
        renderCategoryBreakdown(data.categories);

    } catch (err) {
        console.error('Failed to load learning dashboard:', err);
        showDashboardError();
    }
}

function renderCategoryBreakdown(categories) {
    const container = document.getElementById('category-list');
    if (!container) return;

    // Clear existing
    container.replaceChildren();

    if (!categories || categories.length === 0) {
        const emptyState = document.createElement('p');
        emptyState.className = 'empty-state';
        emptyState.textContent = 'Create your first quote to start building category expertise!';
        container.appendChild(emptyState);
        return;
    }

    categories.forEach(cat => {
        const card = createCategoryCard(cat);
        container.appendChild(card);
    });
}

function createCategoryCard(category) {
    const card = document.createElement('div');
    card.className = 'category-card';
    card.setAttribute('data-category', category.name);

    const header = document.createElement('div');
    header.className = 'category-header';

    const name = document.createElement('span');
    name.className = 'category-name';
    name.textContent = formatCategoryName(category.name);

    const badge = createConfidenceBadge(
        category.confidence,
        category.display.display,
        category.display.tooltip
    );

    header.appendChild(name);
    header.appendChild(badge);

    const details = document.createElement('div');
    details.className = 'category-details';

    const quoteCount = document.createElement('span');
    quoteCount.textContent = `${category.quote_count} quotes`;

    details.appendChild(quoteCount);

    if (category.last_activity) {
        const lastActive = document.createElement('span');
        lastActive.textContent = ` · Last: ${formatRelativeTime(category.last_activity)}`;
        details.appendChild(lastActive);
    }

    card.appendChild(header);
    card.appendChild(details);

    return card;
}

function getConfidenceDescription(confidence) {
    if (confidence >= 0.8) return 'Expert level - AI knows your pricing well';
    if (confidence >= 0.6) return 'Growing expertise - accuracy improving';
    if (confidence >= 0.4) return 'Building patterns - more data helps';
    return 'Just starting - every quote teaches';
}
```

VERIFICATION:
- Dashboard shows real data from API
- Categories render with confidence badges
- Empty state shows for new users

### Agent 4C: Dashboard Navigation Integration

**Target**: Main navigation in `frontend/index.html`

TASK: Add Learning tab to main navigation.

IMPLEMENTATION:
```javascript
// Find navigation element and add Learning tab
function addLearningNavigation() {
    const nav = document.querySelector('.main-nav') || document.querySelector('nav');
    if (!nav) return;

    const learningTab = document.createElement('button');
    learningTab.className = 'nav-tab';
    learningTab.setAttribute('data-tab', 'learning');
    learningTab.textContent = 'AI Learning';

    learningTab.addEventListener('click', () => {
        // Hide other sections
        document.querySelectorAll('.dashboard-section').forEach(s => {
            s.style.display = 'none';
        });

        // Show learning dashboard
        const dashboard = document.getElementById('learning-dashboard');
        if (dashboard) {
            dashboard.style.display = 'block';
            loadLearningDashboard();
        }

        // Update nav state
        document.querySelectorAll('.nav-tab').forEach(t => {
            t.classList.remove('active');
        });
        learningTab.classList.add('active');
    });

    nav.appendChild(learningTab);
}
```

VERIFICATION:
- Learning tab visible in navigation
- Clicking tab shows dashboard
- Data loads correctly

**PHASE 4 GATE**: Learning dashboard fully functional and accessible.

---

## Phase 5: Correction Feedback Loops

**Agent Count**: 2
**Priority**: MEDIUM
**Dependencies**: Phase 4 complete

### Agent 5A: Edit Detection Enhancement

**Target**: Quote editing flow in `frontend/index.html`

TASK: Detect when user edits AI-generated prices and capture structured feedback.

IMPLEMENTATION:
```javascript
function trackPriceEdit(lineItemId, originalPrice, newPrice, category) {
    // Store edit for later learning submission
    const edit = {
        line_item_id: lineItemId,
        original_price: originalPrice,
        new_price: newPrice,
        category: category,
        edit_type: newPrice > originalPrice ? 'increase' : 'decrease',
        edit_percentage: ((newPrice - originalPrice) / originalPrice) * 100,
        timestamp: new Date().toISOString()
    };

    // Store in session for batch submission
    const pendingEdits = JSON.parse(sessionStorage.getItem('pending_edits') || '[]');
    pendingEdits.push(edit);
    sessionStorage.setItem('pending_edits', JSON.stringify(pendingEdits));

    // Show feedback prompt if significant edit
    if (Math.abs(edit.edit_percentage) > 10) {
        showEditFeedbackPrompt(edit);
    }
}

function showEditFeedbackPrompt(edit) {
    const prompt = document.createElement('div');
    prompt.className = 'edit-feedback-prompt';

    const message = document.createElement('p');
    message.textContent = `You changed this from ${formatCurrency(edit.original_price)} to ${formatCurrency(edit.new_price)}. Why?`;

    const options = document.createElement('div');
    options.className = 'feedback-options';

    const reasons = [
        { value: 'too_high', label: 'AI price was too high' },
        { value: 'too_low', label: 'AI price was too low' },
        { value: 'special_circumstances', label: 'Special circumstances' },
        { value: 'customer_request', label: 'Customer requested' }
    ];

    reasons.forEach(reason => {
        const btn = document.createElement('button');
        btn.className = 'feedback-option';
        btn.textContent = reason.label;
        btn.addEventListener('click', () => {
            submitEditFeedback(edit, reason.value);
            prompt.remove();
        });
        options.appendChild(btn);
    });

    prompt.appendChild(message);
    prompt.appendChild(options);

    document.body.appendChild(prompt);
}

async function submitEditFeedback(edit, reason) {
    try {
        await fetch('/api/learning/feedback', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${getToken()}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                ...edit,
                feedback_reason: reason
            })
        });
    } catch (err) {
        console.warn('Failed to submit edit feedback:', err);
    }
}
```

VERIFICATION:
- Editing price triggers tracking
- Significant edits show feedback prompt
- Feedback submits to API

### Agent 5B: Feedback API Endpoint

**Target**: `backend/api/learning.py`

TASK: Add POST `/api/learning/feedback` endpoint for structured corrections.

IMPLEMENTATION:
```python
from pydantic import BaseModel
from typing import Optional

class EditFeedback(BaseModel):
    line_item_id: Optional[str]
    original_price: float
    new_price: float
    category: str
    edit_type: str  # 'increase' or 'decrease'
    edit_percentage: float
    feedback_reason: str
    timestamp: str

@router.post("/feedback")
async def submit_edit_feedback(
    feedback: EditFeedback,
    contractor_id: str = Depends(get_current_contractor_id),
    db: AsyncSession = Depends(get_db)
):
    """Record structured feedback about pricing corrections."""

    # Log for learning system
    logger.info(
        f"Edit feedback: contractor={contractor_id}, "
        f"category={feedback.category}, "
        f"type={feedback.edit_type}, "
        f"percentage={feedback.edit_percentage:.1f}%, "
        f"reason={feedback.feedback_reason}"
    )

    # Track in PostHog for analysis
    posthog.capture(
        distinct_id=contractor_id,
        event="pricing_feedback_submitted",
        properties={
            "category": feedback.category,
            "edit_type": feedback.edit_type,
            "edit_percentage": feedback.edit_percentage,
            "feedback_reason": feedback.feedback_reason
        }
    )

    # TODO: Feed into learning system for model improvement
    # This creates a correction signal (opposite of acceptance)

    return {"status": "recorded"}
```

VERIFICATION:
- Endpoint accepts feedback payload
- Logs to Railway
- PostHog event tracked

**PHASE 5 GATE**: Correction feedback system capturing structured learning signals.

---

## Phase 6: Integration Testing (Pre-PR)

**Agent Count**: 2
**Priority**: CRITICAL
**Dependencies**: Phases 1-5 complete

### Agent 6A: Backend API Tests

**Tools**: Bash (curl), Railway CLI

TASK: Test all new API endpoints comprehensively.

PROCEDURE:
```bash
# Start local backend
cd backend && uvicorn main:app --reload --port 8000 &

# Wait for startup
sleep 5

# Test confidence endpoint
echo "Testing /api/learning/confidence..."
curl -s -X GET "http://localhost:8000/api/learning/confidence/bathroom_remodel" \
  -H "Authorization: Bearer $TEST_TOKEN" | jq .

# Test explanation endpoint (need valid quote ID)
echo "Testing /api/learning/explanation..."
curl -s -X GET "http://localhost:8000/api/learning/explanation/test_quote_id" \
  -H "Authorization: Bearer $TEST_TOKEN" | jq .

# Test progress endpoint
echo "Testing /api/learning/progress..."
curl -s -X GET "http://localhost:8000/api/learning/progress" \
  -H "Authorization: Bearer $TEST_TOKEN" | jq .

# Test feedback endpoint
echo "Testing /api/learning/feedback..."
curl -s -X POST "http://localhost:8000/api/learning/feedback" \
  -H "Authorization: Bearer $TEST_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "original_price": 500,
    "new_price": 550,
    "category": "bathroom_remodel",
    "edit_type": "increase",
    "edit_percentage": 10,
    "feedback_reason": "too_low",
    "timestamp": "2025-01-01T00:00:00Z"
  }' | jq .
```

OUTPUT: Table of endpoint test results
| Endpoint | Status | Response Time | Notes |
|----------|--------|---------------|-------|

### Agent 6B: Frontend Visual Tests

**Tools**: Claude Chrome Extension MCP

TASK: Visually verify all UI components render correctly.

PROCEDURE:
```javascript
// 1. Get browser context
mcp__claude-in-chrome__tabs_context_mcp({ createIfEmpty: true })

// 2. Create new tab
mcp__claude-in-chrome__tabs_create_mcp()

// 3. Navigate to local dev
mcp__claude-in-chrome__navigate({
    url: "http://localhost:8000",
    tabId: TAB_ID
})

// 4. Login (if needed)
// ... login steps ...

// 5. Screenshot home with confidence badges
mcp__claude-in-chrome__computer({
    action: "screenshot",
    tabId: TAB_ID
})

// 6. Navigate to learning dashboard
mcp__claude-in-chrome__find({
    query: "AI Learning tab",
    tabId: TAB_ID
})
// Click learning tab
mcp__claude-in-chrome__computer({
    action: "left_click",
    ref: REF_ID,
    tabId: TAB_ID
})

// 7. Screenshot dashboard
mcp__claude-in-chrome__computer({
    action: "screenshot",
    tabId: TAB_ID
})

// 8. Test mobile viewport
mcp__claude-in-chrome__resize_window({
    width: 375,
    height: 812,
    tabId: TAB_ID
})
mcp__claude-in-chrome__computer({
    action: "screenshot",
    tabId: TAB_ID
})

// 9. Check for console errors
mcp__claude-in-chrome__read_console_messages({
    tabId: TAB_ID,
    onlyErrors: true
})
```

OUTPUT: Screenshots and error report
- Desktop screenshot
- Mobile screenshot
- Console errors (should be none)

**PHASE 6 GATE**: All tests pass before creating PR.

---

## Phase 7: PR & Preview Testing

**Agent Count**: 2
**Priority**: CRITICAL
**Dependencies**: Phase 6 complete

### Agent 7A: Create Pull Request

**Tools**: GitHub CLI

TASK: Create comprehensive PR with full description.

PROCEDURE:
```bash
# Ensure all changes committed
git add .
git commit -m "feat: Anthropic showcase learning transparency

- Add confidence API endpoint with per-category metrics
- Add explanation API endpoint with pricing breakdown
- Enhance progress endpoint with confidence summaries
- Create confidence badge UI component
- Build expandable explanation panel
- Create learning dashboard with progress visualization
- Add edit feedback capture for structured corrections
- Wire acceptance learning signals with logging

Anthropic showcase principles:
- Interpretable AI: Every price explained
- Honest uncertainty: Confidence badges show certainty
- Human-AI collaboration: Learning from corrections"

git push origin feat/anthropic-showcase-learning

# Create PR
gh pr create \
  --title "feat: Anthropic showcase learning transparency" \
  --body "$(cat <<'EOF'
## Summary
Transform Quoted's learning system into an Anthropic showcase demonstrating interpretable AI, honest uncertainty, and human-AI collaboration.

### New Features
- **Confidence Badges**: Visual indicators showing AI certainty per category
- **Pricing Explanations**: Expandable panels showing how each price was determined
- **Learning Dashboard**: Progress visualization with velocity metrics
- **Correction Feedback**: Structured capture of pricing corrections

### API Endpoints Added
- `GET /api/learning/confidence/{category}` - Category confidence metrics
- `GET /api/learning/explanation/{quote_id}` - Quote pricing breakdown
- `POST /api/learning/feedback` - Structured correction feedback

### Anthropic Principles Demonstrated
1. **Interpretable AI**: Every pricing decision traceable to source
2. **Honest Uncertainty**: Confidence scores reflect actual data quality
3. **Human-AI Collaboration**: Learning improves from user corrections

## Test Plan
- [ ] Backend: All new endpoints return valid responses
- [ ] Frontend: Confidence badges render correctly
- [ ] Frontend: Explanation panel expands/collapses
- [ ] Frontend: Dashboard loads and displays data
- [ ] Mobile: All components responsive at 375px
- [ ] Console: No JavaScript errors

## Screenshots
[To be added after visual verification]

---
Generated with Claude Code
EOF
)"

# Get PR URL
gh pr view --web
```

OUTPUT: PR URL for review

### Agent 7B: Railway Preview Testing

**Tools**: Railway CLI, Chrome Extension

TASK: Test on Railway preview deployment.

PROCEDURE:
```bash
# Wait for Railway preview deploy (triggered by PR)
echo "Waiting for Railway preview deployment..."
sleep 120  # 2 minutes typical

# Get preview URL from PR or Railway dashboard
PREVIEW_URL=$(gh pr view --json url -q '.url' | sed 's/github.com/quoted-preview.up.railway.app/')
```

Then use Chrome extension to test preview:
```javascript
// Navigate to preview
mcp__claude-in-chrome__navigate({
    url: PREVIEW_URL,
    tabId: TAB_ID
})

// Full visual test cycle (same as Phase 6B)
// ...

// Verify no errors
mcp__claude-in-chrome__read_console_messages({
    tabId: TAB_ID,
    onlyErrors: true
})

// Check network for API calls
mcp__claude-in-chrome__read_network_requests({
    tabId: TAB_ID,
    urlPattern: "/api/learning"
})
```

OUTPUT: Preview test results
- All visual components working
- API calls successful
- No console errors

**PHASE 7 GATE**: Preview testing passes before merge.

---

## Phase 8: Merge & Deploy

**Agent Count**: 1
**Priority**: CRITICAL
**Dependencies**: Phase 7 complete

### Agent 8A: Merge and Monitor Deployment

**Tools**: GitHub CLI, Railway CLI

TASK: Merge PR and monitor production deployment.

PROCEDURE:
```bash
# Merge PR (squash for clean history)
gh pr merge --squash --delete-branch

# Monitor deployment
echo "Monitoring Railway deployment..."
railway logs --follow &
LOG_PID=$!

# Wait for deployment (typically 2-3 minutes)
sleep 180

# Check deployment status
railway status

# Stop log following
kill $LOG_PID

# Check for errors in recent logs
railway logs -n 200 --filter "@level:error"
```

SUCCESS CRITERIA:
- PR merged successfully
- Deployment completes without errors
- No error logs in first 3 minutes

**PHASE 8 GATE**: Production deployment successful.

---

## Phase 9: Production QA

**Agent Count**: 3
**Priority**: CRITICAL
**Dependencies**: Phase 8 complete

### Agent 9A: Production API Verification

**Tools**: Bash (curl)

TASK: Verify all new endpoints work in production.

PROCEDURE:
```bash
PROD_URL="https://quoted.it.com"

# Test confidence endpoint
echo "Testing production /api/learning/confidence..."
curl -s -X GET "$PROD_URL/api/learning/confidence/bathroom_remodel" \
  -H "Authorization: Bearer $PROD_TOKEN" | jq .

# Test progress endpoint
echo "Testing production /api/learning/progress..."
curl -s -X GET "$PROD_URL/api/learning/progress" \
  -H "Authorization: Bearer $PROD_TOKEN" | jq .

# Test feedback endpoint
echo "Testing production /api/learning/feedback..."
curl -s -X POST "$PROD_URL/api/learning/feedback" \
  -H "Authorization: Bearer $PROD_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "original_price": 100,
    "new_price": 110,
    "category": "test",
    "edit_type": "increase",
    "edit_percentage": 10,
    "feedback_reason": "test",
    "timestamp": "2025-01-01T00:00:00Z"
  }' | jq .
```

OUTPUT: Production API test results

### Agent 9B: Production Visual QA

**Tools**: Chrome Extension

TASK: Full visual verification on production.

PROCEDURE:
```javascript
// Navigate to production
mcp__claude-in-chrome__navigate({
    url: "https://quoted.it.com",
    tabId: TAB_ID
})

// Login as test user
// ... login steps ...

// Screenshot quote list with confidence badges
mcp__claude-in-chrome__computer({
    action: "screenshot",
    tabId: TAB_ID
})

// Navigate to learning dashboard
mcp__claude-in-chrome__find({
    query: "AI Learning",
    tabId: TAB_ID
})
mcp__claude-in-chrome__computer({
    action: "left_click",
    ref: REF_ID,
    tabId: TAB_ID
})

// Screenshot dashboard
mcp__claude-in-chrome__computer({
    action: "screenshot",
    tabId: TAB_ID
})

// Test mobile
mcp__claude-in-chrome__resize_window({
    width: 375,
    height: 812,
    tabId: TAB_ID
})
mcp__claude-in-chrome__computer({
    action: "screenshot",
    tabId: TAB_ID
})

// Check errors
mcp__claude-in-chrome__read_console_messages({
    tabId: TAB_ID,
    onlyErrors: true
})
```

OUTPUT: Production screenshots and error report

### Agent 9C: End-to-End User Journey

**Tools**: Chrome Extension

TASK: Complete user journey testing the full learning loop.

PROCEDURE:
1. Create new quote via voice or text
2. Verify confidence badge appears on quote card
3. View quote details - verify explanation panel
4. Edit a price - verify feedback prompt appears
5. Send quote - verify acceptance learning triggered
6. Check learning dashboard - verify stats updated

OUTPUT: User journey test results
| Step | Expected | Actual | Pass |
|------|----------|--------|------|

**PHASE 9 GATE**: All production tests pass.

---

## Phase 10: Documentation & Metrics

**Agent Count**: 2
**Priority**: MEDIUM
**Dependencies**: Phase 9 complete

### Agent 10A: Update Documentation

**Target**: `ENGINEERING_STATE.md`, `COMPANY_STATE.md`

TASK: Document completed features and update state files.

CHANGES:
1. Add to ENGINEERING_STATE.md:
```markdown
### Anthropic Showcase Learning (DEPLOYED)
- Confidence badges on quote cards
- Pricing explanation panels
- Learning dashboard with progress visualization
- Structured correction feedback loops
- Acceptance learning signal logging

API Endpoints:
- GET /api/learning/confidence/{category}
- GET /api/learning/explanation/{quote_id}
- POST /api/learning/feedback
```

2. Add to COMPANY_STATE.md competitive moat section:
```markdown
### AI Learning Transparency (Anthropic Showcase Quality)
- Every price explained with source attribution
- Confidence badges show AI certainty
- Learning dashboard visualizes improvement
- Correction feedback improves future accuracy
```

### Agent 10B: Capture Metrics Baseline

**Tools**: PostHog, Railway logs

TASK: Document baseline metrics for measuring impact.

METRICS TO CAPTURE:
- Current average confidence score
- Number of categories with high confidence
- Edit rate (% of quotes with price edits)
- Feedback submission rate
- Dashboard page views

PROCEDURE:
```bash
# Check PostHog for current metrics
# (Manual step - document in state file)

# Log baseline to state file
echo "
## Metrics Baseline ($(date))
- Average confidence: TBD
- High-confidence categories: TBD
- Quote edit rate: TBD
- Feedback submissions: TBD
- Dashboard views: TBD
" >> .claude/anthropic-showcase-state.md
```

**PHASE 10 GATE**: Documentation complete, metrics baseline captured.

---

## Rollback Procedures

### Phase 1-5 Rollback (Pre-Merge)
```bash
# Delete feature branch
git checkout main
git branch -D feat/anthropic-showcase-learning
git push origin --delete feat/anthropic-showcase-learning
```

### Post-Merge Rollback
```bash
# Revert merge commit
git revert -m 1 <merge_commit_sha>
git push origin main

# Railway will auto-deploy the revert
```

### Partial Feature Rollback
If specific features cause issues:
1. Comment out problematic code
2. Create hotfix PR
3. Merge and deploy

---

## Resume Procedures

### After Context Reset
1. Read `.claude/anthropic-showcase-state.md`
2. Check current git branch: `git branch --show-current`
3. Check PR status: `gh pr status`
4. Resume from last incomplete phase

### After Failure
1. Read state file for last successful phase
2. Check Railway logs: `railway logs -n 200`
3. Fix issues before resuming
4. Update state file with fix notes

---

## Success Metrics

### Technical Success
- [ ] All 4 API endpoints functional
- [ ] Confidence badges render on all quotes
- [ ] Explanation panels expand/collapse correctly
- [ ] Dashboard shows real learning progress
- [ ] Feedback captures structured corrections
- [ ] No console errors in production
- [ ] Mobile responsive at 375px

### Anthropic Showcase Quality
- [ ] Every price has traceable explanation
- [ ] Confidence reflects actual data quality
- [ ] User corrections feed learning system
- [ ] Learning progress visible to users
- [ ] AI behavior interpretable and honest

### Business Impact (Measure After 30 Days)
- Quote edit rate decreases (AI accuracy)
- User engagement with dashboard
- Feedback submission rate
- Confidence scores improve over time
