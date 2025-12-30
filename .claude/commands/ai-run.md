# AI Civilization - Trigger Agent Run

Manually trigger an agent workflow.

---

## Arguments

Parse from $ARGUMENTS:
- `agent`: Which agent to run (support, ops, code, growth, meta, loop, urgent)
- `task`: Optional specific task for the agent

## Usage Examples

```
/ai-run support           # Run support agent
/ai-run ops               # Run ops agent
/ai-run code              # Run code agent
/ai-run code BUG-001      # Run code agent on specific bug
/ai-run growth            # Run growth agent
/ai-run meta              # Run meta agent (weekly improvement)
/ai-run loop              # Run main coordination loop
/ai-run urgent            # Run urgent handler
/ai-run morning           # Generate morning briefing
/ai-run evening           # Generate evening summary
```

## Instructions

1. Parse $ARGUMENTS to get agent name and optional task

2. Validate agent name is one of:
   - support, ops, code, growth, meta, loop, urgent, morning, evening

3. Map agent to workflow:
   ```
   support  → ai-civilization-support.yml
   ops      → ai-civilization-ops.yml
   code     → ai-civilization-code.yml
   growth   → ai-civilization-growth.yml
   meta     → ai-civilization-meta.yml
   loop     → ai-civilization-loop.yml
   urgent   → ai-civilization-urgent.yml
   morning  → ai-civilization-morning.yml
   evening  → ai-civilization-evening.yml
   ```

4. Trigger GitHub Action:
   ```bash
   # Without task
   gh workflow run ai-civilization-{agent}.yml

   # With task (if supported by workflow)
   gh workflow run ai-civilization-{agent}.yml -f task="{task}"
   ```

5. Get the run ID:
   ```bash
   gh run list --workflow ai-civilization-{agent}.yml --limit 1 --json databaseId -q '.[0].databaseId'
   ```

6. Display status:
   ```bash
   gh run view {run_id}
   ```

7. Ask Eddie if they want to watch the run:
   ```bash
   gh run watch {run_id}
   ```

## Output Format

```
+--------------------------------------------------------------+
|  AI AGENT TRIGGERED                                           |
+--------------------------------------------------------------+

Agent: {agent name}
Workflow: ai-civilization-{agent}.yml
Task: {task or "none specified"}

Run ID: {run_id}
Status: {queued/in_progress}
URL: {github actions url}

Watch progress? (gh run watch {run_id})
+--------------------------------------------------------------+
```

## Error Handling

If workflow fails to trigger:
1. Check if AI_COMPANY_ENABLED var is set to 'true'
2. Verify workflow file exists
3. Check GitHub token permissions
