# AI Company Configuration

## Core Settings

### Company Identity

```yaml
company_name: "Quoted, Inc."
product_url: "https://quoted.it.com"
support_email: "support@quoted.it.com"
founder: "Eddie San Juan"
timezone: "America/New_York"
```

### Operational Parameters

```yaml
# Execution timing
loop_interval_minutes: 30
morning_briefing_hour: 6
evening_summary_hour: 18
weekly_review_day: "Sunday"

# Response SLAs
sla_critical_minutes: 60
sla_high_hours: 4
sla_normal_hours: 24
sla_low_hours: 48

# Processing limits
max_events_per_run: 50
max_decisions_per_briefing: 10
max_actions_per_run: 20
```

### Decision Queue Settings

```yaml
# Auto-expiry for low-priority decisions
decision_ttl_days: 7

# Priority weights
priority_revenue_multiplier: 10  # $1 impact = 10 points
priority_urgency_base: 100      # Critical = 100, High = 50, etc.
priority_age_decay: 5           # Points per hour waiting

# Grouping
batch_similar_decisions: true
max_batch_size: 5
```

### Agent Settings

```yaml
support:
  enabled: true
  auto_acknowledge: true
  faq_confidence_threshold: 0.90
  sentiment_escalation_threshold: -0.5
  max_response_drafts: 5

ops:
  enabled: true
  monitoring_enabled: true
  auto_ticket_creation: true
  error_rate_alert_threshold: 0.05
  response_time_alert_ms: 1000

growth:
  enabled: true
  auto_scheduling: false  # Requires approval
  content_approval_required: true
  max_drafts_per_run: 3

finance:
  enabled: true
  daily_report: true
  weekly_report: true
  monthly_report: true
  refund_auto_approval: false  # Always require approval
  churn_alert_threshold: 2.0  # 2x normal
```

## Notification Settings

### SMS Notifications (Twilio)

```yaml
sms_enabled: true
sms_recipient: "+1XXXXXXXXXX"  # Eddie's phone

# What triggers SMS
sms_triggers:
  - "incident.critical"
  - "finance.dispute"
  - "support.angry_customer"
  - "ops.system_down"

# Quiet hours (no SMS unless critical)
quiet_hours_start: 22  # 10 PM
quiet_hours_end: 7     # 7 AM
quiet_hours_override_critical: true
```

### Email Notifications

```yaml
email_enabled: true
email_recipient: "eddie@quoted.it.com"

# Daily briefing
morning_briefing:
  enabled: true
  time: "06:00"
  include_decisions: true
  include_metrics: true
  include_alerts: true

# Evening summary
evening_summary:
  enabled: true
  time: "18:00"
  include_completed: true
  include_pending: true
  include_metrics: true
```

## Integration Settings

### Stripe

```yaml
stripe:
  enabled: true
  webhook_secret_env: "STRIPE_WEBHOOK_SECRET"
  events_to_process:
    - "customer.subscription.created"
    - "customer.subscription.deleted"
    - "customer.subscription.updated"
    - "invoice.paid"
    - "invoice.payment_failed"
    - "charge.refunded"
    - "charge.dispute.created"
```

### Resend

```yaml
resend:
  enabled: true
  api_key_env: "RESEND_API_KEY"
  from_email: "team@quoted.it.com"
  from_name: "Quoted"
  events_to_process:
    - "email.delivered"
    - "email.bounced"
    - "email.complained"
```

### Railway

```yaml
railway:
  enabled: true
  project_id_env: "RAILWAY_PROJECT_ID"
  log_fetch_interval_minutes: 15
  error_log_lookback_minutes: 30
```

### PostHog

```yaml
posthog:
  enabled: true
  api_key_env: "POSTHOG_API_KEY"
  project_id: "phc_xxxxxxxxxxxx"
  events_to_track:
    - "quote_generated"
    - "quote_sent"
    - "signup_completed"
    - "subscription_started"
```

### Claude API

```yaml
claude:
  model: "claude-sonnet-4-20250514"
  max_tokens: 4096
  api_key_env: "ANTHROPIC_API_KEY"
```

## Feature Flags

```yaml
features:
  # Agent features
  auto_faq_responses: false     # When true, send FAQs without approval
  auto_acknowledgments: true    # Send "received your message" automatically
  auto_ticket_creation: true    # Create ops tickets automatically

  # Monitoring
  proactive_monitoring: true    # Actively check systems vs wait for events
  anomaly_detection: true       # ML-based anomaly detection

  # Content
  draft_social_posts: true      # Generate drafts for social
  auto_schedule_content: false  # Would require approval to enable

  # Finance
  revenue_projections: true     # Generate financial projections
  churn_prediction: true        # Predict likely churns
```

## Safety Limits

```yaml
safety:
  # Maximum actions per period
  max_emails_per_hour: 10
  max_api_calls_per_minute: 60
  max_decisions_per_day: 50

  # Financial limits
  max_auto_refund: 0           # No auto-refunds ever
  max_spend_per_action: 0      # No autonomous spending

  # Content limits
  max_draft_length_chars: 5000
  max_attachments_per_email: 3

  # Rate limiting
  duplicate_action_cooldown_minutes: 5
  same_customer_contact_cooldown_hours: 4
```

## Logging Settings

```yaml
logging:
  # Log levels
  execution_log_level: "INFO"
  decision_log_level: "DEBUG"
  audit_log_level: "DEBUG"

  # Retention
  execution_log_retention_days: 30
  decision_log_retention_days: 90
  audit_log_retention_days: 365

  # What to log
  log_all_events: true
  log_all_decisions: true
  log_all_api_calls: true
  log_execution_time: true
```

## Environment-Specific

### Production

```yaml
environment: "production"
debug_mode: false
dry_run: false  # Actually execute actions
```

### Development/Testing

```yaml
# environment: "development"
# debug_mode: true
# dry_run: true  # Log but don't execute
```
