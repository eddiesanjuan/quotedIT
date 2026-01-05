"""
Complexity Detection System for Task Routing
DISC-103: Smart Complexity Detection

Routes tasks based on confidence scoring:
- 85%+ confidence -> Execute directly
- 60-85% confidence -> Execute with checkpoints
- <60% confidence -> Plan first

Usage:
    from complexity_detection import score_task_complexity

    result = score_task_complexity("Fix typo in README", ["README.md"])
    # Returns: {"confidence": 92, "complexity": "low", "recommended_approach": "direct", ...}

    result = score_task_complexity("Refactor auth system across multiple files")
    # Returns: {"confidence": 45, "complexity": "high", "recommended_approach": "plan_first", ...}
"""

import re
from pathlib import Path
from typing import Optional

import yaml


def _load_signals_config() -> dict:
    """Load complexity signals from YAML config."""
    config_path = Path(__file__).parent / "complexity_signals.yaml"
    if config_path.exists():
        with open(config_path) as f:
            return yaml.safe_load(f)
    # Fallback defaults if config doesn't exist
    return {
        "baseline_confidence": 70,
        "thresholds": {"direct_execution": 85, "checkpoint": 60, "plan_first": 0},
        "high_complexity_signals": [],
        "medium_complexity_signals": [],
        "low_complexity_signals": [],
        "protected_paths": [],
        "scope_multipliers": {"file_count": {}, "change_type": {}},
    }


def _match_patterns(text: str, patterns: list[dict]) -> list[dict]:
    """Find all matching patterns in text."""
    matches = []
    text_lower = text.lower()
    for pattern_config in patterns:
        pattern = pattern_config.get("pattern", "")
        if re.search(pattern, text_lower, re.IGNORECASE):
            matches.append(pattern_config)
    return matches


def _check_protected_paths(file_hints: list[str], protected_paths: list[dict]) -> list[dict]:
    """Check if any files are in protected paths."""
    violations = []
    for file_path in file_hints:
        file_lower = file_path.lower()
        for protected in protected_paths:
            pattern = protected.get("pattern", "")
            if re.search(pattern, file_lower, re.IGNORECASE):
                violations.append(protected)
    return violations


def _get_file_count_multiplier(file_count: int, multipliers: dict) -> float:
    """Get confidence multiplier based on file count."""
    file_config = multipliers.get("file_count", {})

    if file_count == 1:
        return file_config.get("1", 1.2)
    elif file_count <= 3:
        return file_config.get("2-3", 1.0)
    elif file_count <= 5:
        return file_config.get("4-5", 0.85)
    else:
        return file_config.get("6+", 0.7)


