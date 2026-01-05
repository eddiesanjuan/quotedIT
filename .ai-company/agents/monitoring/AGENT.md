# Monitoring Agent Specification

**Version**: 1.0
**Status**: Active
**Ticket**: DISC-140

## Purpose

The Monitoring Agent is an autonomous system that continuously watches Quoted's health and surfaces issues proactively. The founder should wake up to a briefing, not a crisis.

## Core Responsibilities

### 1. System Health Monitoring (Critical - Every 15 Minutes)

| Check | Threshold | Alert Level |
|-------|-----------|-------------|
| API Response Time | >2s average | WARNING |
| API Response Time | >5s average | CRITICAL |
| Error Rate | >1% of requests | WARNING |
| Error Rate | >5% of requests | CRITICAL |
| Database Connectivity | Failure | CRITICAL |
| Demo Generation | Failure | WARNING |
| PDF Generation | Failure | WARNING |

### 2. Business Metrics Monitoring (Hourly)

| Metric | Condition | Alert Level |
|--------|-----------|-------------|
| Traffic Spike | 3x normal | INFO (opportunity) |
| Traffic Drop | <30% of average | WARNING |
| Traffic Drop | <10% of average | CRITICAL |
| Signup Velocity | 0 signups for 24h (with ads running) | WARNING |
| Demo-to-Signup Conversion | <50% of baseline | WARNING |
| Payment Failures | Any | WARNING |
| Churn Signal | Account deletion | INFO |

### 3. Daily Summary Email (8:15 AM UTC)

Generates a founder briefing email including:
- System health status (GREEN/YELLOW/RED)
- Key metrics vs. 7-day average
- Anomalies detected in last 24 hours
- Recommended actions with priority
- Scheduled tasks for the day

## Architecture

```
monitoring_agent.py
├── run_critical_health_checks()     # Every 15 minutes
├── run_business_metrics_check()     # Every hour
├── generate_daily_summary()         # Daily at 8:15 AM UTC
└── alert_founder()                  # Immediate alerts for CRITICAL issues
```

## Alert Routing

| Severity | Action |
|----------|--------|
| CRITICAL | Immediate email + log |
| WARNING | Include in next hourly check, email if >2 warnings |
| INFO | Include in daily summary only |

## State Persistence

The agent maintains state in `.ai-company/agents/monitoring/state.md`:
- Last known healthy baselines
- Recent alert history (dedup window: 1 hour)
- Metrics trend data (7-day rolling)

## Dependencies

- `backend/services/health.py` - External service health checks
- `backend/services/alerts.py` - Alert infrastructure
- `backend/services/email.py` - Email delivery
- `backend/services/marketing_analytics.py` - Business metrics
- `backend/services/traffic_spike_alerts.py` - Traffic anomaly detection

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `MONITORING_AGENT_ENABLED` | `true` | Enable/disable the monitoring agent |
| `MONITORING_CRITICAL_INTERVAL` | `15` | Minutes between critical checks |
| `MONITORING_BUSINESS_INTERVAL` | `60` | Minutes between business checks |
| `MONITORING_DAILY_SUMMARY_HOUR` | `8` | UTC hour for daily summary |

## Alert Throttling

To prevent alert fatigue:
- Same alert type: Max 1 per hour
- Same CRITICAL alert: Max 1 per 15 minutes
- Daily summary includes deduplicated alert count

## Integration Points

### Existing Infrastructure (Leveraged)
- DISC-139: Traffic spike/drop detection
- DISC-141: Marketing analytics
- DISC-148: Daily health check
- INFRA-007: Service health checks
- INFRA-010: Alert service

### New Capabilities
- Unified monitoring dashboard (via daily email)
- Trend analysis (7-day baselines)
- Proactive recommendations
- Alert deduplication

## Success Metrics

1. **Time to Detection**: <15 minutes for critical issues
2. **Alert Accuracy**: <10% false positive rate
3. **Founder Experience**: "Wake up to briefing, not crisis"

## Future Enhancements (Not in Scope)

- Slack integration
- Mobile push notifications
- Competitive intelligence monitoring
- Auto-remediation for known issues
