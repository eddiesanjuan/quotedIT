# External Integrations Configuration

## Stripe Integration

### Webhook Configuration

```yaml
stripe:
  webhook_endpoint: "https://quoted.it.com/api/events/webhook/stripe"
  webhook_secret: "${STRIPE_WEBHOOK_SECRET}"

  # Events to subscribe
  events:
    # Subscriptions
    - customer.subscription.created
    - customer.subscription.updated
    - customer.subscription.deleted
    - customer.subscription.trial_will_end

    # Invoices
    - invoice.created
    - invoice.paid
    - invoice.payment_failed
    - invoice.upcoming

    # Charges
    - charge.succeeded
    - charge.failed
    - charge.refunded
    - charge.dispute.created
    - charge.dispute.closed

    # Customers
    - customer.created
    - customer.updated
    - customer.deleted
```

### Event Mapping

| Stripe Event | AI Company Action | Priority |
|--------------|-------------------|----------|
| `subscription.created` | Log revenue, celebrate | MEDIUM |
| `subscription.deleted` | Log churn, trigger outreach | HIGH |
| `invoice.payment_failed` | Alert, trigger recovery | HIGH |
| `charge.refunded` | Log, update metrics | MEDIUM |
| `charge.dispute.created` | Alert Eddie, gather evidence | CRITICAL |

### API Calls

```yaml
stripe_api:
  # Allowed operations (read-only by default)
  allowed:
    - list_customers
    - get_customer
    - list_subscriptions
    - get_subscription
    - list_invoices
    - get_invoice
    - list_charges

  # Requires approval
  requires_approval:
    - create_refund
    - cancel_subscription
    - update_subscription

  # Never
  forbidden:
    - delete_customer
    - modify_payment_method
```

---

## Resend Integration

### Configuration

```yaml
resend:
  api_key: "${RESEND_API_KEY}"
  from_email: "team@quoted.it.com"
  from_name: "Quoted"
  reply_to: "support@quoted.it.com"

  # Webhook for email events
  webhook_endpoint: "https://quoted.it.com/api/events/webhook/resend"
```

### Email Types

| Type | Template | Approval |
|------|----------|----------|
| Acknowledgment | Standard | Auto |
| FAQ Response | Standard | Review |
| Custom Response | Custom | Required |
| Marketing | Template | Required |
| Transactional | Standard | Auto |

### Event Mapping

| Resend Event | AI Company Action | Priority |
|--------------|-------------------|----------|
| `email.delivered` | Log success | LOW |
| `email.bounced` | Flag address, alert | MEDIUM |
| `email.complained` | Stop sending, alert | HIGH |
| `email.opened` | Log engagement | LOW |
| `email.clicked` | Log engagement | LOW |

### Safety Limits

```yaml
resend_limits:
  max_per_hour: 10
  max_per_day: 50
  same_recipient_cooldown_hours: 4
  blocked_domains: []  # Add if spam issues
```

---

## Railway Integration

### Configuration

```yaml
railway:
  project_id: "${RAILWAY_PROJECT_ID}"
  service_name: "web"
  environment: "production"
```

### Log Monitoring

```yaml
railway_logs:
  # Polling (if no webhook)
  poll_interval_minutes: 15
  lookback_minutes: 30

  # Patterns to watch
  error_patterns:
    - "ERROR"
    - "CRITICAL"
    - "Exception"
    - "Traceback"
    - "status=500"

  warning_patterns:
    - "WARNING"
    - "slow query"
    - "timeout"
    - "rate limit"

  # Ignore patterns
  ignore_patterns:
    - "health check"
    - "OPTIONS request"
```

### Deployment Tracking

```yaml
railway_deployments:
  track_deployments: true
  notify_on_deploy: true
  post_deploy_health_check: true
  health_check_wait_seconds: 60
```

---

## PostHog Integration

### Configuration

```yaml
posthog:
  api_key: "${POSTHOG_API_KEY}"
  project_id: "phc_xxxxxxxxxxxx"
  host: "https://app.posthog.com"
```

