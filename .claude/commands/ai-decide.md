# AI Civilization - Decision Queue

Process pending decisions that require Eddie's input.

---

## Instructions

1. Read .ai-company/queues/decisions.md
2. If no pending decisions, display "No decisions pending" and exit
3. For each pending decision:
   a. Display the decision context
   b. Show options with AI recommendation
   c. Ask Eddie for decision using AskUserQuestion tool
   d. Record decision and reasoning
   e. Move to completed queue
4. Update state files

## Decision Display Format

For each decision, show:

```
+--------------------------------------------------------------+
|  DECISION {N} of {total}: {title}                            |
+--------------------------------------------------------------+

**Urgency**: {CRITICAL/HIGH/MEDIUM/LOW}
**From**: {agent name}
**Submitted**: {timestamp}

### Context
{full context from the decision}

### Options
1. {option 1} - {impact description}
2. {option 2} - {impact description}
3. {option 3} - {impact description}

### AI Recommendation
{recommendation} (confidence: {0.X})
**Reasoning**: {reasoning}

+--------------------------------------------------------------+
```

## After Decision

1. Log decision to .ai-company/logs/decisions/{date}.md with format:
   ```markdown
   ## Decision: {title}
   - **Time**: {timestamp}
   - **Choice**: {option selected}
   - **Reasoning**: {Eddie's reasoning if provided}
   - **Original Recommendation**: {AI recommendation}
   ```

2. Remove from .ai-company/queues/decisions.md

3. If decision triggers action, add to .ai-company/queues/actions.md

4. Notify originating agent by updating their inbox:
   .ai-company/agents/{agent}/inbox.md

5. Update metrics in agent state file

## Decision Types

Common decisions Eddie may need to approve:
- Email template for first-time use
- Code PR merges
- Spec changes from Meta Agent
- Refund requests
- Feature flag toggles
- Incident response escalations
