# Quoted Autonomous Development Cycle

You are executing an autonomous development cycle for Quoted. Follow this process exactly.

---

## PHASE 1: EXECUTIVE REVIEW

First, spawn a CEO agent to review current state and create an execution plan.

Use the Task tool with subagent_type "general-purpose" and this prompt:

```
You are the CEO of Quoted, an AI-powered quoting SaaS for contractors.

## Your Mission
Review the current state and decide what the engineering team should work on in this cycle.

## Step 1: Read State Files
Read these files to understand current status:
- COMPANY_STATE.md - Business goals and metrics
- ENGINEERING_STATE.md - Task backlog with full specifications
- BETA_SPRINT.md - Current sprint (100 users goal)
- ACTION_LOG.md - Recent activity

## Step 2: Strategic Assessment
Consider:
- Current sprint goal (100 users in 2 weeks)
- Which tier of tasks to focus on (Tier 1 blockers first)
- Dependencies between tasks
- What will have highest impact on the goal

## Step 3: Select Tasks
Pick 2-4 tasks for this cycle:
- Must be parallelizable (no dependencies on each other)
- Prioritize by impact on sprint goal
- Consider scope (don't overload a single cycle)

## Step 4: Create Execution Plan
Output your decision as JSON:

{
  "cycle_id": "[today's date]-[time]",
  "sprint_goal": "100 active beta testers by 2025-12-16",
  "rationale": "Why you chose these tasks",
  "tasks": [
    {
      "ticket_id": "TICKET-ID",
      "title": "Task title from ENGINEERING_STATE.md",
      "agent_type": "Backend Engineer | Frontend Engineer | Full Stack",
      "priority": 1,
      "why": "Why this task now"
    }
  ],
  "deferred": ["TICKET-IDs not selected and why"],
  "blockers_for_founder": ["Any decisions needed from founder"]
}

## Step 5: Update State Files
- In ENGINEERING_STATE.md, mark selected tasks as "IN PROGRESS"
- Add entry to ACTION_LOG.md: "[time] | CEO | Started autonomous cycle [cycle_id], selected [tasks]"

Return ONLY the JSON execution plan after updating files.
```

Wait for the CEO agent to complete and return the execution plan.

---

## PHASE 2: SPAWN EXECUTION AGENTS

Parse the CEO's execution plan. For EACH task in the `tasks` array, spawn an engineering agent IN PARALLEL.

Use the Task tool with subagent_type "general-purpose" for each task:

```
You are a [agent_type from plan] at Quoted.

## Your Assignment
Ticket: [ticket_id]
Title: [title]
Priority: [priority]

## Context
- Backend: FastAPI in backend/ (Python)
- Frontend: Single-page app in frontend/index.html (vanilla JS)
- Read ENGINEERING_STATE.md for full ticket specification
- Read BETA_SPRINT.md for detailed implementation requirements

## Your Process
1. Read the full ticket spec from ENGINEERING_STATE.md and/or BETA_SPRINT.md
2. Understand existing code patterns by reading related files
3. Implement the feature following existing conventions
4. Test that your changes work (run relevant commands)
5. Commit with descriptive message referencing the ticket ID

## Constraints
- Follow existing code patterns exactly
- Don't over-engineer - minimal changes to achieve the goal
- Commit frequently with clear messages
- If blocked, document what's blocking you

## Output
Return completion report as JSON:
{
  "ticket_id": "[ticket_id]",
  "status": "completed | partial | blocked",
  "commits": ["commit hashes"],
  "files_changed": ["paths"],
  "summary": "What you did",
  "blockers": ["If blocked, what's blocking"]
}
```

IMPORTANT: Spawn ALL task agents in a SINGLE message with multiple Task tool calls to run them in parallel.

---

## PHASE 3: COMPLETION

After all agents return:

1. **Collect Results**
   - Parse completion reports from each agent
   - Note successes, partial completions, and blockers

2. **Update State Files**
   - Mark completed tasks as COMPLETED in ENGINEERING_STATE.md
   - Update metrics in COMPANY_STATE.md if applicable
   - Add detailed entry to ACTION_LOG.md with all commits

3. **Push Changes**
   - Run: git push origin main

4. **Report to Founder**
   Summarize the cycle:
   - What was accomplished (with commit hashes)
   - Any blockers requiring human input
   - Recommended next priorities
   - Questions for the founder

---

## EXECUTION CHECKLIST

- [ ] Phase 1: Spawn CEO agent for review and planning
- [ ] Phase 1: CEO returns execution plan JSON
- [ ] Phase 2: Spawn ALL engineering agents in parallel (single message, multiple Task calls)
- [ ] Phase 2: Collect completion reports from all agents
- [ ] Phase 3: Update ENGINEERING_STATE.md with task statuses
- [ ] Phase 3: Update ACTION_LOG.md with cycle summary
- [ ] Phase 3: Push changes to git
- [ ] Phase 3: Report summary to founder

Begin Phase 1 now.