def score_task_complexity(
    task_description: str,
    file_hints: Optional[list[str]] = None,
) -> dict:
    """
    Score task complexity and recommend an execution approach.

    Args:
        task_description: Natural language description of the task
        file_hints: Optional list of files that will be affected

    Returns:
        dict with:
            - confidence: 0-100 score
            - complexity: "low" | "medium" | "high"
            - recommended_approach: "direct" | "checkpoints" | "plan_first"
            - reasoning: Explanation of the score
            - signals_matched: List of signals that were detected
    """
    if file_hints is None:
        file_hints = []

    config = _load_signals_config()

    # Start with baseline confidence
    confidence = config.get("baseline_confidence", 70)
    reasoning_parts = [f"Starting confidence: {confidence}%"]
    signals_matched = []

    # Check for high complexity signals (reduce confidence)
    high_matches = _match_patterns(
        task_description, config.get("high_complexity_signals", [])
    )
    for match in high_matches:
        weight = match.get("weight", 20)
        confidence -= weight
        signals_matched.append(
            {"type": "high", "pattern": match.get("pattern"), "weight": -weight}
        )
        reasoning_parts.append(
            f"High complexity signal: {match.get('reason')} (-{weight}%)"
        )

    # Check for medium complexity signals (slight reduction)
    medium_matches = _match_patterns(
        task_description, config.get("medium_complexity_signals", [])
    )
    for match in medium_matches:
        weight = match.get("weight", 10)
        confidence -= weight
        signals_matched.append(
            {"type": "medium", "pattern": match.get("pattern"), "weight": -weight}
        )
        reasoning_parts.append(
            f"Medium complexity signal: {match.get('reason')} (-{weight}%)"
        )

    # Check for low complexity signals (increase confidence)
    low_matches = _match_patterns(
        task_description, config.get("low_complexity_signals", [])
    )
    for match in low_matches:
        weight = match.get("weight", 15)
        confidence += weight
        signals_matched.append(
            {"type": "low", "pattern": match.get("pattern"), "weight": weight}
        )
        reasoning_parts.append(
            f"Low complexity signal: {match.get('reason')} (+{weight}%)"
        )

    # Check protected paths (force plan-first)
    protected_violations = _check_protected_paths(
        file_hints, config.get("protected_paths", [])
    )
    if protected_violations:
        # Protected paths cap confidence at 50%
        if confidence > 50:
            old_confidence = confidence
            confidence = 50
            reasoning_parts.append(
                f"Protected path detected: capped confidence from {old_confidence}% to 50%"
            )
        for violation in protected_violations:
            signals_matched.append(
                {
                    "type": "protected",
                    "pattern": violation.get("pattern"),
                    "reason": violation.get("reason"),
                }
            )

    # Apply file count multiplier
    if file_hints:
        file_count = len(file_hints)
        multiplier = _get_file_count_multiplier(
            file_count, config.get("scope_multipliers", {})
        )
        if multiplier != 1.0:
            old_confidence = confidence
            confidence = int(confidence * multiplier)
            reasoning_parts.append(
                f"File count ({file_count}): {old_confidence}% * {multiplier} = {confidence}%"
            )

    # Clamp confidence to 0-100
    confidence = max(0, min(100, confidence))

    # Determine complexity level
    if confidence >= 85:
        complexity = "low"
    elif confidence >= 60:
        complexity = "medium"
    else:
        complexity = "high"

    # Determine recommended approach based on thresholds
    thresholds = config.get("thresholds", {})
    if confidence >= thresholds.get("direct_execution", 85):
        recommended_approach = "direct"
        approach_explanation = "Execute directly - high confidence, low risk"
    elif confidence >= thresholds.get("checkpoint", 60):
        recommended_approach = "checkpoints"
        approach_explanation = "Execute with checkpoints - moderate complexity, verify at milestones"
    else:
        recommended_approach = "plan_first"
        approach_explanation = "Plan first - complex task, design before implementing"

    reasoning_parts.append(f"Final: {confidence}% -> {recommended_approach}")

    return {
        "confidence": confidence,
        "complexity": complexity,
        "recommended_approach": recommended_approach,
        "reasoning": "; ".join(reasoning_parts),
        "approach_explanation": approach_explanation,
        "signals_matched": signals_matched,
        "file_count": len(file_hints) if file_hints else 0,
    }


def get_routing_recommendation(
    task_description: str,
    file_hints: Optional[list[str]] = None,
) -> str:
    """
    Get a simple routing recommendation for a task.

    Returns one of: "direct", "checkpoints", "plan_first"
    """
    result = score_task_complexity(task_description, file_hints)
    return result["recommended_approach"]


def explain_complexity(
    task_description: str,
    file_hints: Optional[list[str]] = None,
) -> str:
    """
    Get a human-readable explanation of task complexity.

    Returns a formatted string explaining the analysis.
    """
    result = score_task_complexity(task_description, file_hints)

    lines = [
        f"Task Complexity Analysis",
        f"========================",
        f"",
        f"Confidence: {result['confidence']}%",
        f"Complexity: {result['complexity'].upper()}",
        f"Approach: {result['recommended_approach'].replace('_', ' ').title()}",
        f"",
        f"Reasoning:",
    ]

    for signal in result["signals_matched"]:
        signal_type = signal.get("type", "unknown")
        pattern = signal.get("pattern", "unknown")
        if signal_type == "protected":
            lines.append(f"  - PROTECTED PATH: {signal.get('reason')}")
        else:
            weight = signal.get("weight", 0)
            sign = "+" if weight > 0 else ""
            lines.append(f"  - [{signal_type.upper()}] {pattern} ({sign}{weight}%)")

    lines.append("")
    lines.append(f"Recommendation: {result['approach_explanation']}")

    return "\n".join(lines)


# Example usage and self-test
if __name__ == "__main__":
    # Test cases
    test_cases = [
        ("Fix typo in README", ["README.md"]),
        ("Update button color to blue", ["frontend/styles.css"]),
        ("Refactor authentication system", ["backend/api/auth.py", "backend/models/user.py"]),
        ("Add new billing endpoint for refunds", ["backend/api/billing.py"]),
        ("Update error message text", ["frontend/index.html"]),
        (
            "Migrate database schema and update all models",
            ["backend/models/database.py", "backend/models/user.py", "backend/models/quote.py"],
        ),
        ("Add comment explaining function", ["backend/utils.py"]),
    ]

    print("Complexity Detection Test Results")
    print("=" * 50)
    print()

    for task, files in test_cases:
        result = score_task_complexity(task, files)
        print(f"Task: {task}")
        print(f"Files: {files}")
        print(f"Confidence: {result['confidence']}%")
        print(f"Complexity: {result['complexity']}")
        print(f"Approach: {result['recommended_approach']}")
        print("-" * 50)
        print()
