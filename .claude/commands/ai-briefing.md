# AI Civilization - Generate Briefing

Generate an on-demand briefing for the AI Civilization system.

---

## Arguments

Parse from $ARGUMENTS:
- `type`: briefing type (morning, evening, status, full)
  - Default: status (quick overview)

## Usage Examples

```
/ai-briefing              # Quick status briefing
/ai-briefing morning      # Full morning briefing format
/ai-briefing evening      # Full evening summary format
/ai-briefing full         # Comprehensive system report
```

## Instructions

### For "status" (default)

Quick 30-second overview:

1. Read .ai-company/state/current.md
2. Count pending decisions from .ai-company/queues/decisions.md
3. Check for active incidents in .ai-company/incidents/
4. Get last activity from each agent's state.md

Display:
```
+--------------------------------------------------------------+
|  QUICK BRIEFING                                               |
+--------------------------------------------------------------+

System: {GREEN/YELLOW/RED}
Pending Decisions: {N}
Active Incidents: {N}

Last 3 Agent Activities:
- {agent}: {action} ({time ago})
- {agent}: {action} ({time ago})
- {agent}: {action} ({time ago})

Need attention: {yes/no with reason}
+--------------------------------------------------------------+
```

### For "morning"

Full morning briefing format:

1. Read all agent states from .ai-company/agents/*/state.md
2. Read pending decisions from .ai-company/queues/decisions.md
3. Read yesterday's metrics from .ai-company/state/daily/
4. Check overnight logs for anomalies

Display:
```
+--------------------------------------------------------------+
|  MORNING BRIEFING - {date}                                    |
+--------------------------------------------------------------+

## OVERNIGHT SUMMARY
- Events processed: {N}
- Agent actions taken: {N}
- Incidents: {N}
- Anomalies detected: {list}

## DECISIONS NEEDED ({N})
{prioritized list with urgency}

## TODAY'S FOCUS
- Scheduled events: {list}
- Metrics to watch: {list}
- Recommended priorities: {list}

## WINS & CONCERNS
Wins: {list}
Concerns: {list}
+--------------------------------------------------------------+
```

### For "evening"

Full evening summary format:

1. Read all agent states
2. Read today's events from .ai-company/state/daily/
3. Read the morning briefing if available
4. Calculate day's metrics

Display:
```
+--------------------------------------------------------------+
|  EVENING SUMMARY - {date}                                     |
+--------------------------------------------------------------+

## TODAY'S ACCOMPLISHMENTS
- Quotes generated: {N}
- Users active: {N}
- Agent actions: {N}
- PRs created/merged: {N}

## METRICS SNAPSHOT
{key numbers with comparisons}

## OVERNIGHT PLANS
{what agents will do while sleeping}

## OPEN ITEMS
{decisions still pending, new items}
+--------------------------------------------------------------+
```

### For "full"

Comprehensive system report:

1. Run all briefing types
2. Add system health details
3. Include recent GitHub Actions results
4. Show full agent queue states

## Notes

- Briefings are generated locally, not via GitHub Actions
- For automated briefings, use /ai-run morning or /ai-run evening
- This command is for on-demand quick insights
