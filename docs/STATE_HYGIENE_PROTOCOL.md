# State Hygiene Protocol

**Purpose**: Keep Quoted state files lean and current to preserve AI context budget.
**Applies To**: All autonomous skills (`/quoted-run`, `/quoted-discover`, etc.)

---

## Quick Reference

| File | Target Size | Check | Action When Exceeded |
|------|-------------|-------|---------------------|
| `DISCOVERY_BACKLOG.md` | <500 lines | Each `/quoted-run` | Archive DEPLOYED tickets |
| `DISCOVERY_ARCHIVE.md` | Unlimited | Append-only | N/A |
| `COMPANY_STATE.md` | <300 lines | Weekly | Update stale metrics |
| `ENGINEERING_STATE.md` | <250 lines | Each deploy | Update Recently Deployed |

---

## Why This Matters

**Problem**: State files grow unbounded. A 2,500-line backlog consumes ~27,000 tokens (13% of context).

**Solution**: Active/Archive split + automated hygiene checks.

**Result**: ~5,000 tokens for backlog, preserving 22,000 tokens for actual work.

---

## The Two-File Pattern

### Active File: `DISCOVERY_BACKLOG.md`
- Contains ONLY: READY, DISCOVERED, COMPLETE tickets
- Recently Deployed section: Last 5 tickets as table (brief)
- **Target**: <500 lines (~5,000 tokens)

### Archive File: `DISCOVERY_ARCHIVE.md`
- Contains ALL DEPLOYED tickets organized by category
- Searchable for "have we done this?" checks
- Append-only (never delete from archive)

---

## Hygiene Actions

### 1. Archive DEPLOYED Tickets (Each `/quoted-run`)

**When**: DISCOVERY_BACKLOG.md exceeds 500 lines OR has DEPLOYED tickets older than 2 weeks

**Steps**:
1. Identify DEPLOYED tickets older than 2 weeks
2. Move to appropriate category in DISCOVERY_ARCHIVE.md
3. Remove from DISCOVERY_BACKLOG.md (keep in Recently Deployed table only)
4. Update summary counts

**Example**:
```markdown
# DISCOVERY_ARCHIVE.md (add to relevant category)
| DISC-098 | Simplified Single-Tier Pricing ($9/mo) | 2025-12-19 |
```

### 2. Update Recently Deployed (After each deployment)

**In DISCOVERY_BACKLOG.md**:
- Keep only last 5 deployed tickets as table
- Newest first
- Brief format: Ticket | Title | Date

### 3. Validate COMPANY_STATE.md (Weekly or if referenced)

**Check for staleness**:
- Pricing info matches current reality
- User metrics are recent (<1 week old)
- Strategic priorities match current focus

**Fix**: Update stale sections, add "Last verified: YYYY-MM-DD"

### 4. Validate ENGINEERING_STATE.md (After each deployment)

**Check**:
- Recently Deployed section current
- Sprint info matches reality
- Product Reality table accurate

---

## Integration with `/quoted-run`

Add to Phase 0 (Orient):

```bash
# Step 0.0: State Hygiene Check
BACKLOG_LINES=$(wc -l < quoted/DISCOVERY_BACKLOG.md)
if [ $BACKLOG_LINES -gt 500 ]; then
  echo "[$(date '+%H:%M:%S')] ⚠️ BACKLOG HYGIENE NEEDED ($BACKLOG_LINES lines)" >> quoted/QUOTED_RUN_LIVE.md
  # Trigger archive operation before proceeding
fi
```

Add to Phase 7 (State Update):

```markdown
### Step 7.0: Archive Old DEPLOYED Tickets

For any ticket marked DEPLOYED more than 2 weeks ago:
1. Add to DISCOVERY_ARCHIVE.md under appropriate category
2. Remove full entry from DISCOVERY_BACKLOG.md
3. Keep in Recently Deployed table if within last 5

### Step 7.1: Update State Files
[existing steps...]
```

---

## For AI Agents: Pre-Run Checklist

Before starting any autonomous cycle:

1. Check DISCOVERY_BACKLOG.md line count
2. If >500 lines, run hygiene first
3. Check COMPANY_STATE.md pricing (compare to current landing page if uncertain)
4. Proceed with main task

---

## For AI Agents: Post-Run Checklist

After completing work:

1. Update ticket status in DISCOVERY_BACKLOG.md
2. If ticket now DEPLOYED, add to Recently Deployed table
3. If Recently Deployed > 5 entries, move oldest to archive
4. Update ENGINEERING_STATE.md Recently Deployed section
5. Commit state changes

---

## Duplicate Detection

Before creating new tickets, grep DISCOVERY_ARCHIVE.md:

```bash
grep -i "keyword" quoted/DISCOVERY_ARCHIVE.md
```

This prevents re-implementing features that already shipped.

---

## File Size Monitoring

Target sizes (in tokens, approximate):

| File | Healthy | Warning | Critical |
|------|---------|---------|----------|
| DISCOVERY_BACKLOG.md | <5,000 | 5,000-10,000 | >10,000 |
| ENGINEERING_STATE.md | <2,500 | 2,500-5,000 | >5,000 |
| COMPANY_STATE.md | <3,000 | 3,000-5,000 | >5,000 |

**Critical = immediate hygiene action required before proceeding**

---

*This protocol ensures state files don't consume excessive context, leaving maximum budget for actual work.*