### Metrics to Track

```yaml
posthog_metrics:
  # User events
  events:
    - signup_completed
    - quote_generated
    - quote_sent
    - quote_edited
    - subscription_started
    - subscription_cancelled

  # Properties to extract
  properties:
    - trade
    - plan_type
    - quote_value
    - source
```

### Feature Flags

```yaml
posthog_flags:
  check_on_startup: true
  refresh_interval_minutes: 5

  flags_to_monitor:
    - invoicing_enabled
    - new_pdf_templates
    - voice_template_customization
```

---

## Twilio Integration (SMS)

### Configuration

```yaml
twilio:
  account_sid: "${TWILIO_ACCOUNT_SID}"
  auth_token: "${TWILIO_AUTH_TOKEN}"
  from_number: "${TWILIO_FROM_NUMBER}"
  to_number: "${EDDIE_PHONE_NUMBER}"
```

### Usage Rules

```yaml
twilio_rules:
  # Only for critical alerts
  triggers:
    - incident.critical
    - finance.dispute
    - support.legal_mention
    - ops.system_down

  # Rate limits
  max_per_hour: 5
  max_per_day: 20
  cooldown_minutes: 5

  # Quiet hours (except critical)
  quiet_hours:
    start: "22:00"
    end: "07:00"
    override_for_critical: true
```

### Message Templates

```yaml
twilio_templates:
  critical_alert: |
    [QUOTED ALERT] CRITICAL
    {description}
    Action: {action_needed}
    Reply YES to ack

  incident: |
    [QUOTED] System Issue
    {description}
    Status: {status}

  dispute: |
    [QUOTED] Payment Dispute
    Customer: {customer}
    Amount: ${amount}
    Needs response by: {deadline}
```

---

## GitHub Integration

### Configuration

```yaml
github:
  owner: "eddiesanjuan"
  repo: "quotedIT"
  token: "${GITHUB_TOKEN}"
```

### Workflow Dispatch

```yaml
github_workflows:
  # Workflows to trigger
  ai_company_loop: "ai-company-loop.yml"
  ai_company_urgent: "ai-company-urgent.yml"

  # Dispatch rules
  dispatch_on:
    - critical_event_received
    - manual_trigger
```

### Issue/PR Creation

```yaml
github_issues:
  # Auto-create issues for
  auto_create:
    - bug_reports
    - feature_requests
    - incident_postmortems

  # Labels
  labels:
    bug: "bug"
    feature: "enhancement"
    incident: "incident"
    ai_generated: "ai-company"
```

---

## Claude API Integration

### Configuration

```yaml
claude:
  api_key: "${ANTHROPIC_API_KEY}"
  model: "claude-sonnet-4-20250514"
  max_tokens: 4096
```

### Usage

```yaml
claude_usage:
  # What Claude is used for
  tasks:
    - email_classification
    - sentiment_analysis
    - response_drafting
    - summary_generation
    - decision_recommendations

  # Rate limits
  max_calls_per_minute: 60
  max_calls_per_day: 1000

  # Cost tracking
  track_token_usage: true
  alert_threshold_dollars: 10  # per day
```

---

## Integration Health Checks

### Monitoring

```yaml
health_checks:
  interval_minutes: 30

  services:
    stripe:
      check: "list_customers(limit=1)"
      timeout_seconds: 10

    resend:
      check: "api_status"
      timeout_seconds: 5

    railway:
      check: "health_endpoint"
      timeout_seconds: 10

    posthog:
      check: "api_status"
      timeout_seconds: 5

    claude:
      check: "simple_completion"
      timeout_seconds: 15
```

### Alerting

```yaml
integration_alerts:
  # When service is down
  on_failure:
    - log_error
    - retry_count: 3
    - alert_if_persistent: true

  # When to escalate
  escalate_after_failures: 3
  escalate_method: "email"  # sms for critical services
```
