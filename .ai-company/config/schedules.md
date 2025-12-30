# Operating Rhythm Configuration

## Daily Schedule

### Autonomous Operations (24/7)

| Time | Activity | Agent | Notes |
|------|----------|-------|-------|
| Every 30 min | Event processing loop | All | GitHub Actions |
| Continuous | Log monitoring | Ops | Background |
| Continuous | Event ingestion | Brain | Railway endpoint |

### Human Touchpoints

| Time | Activity | Duration | Purpose |
|------|----------|----------|---------|
| 6:00 AM | Morning briefing | 5-10 min | Review decisions, set priorities |
| 6:00 PM | Evening summary | 2-5 min | Review day, urgent items |
| Async | Critical alerts | As needed | SMS for urgent items |

## Scheduled Jobs

### Every 30 Minutes (Main Loop)

```yaml
job: ai-company-loop
trigger: "*/30 * * * *"
timeout: 10 minutes
actions:
  - fetch_pending_events
  - process_events_by_priority
  - run_agent_tasks
  - update_state
  - generate_decisions
  - send_notifications (if any)
  - clean_processed_events
```

### Morning Briefing (6:00 AM)

```yaml
job: ai-company-morning
trigger: "0 6 * * *"
timeout: 5 minutes
actions:
  - compile_overnight_events
  - summarize_decision_queue
  - generate_metrics_snapshot
  - create_priority_list
  - send_briefing_email
  - prepare_quick_action_links
```

### Evening Summary (6:00 PM)

```yaml
job: ai-company-evening
trigger: "0 18 * * *"
timeout: 5 minutes
actions:
  - summarize_day_activity
  - check_pending_decisions
  - highlight_unresolved_items
  - generate_tomorrow_preview
  - send_summary_email
```

### Weekly Review (Sunday 6:00 PM)

```yaml
job: ai-company-weekly
trigger: "0 18 * * 0"
timeout: 15 minutes
actions:
  - generate_weekly_metrics
  - analyze_trends
  - review_agent_performance
  - identify_process_improvements
  - compile_strategic_items
  - send_weekly_report
```

### Urgent Handler (On-Demand)

```yaml
job: ai-company-urgent
trigger: workflow_dispatch
timeout: 5 minutes
actions:
  - process_critical_event
  - send_immediate_notification
  - prepare_response_options
  - update_incident_status
```

## Event Priority Processing

### Processing Order

```
1. CRITICAL (immediate)
   - System down
   - Security events
   - Angry customers
   - Payment disputes

2. HIGH (within 30 min loop)
   - Payment failures
   - Bug reports
   - Churn signals

3. MEDIUM (batched)
   - Support questions
   - Feedback
   - Feature requests

4. LOW (weekly)
   - General metrics
   - Non-urgent improvements
   - Long-term planning
```

### Batch Processing Rules

```yaml
batching:
  # Group similar events
  group_by_customer: true
  group_by_type: true
  max_batch_size: 10

  # Timing
  batch_window_minutes: 30
  force_process_after_hours: 4

  # Exceptions (never batch)
  never_batch:
    - critical_events
    - payment_events
    - security_events
```

## Maintenance Windows

### Daily Maintenance (4:00 AM)

```yaml
maintenance_daily:
  time: "04:00"
  duration_minutes: 15
  actions:
    - rotate_logs
    - clean_temp_files
    - archive_old_events
    - update_metrics_cache
```

### Weekly Maintenance (Sunday 4:00 AM)

```yaml
maintenance_weekly:
  time: "Sunday 04:00"
  duration_minutes: 30
  actions:
    - full_log_rotation
    - archive_completed_decisions
    - generate_weekly_backup
    - update_knowledge_base_index
```

## Quiet Hours

```yaml
quiet_hours:
  start: "22:00"
  end: "07:00"
  timezone: "America/New_York"

  # What changes during quiet hours
  reduced_processing: true
  batch_non_critical: true
  delay_notifications: true

  # Exceptions (always notify)
  override_for:
    - critical_events
    - system_down
    - security_incidents
    - revenue_threshold: 100  # > $100 impact
```

## Holiday Schedule

```yaml
holidays:
  # US holidays (reduced operations)
  reduced_days:
    - "New Year's Day"
    - "Memorial Day"
    - "Independence Day"
    - "Labor Day"
    - "Thanksgiving"
    - "Christmas"

  # What changes on holidays
  holiday_mode:
    morning_briefing: false
    evening_summary: false
    batch_all_non_critical: true
    critical_only_notifications: true
```

## Response Time Goals

### By Priority

| Priority | First Response | Resolution |
|----------|---------------|------------|
| CRITICAL | 5 minutes | 1 hour |
| HIGH | 30 minutes | 4 hours |
| MEDIUM | 4 hours | 24 hours |
| LOW | 24 hours | 1 week |

### By Type

| Type | Target Response | Target Resolution |
|------|-----------------|-------------------|
| Support ticket | 4 hours | 24 hours |
| Bug report | 1 hour | 48 hours |
| Feature request | 24 hours | Logged only |
| Payment issue | 30 minutes | 4 hours |
| Security event | 5 minutes | Until resolved |

## Capacity Planning

### Processing Limits

```yaml
capacity:
  # Per 30-minute run
  max_events_per_run: 50
  max_decisions_generated: 10
  max_emails_sent: 10
  max_api_calls: 100

  # Daily totals
  max_decisions_per_day: 100
  max_emails_per_day: 50
  max_support_responses: 20

  # If limits hit
  overflow_action: "queue_for_next_run"
  alert_at_percent: 80
```

### Scaling Triggers

```yaml
scaling:
  # When to increase processing
  increase_frequency_if:
    - queue_depth: 100
    - critical_events_pending: 5
    - response_time_exceeded: true

  # How to scale
  scale_actions:
    - reduce_loop_interval: 15  # minutes
    - prioritize_critical: true
    - defer_non_essential: true
```
