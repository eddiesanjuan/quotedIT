# AI Civilization Status

Display the current status of the AI Civilization system.

---

## Instructions

1. Read .ai-company/state/current.md
2. Read .ai-company/queues/decisions.md (count pending)
3. Read .ai-company/queues/events.md (count pending)
4. Read each agent's state.md:
   - .ai-company/agents/support/state.md
   - .ai-company/agents/ops/state.md
   - .ai-company/agents/code/state.md
   - .ai-company/agents/growth/state.md
   - .ai-company/agents/meta/state.md

5. Check GitHub Actions recent runs:
   ```bash
   gh run list --limit 10
   ```

6. Display formatted status:

```
+--------------------------------------------------------------+
|                   AI CIVILIZATION STATUS                      |
+--------------------------------------------------------------+

## System Health: {GREEN/YELLOW/RED}

Based on:
- All agents reporting OK = GREEN
- Minor issues = YELLOW
- Active incidents or agent failures = RED

## Pending Items
- Decisions awaiting Eddie: {count from decisions.md}
- Events in queue: {count from events.md}
- Active incidents: {count from .ai-company/incidents/}

## Agent Status
| Agent   | Status     | Last Run      | Queue | Success |
|---------|------------|---------------|-------|---------|
| Support | {status}   | {timestamp}   | {n}   | {rate}% |
| Ops     | {status}   | {timestamp}   | {n}   | {rate}% |
| Code    | {status}   | {timestamp}   | {n}   | {rate}% |
| Growth  | {status}   | {timestamp}   | {n}   | {rate}% |
| Meta    | {status}   | {timestamp}   | {n}   | {rate}% |

## Recent Activity
{last 5 entries from .ai-company/logs/}

## GitHub Actions (Last 5)
{from gh run list output}

## Quick Actions
- /ai-decide     Process pending decisions
- /ai-run        Trigger agent run
- /ai-briefing   Generate briefing

+--------------------------------------------------------------+
```

## Notes

- Status values: IDLE, RUNNING, ERROR, DISABLED
- Success rate calculated from logs
- Last Run shows relative time (e.g., "2 hours ago")
