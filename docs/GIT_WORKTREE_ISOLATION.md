# Git Worktree Isolation for Autonomous Operations

**DISC-104**: Work isolation via git worktrees for safer parallel autonomous work

---

## Overview

When multiple AI agents or autonomous cycles run in parallel, they risk contaminating each other's work. Git worktrees provide isolated working directories where each task operates independently. Failures in one worktree don't affect others.

## Why Worktrees?

| Problem | Worktree Solution |
|---------|-------------------|
| Uncommitted changes from Task A affect Task B | Each task has separate working directory |
| Failed task leaves repo in dirty state | Just delete the worktree, main stays clean |
| Can't run parallel tasks | Each worktree is independent |
| Branch switching interrupts work | Each worktree is on its own branch |
| Rollback is complex | Worktree deletion is instant rollback |

## Architecture

```
quoted/                          # Main working tree (main branch)
├── .git/                        # Shared git database
└── ...

/tmp/quoted-worktrees/           # Worktree directory (outside repo)
├── disc-104/                    # Worktree for DISC-104
│   ├── .git (file -> quoted/.git/worktrees/disc-104)
│   └── ...
├── disc-106/                    # Worktree for DISC-106
│   └── ...
└── hotfix-auth/                 # Worktree for urgent hotfix
    └── ...
```

## Quick Reference

### Creating a Worktree

```bash
# Create worktree for a ticket (from main quoted directory)
cd /Users/eddiesanjuan/Personal_Assistant/Eddie_Personal_Assistant/quoted

# Create new branch AND worktree in one command
git worktree add -b feat/disc-XXX ../quoted-worktrees/disc-XXX main

# Or create worktree from existing branch
git worktree add ../quoted-worktrees/disc-XXX feat/disc-XXX
```

### Working in a Worktree

```bash
# Navigate to worktree
cd /tmp/quoted-worktrees/disc-XXX

# Work normally - all git commands work
git status
git add .
git commit -m "feat: implement DISC-XXX"
git push -u origin feat/disc-XXX
```

### Completing Work

```bash
# After PR merged, clean up worktree
cd /Users/eddiesanjuan/Personal_Assistant/Eddie_Personal_Assistant/quoted
git worktree remove ../quoted-worktrees/disc-XXX

# Or force remove if there are uncommitted changes
git worktree remove --force ../quoted-worktrees/disc-XXX

# Clean up the branch too
git branch -d feat/disc-XXX
```

### Listing Worktrees

```bash
git worktree list
# /Users/.../quoted                    abc1234 [main]
# /tmp/quoted-worktrees/disc-104       def5678 [feat/disc-104]
# /tmp/quoted-worktrees/disc-106       ghi9012 [feat/disc-106]
```

## Agent Integration

### For Code Agent

The Code Agent should use worktrees for each task to prevent cross-contamination:

```python
# Pseudocode for agent worktree management
def start_task(ticket_id: str) -> Path:
    """Create isolated worktree for task."""
    worktree_path = Path(f"/tmp/quoted-worktrees/{ticket_id}")
    branch_name = f"feat/{ticket_id.lower()}"

    # Create worktree with new branch
    subprocess.run([
        "git", "worktree", "add",
        "-b", branch_name,
        str(worktree_path),
        "main"
    ], cwd=MAIN_REPO_PATH)

    return worktree_path

def complete_task(ticket_id: str, success: bool):
    """Clean up worktree after task."""
    worktree_path = f"/tmp/quoted-worktrees/{ticket_id}"

    if success:
        # Create PR, then clean up
        subprocess.run(["git", "push", "-u", "origin", f"feat/{ticket_id}"],
                      cwd=worktree_path)
        # PR creation here...

    # Always clean up worktree
    subprocess.run(["git", "worktree", "remove", worktree_path],
                  cwd=MAIN_REPO_PATH)

def rollback_task(ticket_id: str):
    """Abort task and clean up."""
    worktree_path = f"/tmp/quoted-worktrees/{ticket_id}"

    # Force remove (discards all changes)
    subprocess.run(["git", "worktree", "remove", "--force", worktree_path],
                  cwd=MAIN_REPO_PATH)

    # Delete branch if it exists
    subprocess.run(["git", "branch", "-D", f"feat/{ticket_id}"],
                  cwd=MAIN_REPO_PATH)
```

