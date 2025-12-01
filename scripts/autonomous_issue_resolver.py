#!/usr/bin/env python3
"""
Autonomous Issue Resolver for Quoted
=====================================

This script polls the Quoted API for new user-reported issues,
then uses Claude Code to analyze and attempt to fix them.

Usage:
    # Run once (process all new issues)
    python scripts/autonomous_issue_resolver.py

    # Run in daemon mode (poll every 5 minutes)
    python scripts/autonomous_issue_resolver.py --daemon

    # Run with custom interval
    python scripts/autonomous_issue_resolver.py --daemon --interval 300

Environment Variables:
    QUOTED_API_URL: Base URL of the Quoted API (default: http://localhost:8000)
    QUOTED_PROJECT_PATH: Path to the Quoted project (for Claude Code)

How It Works:
    1. Polls /api/issues/new for issues with status='new'
    2. Claims issue via /api/issues/{id}/claim (prevents duplicate work)
    3. Builds a prompt for Claude Code with issue context
    4. Runs Claude Code CLI in non-interactive mode
    5. Updates issue status with analysis and solution
"""

import os
import sys
import json
import time
import argparse
import subprocess
from datetime import datetime
from typing import Optional, List, Dict, Any
import requests


# Configuration
API_URL = os.environ.get("QUOTED_API_URL", "http://localhost:8000")
PROJECT_PATH = os.environ.get(
    "QUOTED_PROJECT_PATH",
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)


def log(message: str, level: str = "INFO"):
    """Simple logging with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")


def get_new_issues() -> List[Dict[str, Any]]:
    """Fetch all issues with status='new'."""
    try:
        response = requests.get(f"{API_URL}/api/issues/new", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        log(f"Error fetching issues: {e}", "ERROR")
        return []


def claim_issue(issue_id: str) -> Optional[Dict[str, Any]]:
    """
    Claim an issue for processing.
    Returns the issue if claimed successfully, None if already claimed.
    """
    try:
        response = requests.post(
            f"{API_URL}/api/issues/{issue_id}/claim",
            timeout=10
        )
        if response.status_code == 409:
            log(f"Issue {issue_id} already claimed by another agent", "WARN")
            return None
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        log(f"Error claiming issue {issue_id}: {e}", "ERROR")
        return None


def update_issue(issue_id: str, update: Dict[str, Any]) -> bool:
    """Update an issue with resolution details."""
    try:
        response = requests.patch(
            f"{API_URL}/api/issues/{issue_id}",
            json=update,
            timeout=10
        )
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        log(f"Error updating issue {issue_id}: {e}", "ERROR")
        return False


def build_claude_prompt(issue: Dict[str, Any]) -> str:
    """
    Build a prompt for Claude Code to analyze and fix the issue.
    """
    prompt = f"""You are analyzing a user-reported issue for the Quoted application.

## Issue Details

**Title:** {issue.get('title', 'No title')}

**Description:**
{issue.get('description', 'No description')}

**Category:** {issue.get('category', 'bug')}
**Severity:** {issue.get('severity', 'medium')}

**Page URL:** {issue.get('page_url', 'Not specified')}

**Error Message:**
{issue.get('error_message', 'None provided')}

**Steps to Reproduce:**
{issue.get('steps_to_reproduce', 'Not provided')}

## Your Task

1. **Analyze** the issue and identify the root cause
2. **Search** the codebase for relevant files
3. **Propose** a fix with specific code changes
4. **Implement** the fix if you're confident it's correct
5. **Test** that the fix works (if possible)

## Important Guidelines

- Only make changes you're confident about
- If the issue is unclear, mark it as 'needs_human'
- Document your analysis thoroughly
- Don't make changes outside the scope of this specific issue
- If you can't reproduce or understand the issue, explain why

## Response Format

After your analysis and any fixes, provide a summary in this exact format:

