# Support Queue

**Last Updated**: 2025-12-01 22:35 PST
**Updated By**: Support Manager (AI)

---

## Queue Summary

| Status | Count |
|--------|-------|
| New | 0 |
| In Progress | 0 |
| Waiting on Customer | 0 |
| Resolved Today | 0 |

**SLA Status**: All tickets within SLA

---

## Active Tickets

| ID | Customer | Issue | Priority | Status | Assignee | Age | SLA |
|----|----------|-------|----------|--------|----------|-----|-----|
| - | - | No active tickets | - | - | - | - | - |

---

## Waiting on Customer

| ID | Customer | Last Contact | Days Waiting | Next Action |
|----|----------|--------------|--------------|-------------|
| - | - | - | - | - |

---

## Escalated to Engineering

| ID | Issue | Engineering Ticket | Status | ETA |
|----|-------|--------------------|--------|-----|
| - | - | - | - | - |

---

## Resolved This Week

| ID | Customer | Issue | Resolution Time | Resolution |
|----|----------|-------|-----------------|------------|
| - | - | No resolved tickets this week | - | - |

---

## Metrics (This Week)

| Metric | Value |
|--------|-------|
| Tickets Opened | 0 |
| Tickets Resolved | 0 |
| Avg Response Time | - |
| Avg Resolution Time | - |
| CSAT | - |
| Escalation Rate | - |

---

## Common Issues

| Issue | Count | KB Article | Auto-Reply |
|-------|-------|------------|------------|
| - | - | - | - |

*No patterns detected yet - awaiting first users*

---

## Support Processes

### Ticket Flow
```
User reports issue (in-app or /api/issues)
         │
         ▼
   Tier 1 Triage (< 2 hours)
         │
    ┌────┴────┐
    │         │
    ▼         ▼
 Resolve   Escalate
  (80%)      (20%)
    │         │
    │    ┌────┴────┐
    │    │         │
    │    ▼         ▼
    │  Tier 2   Engineering
    │  (15%)     (5%)
    │    │         │
    └────┴────┬────┘
              │
              ▼
         Resolution
              │
              ▼
    Customer Notification
```

### SLAs
- **First Response**: < 2 hours (business hours)
- **Tier 1 Resolution**: < 24 hours
- **Tier 2 Resolution**: < 48 hours
- **Engineering Escalation**: < 72 hours
- **Critical Issues**: < 4 hours

### Issue Categories
- `bug` - Something broken
- `feature_request` - New capability request
- `ui_issue` - Visual/UX problem
- `pricing_issue` - Quote accuracy problem
- `onboarding_issue` - Setup problems

### Severity Levels
- `critical` - Product unusable, data loss
- `high` - Major feature broken
- `medium` - Minor feature issue
- `low` - Cosmetic, edge case

---

## API Integration

Issues are submitted via `/api/issues`:
```bash
# Get new issues to process
GET /api/issues/new

# Claim an issue
POST /api/issues/{id}/claim

# Update with analysis/solution
PATCH /api/issues/{id}
{
  "status": "resolved",
  "agent_analysis": "...",
  "agent_solution": "...",
  "files_modified": ["..."]
}
```

---

## Knowledge Base Articles (To Create)

| Topic | Priority | Status |
|-------|----------|--------|
| How to use voice recording | HIGH | NOT STARTED |
| How onboarding works | HIGH | NOT STARTED |
| How to edit quotes | MEDIUM | NOT STARTED |
| How learning improves over time | MEDIUM | NOT STARTED |
| PDF export guide | LOW | NOT STARTED |
