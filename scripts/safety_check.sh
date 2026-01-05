#!/bin/bash
# Safety Net Check Script for Quoted Autonomous Operations
# DISC-106: Defense-in-depth safety checks
#
# Usage:
#   ./scripts/safety_check.sh <agent-name> <action-type>
#
# Exit codes:
#   0 = All checks passed, safe to proceed
#   1 = Safety check failed, do not proceed
#
# Example:
#   ./scripts/safety_check.sh code implement
#   ./scripts/safety_check.sh discovery analyze

set -e

# Configuration
REPO_ROOT="/Users/eddiesanjuan/Personal_Assistant/Eddie_Personal_Assistant/quoted"
AI_COMPANY_DIR="${REPO_ROOT}/.ai-company"

# Defaults (can be overridden by environment)
DEFAULT_MAX_ITERATIONS=5
DEFAULT_COOLDOWN_SECONDS=60
DEFAULT_MAX_COST_PER_HOUR=5.00

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

log_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Parse arguments
AGENT="${1:-unknown}"
ACTION="${2:-unknown}"

if [ "$AGENT" = "unknown" ]; then
    echo "Usage: $0 <agent-name> <action-type>"
    echo "Example: $0 code implement"
    exit 1
fi

echo "=== Safety Net Check ==="
echo "Agent: $AGENT"
echo "Action: $ACTION"
echo "Time: $(date -Iseconds)"
echo ""

# Track if any check fails
BLOCKED=false
BLOCK_REASON=""

# ============================================
# LAYER 4: HUMAN OVERRIDE CHECKS
# ============================================
echo "--- Layer 4: Human Override ---"

# Check 1: Emergency stop file
if [ -f "${AI_COMPANY_DIR}/EMERGENCY_STOP" ]; then
    log_fail "Emergency stop is ACTIVE"
    echo "  Contents: $(cat ${AI_COMPANY_DIR}/EMERGENCY_STOP)"
    echo "  Remove file to resume: rm ${AI_COMPANY_DIR}/EMERGENCY_STOP"
    BLOCKED=true
    BLOCK_REASON="Emergency stop active"
else
    log_pass "No emergency stop"
fi

# Check 2: AI_COMPANY_ENABLED flag
if [ "${AI_COMPANY_ENABLED:-true}" = "false" ]; then
    log_fail "AI Company is DISABLED (AI_COMPANY_ENABLED=false)"
    BLOCKED=true
    BLOCK_REASON="AI Company disabled"
else
    log_pass "AI Company enabled"
fi

# ============================================
# LAYER 1: COOLDOWNS & RATE LIMITS
# ============================================
echo ""
echo "--- Layer 1: Cooldowns & Rate Limits ---"

# Get agent-specific limits
AGENT_DIR="${AI_COMPANY_DIR}/agents/${AGENT}"
mkdir -p "${AGENT_DIR}"

# Check 3: Iteration limit
ITERATION_FILE="${AGENT_DIR}/iteration.md"
CURRENT_ITERATION=$(cat "$ITERATION_FILE" 2>/dev/null || echo "0")

# Agent-specific max iterations from Constitution
case "$AGENT" in
    discovery) MAX_ITERATIONS=3 ;;
    support)   MAX_ITERATIONS=5 ;;
    ops)       MAX_ITERATIONS=10 ;;
    code)      MAX_ITERATIONS=3 ;;
    growth)    MAX_ITERATIONS=5 ;;
    meta)      MAX_ITERATIONS=2 ;;
    finance)   MAX_ITERATIONS=3 ;;
    loop)      MAX_ITERATIONS=5 ;;
    *)         MAX_ITERATIONS=${DEFAULT_MAX_ITERATIONS} ;;
esac

if [ "$CURRENT_ITERATION" -ge "$MAX_ITERATIONS" ]; then
    log_fail "Iteration limit reached: ${CURRENT_ITERATION} >= ${MAX_ITERATIONS}"
    BLOCKED=true
    BLOCK_REASON="Iteration limit exceeded"
else
    log_pass "Iteration count OK: ${CURRENT_ITERATION} / ${MAX_ITERATIONS}"
fi

# Check 4: Cooldown period
LAST_RUN_FILE="${AGENT_DIR}/last_run"
COOLDOWN_SECONDS="${COOLDOWN_SECONDS:-$DEFAULT_COOLDOWN_SECONDS}"

if [ -f "$LAST_RUN_FILE" ]; then
    LAST_RUN=$(cat "$LAST_RUN_FILE")
    NOW=$(date +%s)
    ELAPSED=$((NOW - LAST_RUN))

    if [ "$ELAPSED" -lt "$COOLDOWN_SECONDS" ]; then
        REMAINING=$((COOLDOWN_SECONDS - ELAPSED))
        log_fail "Cooldown not elapsed: ${ELAPSED}s < ${COOLDOWN_SECONDS}s (wait ${REMAINING}s)"
        BLOCKED=true
        BLOCK_REASON="Cooldown not elapsed"
    else
        log_pass "Cooldown elapsed: ${ELAPSED}s >= ${COOLDOWN_SECONDS}s"
    fi
else
    log_pass "No previous run recorded (first run)"
fi

# Check 5: Budget (simplified - would need actual cost tracking)
COST_FILE="${AGENT_DIR}/cost_today.md"
COST_TODAY=$(cat "$COST_FILE" 2>/dev/null || echo "0")
MAX_DAILY_COST="${MAX_DAILY_COST:-50.00}"

# Convert to cents for integer comparison
COST_CENTS=$(echo "$COST_TODAY * 100" | bc 2>/dev/null || echo "0")
MAX_CENTS=$(echo "$MAX_DAILY_COST * 100" | bc 2>/dev/null || echo "5000")

if [ "${COST_CENTS%.*}" -ge "${MAX_CENTS%.*}" ]; then
    log_fail "Daily budget exceeded: \$${COST_TODAY} >= \$${MAX_DAILY_COST}"
    BLOCKED=true
    BLOCK_REASON="Budget exceeded"
else
    log_pass "Budget OK: \$${COST_TODAY} / \$${MAX_DAILY_COST}"
fi

# ============================================
# FINAL RESULT
# ============================================
echo ""
echo "=== Result ==="

if [ "$BLOCKED" = true ]; then
    log_fail "BLOCKED: $BLOCK_REASON"
    echo ""
    echo "Action '$ACTION' by agent '$AGENT' is NOT SAFE to proceed."
    echo "Resolve the issue above before continuing."
    exit 1
else
    log_pass "All safety checks passed"
    echo ""
    echo "Action '$ACTION' by agent '$AGENT' is SAFE to proceed."

    # Update tracking files for next check
    date +%s > "$LAST_RUN_FILE"

    # Increment iteration count
    NEW_ITERATION=$((CURRENT_ITERATION + 1))
    echo "$NEW_ITERATION" > "$ITERATION_FILE"
    echo "Iteration count updated: ${CURRENT_ITERATION} -> ${NEW_ITERATION}"

    exit 0
fi