```json
{{
    "analysis": "Your detailed analysis of the issue",
    "solution": "What you did to fix it (or why you couldn't)",
    "files_modified": ["list", "of", "files.py"],
    "status": "resolved|needs_human|wont_fix",
    "confidence": "high|medium|low"
}}
```
"""
    return prompt


def run_claude_code(prompt: str, issue_id: str) -> Dict[str, Any]:
    """
    Run Claude Code CLI with the given prompt.
    Returns parsed results from Claude's response.
    """
    log(f"Running Claude Code for issue {issue_id}...")

    # Build the Claude Code command
    # Using --print to get output, --dangerously-skip-permissions for automation
    cmd = [
        "claude",
        "--print",
        "--dangerously-skip-permissions",
        "-p", prompt
    ]

    try:
        # Run in the project directory
        result = subprocess.run(
            cmd,
            cwd=PROJECT_PATH,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        output = result.stdout

        # Try to extract JSON from the response
        if "```json" in output:
            json_start = output.find("```json") + 7
            json_end = output.find("```", json_start)
            if json_end > json_start:
                json_str = output[json_start:json_end].strip()
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    pass

        # Fallback: return raw output
        return {
            "analysis": output[:2000],
            "solution": "See analysis for details",
            "files_modified": [],
            "status": "needs_human",
            "confidence": "low"
        }

    except subprocess.TimeoutExpired:
        log(f"Claude Code timed out for issue {issue_id}", "ERROR")
        return {
            "analysis": "Processing timed out after 5 minutes",
            "solution": None,
            "files_modified": [],
            "status": "needs_human",
            "confidence": "low"
        }
    except Exception as e:
        log(f"Error running Claude Code: {e}", "ERROR")
        return {
            "analysis": f"Error: {str(e)}",
            "solution": None,
            "files_modified": [],
            "status": "needs_human",
            "confidence": "low"
        }


def process_issue(issue: Dict[str, Any]) -> bool:
    """
    Process a single issue: analyze, fix, update.
    Returns True if processed successfully.
    """
    issue_id = issue["id"]
    log(f"Processing issue: {issue.get('title', issue_id)}")

    # Update status to in_progress
    update_issue(issue_id, {"status": "in_progress"})

    # Build prompt and run Claude Code
    prompt = build_claude_prompt(issue)
    result = run_claude_code(prompt, issue_id)

    # Map confidence/status to final status
    final_status = result.get("status", "needs_human")
    if final_status == "resolved" and result.get("confidence") == "low":
        final_status = "needs_human"

    # Update the issue with results
    update = {
        "status": final_status,
        "agent_analysis": result.get("analysis", ""),
        "agent_solution": result.get("solution", ""),
        "files_modified": result.get("files_modified", []),
    }

    success = update_issue(issue_id, update)

    if success:
        log(f"Issue {issue_id} processed: {final_status}")
    else:
        log(f"Failed to update issue {issue_id}", "ERROR")

    return success


def run_once():
    """Process all new issues once."""
    log("Checking for new issues...")

    issues = get_new_issues()
    if not issues:
        log("No new issues found")
        return

    log(f"Found {len(issues)} new issue(s)")

    for issue in issues:
        # Try to claim the issue
        claimed = claim_issue(issue["id"])
        if not claimed:
            continue

        # Process the claimed issue
        process_issue(claimed)

        # Small delay between issues
        time.sleep(2)


def run_daemon(interval: int = 300):
    """
    Run in daemon mode, polling for new issues at regular intervals.

    Args:
        interval: Seconds between polls (default: 300 = 5 minutes)
    """
    log(f"Starting daemon mode (polling every {interval} seconds)")
    log("Press Ctrl+C to stop")

    while True:
        try:
            run_once()
            log(f"Sleeping for {interval} seconds...")
            time.sleep(interval)
        except KeyboardInterrupt:
            log("Shutting down...")
            break
        except Exception as e:
            log(f"Unexpected error: {e}", "ERROR")
            time.sleep(60)  # Wait a bit before retrying


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Autonomous Issue Resolver for Quoted",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "--daemon", "-d",
        action="store_true",
        help="Run in daemon mode (continuous polling)"
    )

    parser.add_argument(
        "--interval", "-i",
        type=int,
        default=300,
        help="Polling interval in seconds (default: 300)"
    )

    parser.add_argument(
        "--api-url",
        default=API_URL,
        help=f"API base URL (default: {API_URL})"
    )

    args = parser.parse_args()

    # Update global API URL if provided
    global API_URL
    API_URL = args.api_url

    log(f"Quoted Autonomous Issue Resolver")
    log(f"API URL: {API_URL}")
    log(f"Project Path: {PROJECT_PATH}")

    if args.daemon:
        run_daemon(args.interval)
    else:
        run_once()


if __name__ == "__main__":
    main()