### For /quoted-run Command

Update the autonomous run workflow:

```
Phase 2: Task Preparation
├── Step 2.3: Create isolated worktree
│   ├── git worktree add -b feat/{ticket} /tmp/quoted-worktrees/{ticket} main
│   └── cd to worktree directory
└── Step 2.4: Verify isolation
    └── Confirm we're in worktree, not main

Phase 3: Execution
├── All changes happen in worktree
├── Tests run in worktree
└── On failure: Clean up worktree (no main pollution)

Phase 4: Integration
├── Step 4.1: Push branch to origin
├── Step 4.2: Create PR
├── Step 4.3: Wait for Railway preview
└── Step 4.4: Run verification checklist

Phase 5: Cleanup
├── After PR merged: git worktree remove
└── Delete feature branch
```

## Benefits

### 1. Instant Rollback

If a task fails mid-implementation:
```bash
# Discard all changes instantly
git worktree remove --force /tmp/quoted-worktrees/disc-XXX
```
Main repository is untouched. No need to reset, stash, or clean.

### 2. Parallel Execution

Run multiple agents simultaneously:
```
Agent 1: Working on DISC-104 in /tmp/quoted-worktrees/disc-104
Agent 2: Working on DISC-106 in /tmp/quoted-worktrees/disc-106
Agent 3: Working on hotfix in /tmp/quoted-worktrees/hotfix-auth
```
Each has full repo access, none interfere with others.

### 3. Clean Main Always

The main working directory (`/Users/.../quoted`) stays on `main` branch, always clean. No dirty state from failed tasks.

### 4. Merge Only on Success

Changes only reach `main` after:
1. Implementation complete
2. Tests pass
3. PR created
4. Railway preview verified
5. Human approval (for sensitive changes)

## Worktree Hygiene

### Recommended Directory Structure

```bash
# Create worktree parent directory
mkdir -p /tmp/quoted-worktrees

# Or use a more persistent location
mkdir -p ~/quoted-worktrees
```

### Cleanup Stale Worktrees

```bash
# List all worktrees
git worktree list

# Prune worktrees whose directories no longer exist
git worktree prune

# Remove specific stale worktree
git worktree remove /path/to/worktree
```

### Worktree Lifecycle

```
CREATE ──────────────────────────────────────────────────────> REMOVE
   │                                                              │
   │  git worktree add                       git worktree remove  │
   │                                                              │
   └── work ── commit ── push ── PR ── verify ── merge ──────────┘
```

## Error Handling

### Worktree Already Exists

```bash
# Error: worktree is already locked
# Solution: Remove and recreate
git worktree remove /tmp/quoted-worktrees/disc-XXX
git worktree add -b feat/disc-XXX /tmp/quoted-worktrees/disc-XXX main
```

### Branch Already Exists

```bash
# Error: branch already exists
# Solution: Use existing branch
git worktree add /tmp/quoted-worktrees/disc-XXX feat/disc-XXX
```

### Dirty Worktree

```bash
# Error: worktree has uncommitted changes
# Solution: Force remove (use only if changes should be discarded)
git worktree remove --force /tmp/quoted-worktrees/disc-XXX
```

## Integration with Existing Protocols

### With Regression Gate (DISC-108)

Run regression tests in the worktree before pushing:
```bash
cd /tmp/quoted-worktrees/disc-XXX/backend
pytest -x --tb=short
# Only push if tests pass
```

### With LLM-as-Judge (DISC-101)

Judge evaluation happens before PR creation:
```bash
cd /tmp/quoted-worktrees/disc-XXX
git diff main...HEAD  # Show what will be in PR
# Judge evaluates this diff
# Score >= 4.0 -> Create PR
# Score < 4.0 -> Clean up worktree, escalate
```

### With HANDOFF.md (DISC-107)

Log worktree status in handoff:
```markdown
## Active Worktrees
| Ticket | Path | Status |
|--------|------|--------|
| DISC-104 | /tmp/quoted-worktrees/disc-104 | PR created, awaiting review |
| DISC-106 | /tmp/quoted-worktrees/disc-106 | Implementation in progress |
```

---

*Created: 2026-01-05 | DISC-104*
