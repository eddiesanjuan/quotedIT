"""
AI Company Dispatcher Service.

Dispatches events to GitHub Actions workflows for processing by AI agents.

This service bridges the webhook gateway with the GitHub Actions-based
agent processing system.
"""

import os
import logging
import asyncio
from typing import Optional
import httpx

logger = logging.getLogger(__name__)


# Workflow mappings for each agent
WORKFLOW_MAP = {
    "support": "ai-civilization-support.yml",
    "ops": "ai-civilization-ops.yml",
    "code": "ai-civilization-code.yml",
    "growth": "ai-civilization-growth.yml",
    "urgent": "ai-civilization-urgent.yml",
    "meta": "ai-civilization-meta.yml",
    "loop": "ai-civilization-loop.yml",
    "morning": "ai-civilization-morning.yml",
}

# GitHub repository info
GITHUB_OWNER = "eddiesanjuan"
GITHUB_REPO = "quotedIT"


async def dispatch_to_agent_async(agent: str, payload: dict) -> bool:
    """
    Trigger a GitHub Action workflow for an agent.

    Args:
        agent: The agent to trigger (support, ops, code, growth, urgent, meta)
        payload: The event payload to pass to the workflow

    Returns:
        True if dispatch was successful, False otherwise
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        logger.warning("GITHUB_TOKEN not set - cannot dispatch to agent")
        return False

    workflow = WORKFLOW_MAP.get(agent)
    if not workflow:
        logger.error(f"Unknown agent: {agent}")
        return False

    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/dispatches"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github.v3+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
                json={
                    "event_type": f"{agent}_dispatch",
                    "client_payload": payload
                },
                timeout=30.0
            )

            if response.status_code == 204:
                logger.info(f"Successfully dispatched to {agent} agent")
                return True
            else:
                logger.error(
                    f"Failed to dispatch to {agent}: {response.status_code} - {response.text}"
                )
                return False

    except httpx.TimeoutException:
        logger.error(f"Timeout dispatching to {agent} agent")
        return False
    except Exception as e:
        logger.error(f"Error dispatching to {agent}: {e}")
        return False


def dispatch_to_agent_sync(agent: str, payload: dict) -> bool:
    """
    Synchronous version of dispatch_to_agent.

    For use in background tasks or non-async contexts.
    """
    return asyncio.run(dispatch_to_agent_async(agent, payload))


async def trigger_workflow(workflow_name: str, inputs: Optional[dict] = None) -> bool:
    """
    Trigger a specific GitHub Actions workflow by name.

    Args:
        workflow_name: The workflow file name (e.g., "ai-civilization-loop.yml")
        inputs: Optional workflow inputs

    Returns:
        True if trigger was successful
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        logger.warning("GITHUB_TOKEN not set - cannot trigger workflow")
        return False

    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/actions/workflows/{workflow_name}/dispatches"

    try:
        async with httpx.AsyncClient() as client:
            payload = {"ref": "main"}
            if inputs:
                payload["inputs"] = inputs

            response = await client.post(
                url,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github.v3+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
                json=payload,
                timeout=30.0
            )

            if response.status_code == 204:
                logger.info(f"Successfully triggered workflow: {workflow_name}")
                return True
            else:
                logger.error(
                    f"Failed to trigger {workflow_name}: {response.status_code} - {response.text}"
                )
                return False

    except Exception as e:
        logger.error(f"Error triggering workflow {workflow_name}: {e}")
        return False


async def get_workflow_runs(workflow_name: str, limit: int = 5) -> list:
    """
    Get recent workflow runs for monitoring.

    Returns list of recent run status for the specified workflow.
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        return []

    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/actions/workflows/{workflow_name}/runs"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github.v3+json",
                },
                params={"per_page": limit},
                timeout=15.0
            )

            if response.status_code == 200:
                data = response.json()
                runs = []
                for run in data.get("workflow_runs", [])[:limit]:
                    runs.append({
                        "id": run["id"],
                        "status": run["status"],
                        "conclusion": run.get("conclusion"),
                        "created_at": run["created_at"],
                        "html_url": run["html_url"],
                    })
                return runs
            else:
                logger.warning(f"Failed to get workflow runs: {response.status_code}")
                return []

    except Exception as e:
        logger.error(f"Error getting workflow runs: {e}")
        return []


class AIDispatcher:
    """
    Wrapper class for AI Company dispatching functionality.

    Provides a clean interface for other services to dispatch work to agents.
    """

    @staticmethod
    async def dispatch_event(agent: str, event_id: str, event_data: dict) -> bool:
        """Dispatch an event to an agent for processing."""
        return await dispatch_to_agent_async(agent, {
            "event_id": event_id,
            "event": event_data
        })

    @staticmethod
    async def dispatch_task(agent: str, task: str, context: dict = None) -> bool:
        """Dispatch a task to an agent."""
        return await dispatch_to_agent_async(agent, {
            "task": task,
            "context": context or {}
        })

    @staticmethod
    async def dispatch_urgent(event_id: str, event_data: dict) -> bool:
        """Dispatch a critical event for immediate handling."""
        return await dispatch_to_agent_async("urgent", {
            "event_id": event_id,
            "event": event_data
        })

    @staticmethod
    async def trigger_loop() -> bool:
        """Trigger the main AI Company processing loop."""
        return await trigger_workflow("ai-civilization-loop.yml")

    @staticmethod
    async def trigger_briefing() -> bool:
        """Trigger the morning briefing generation."""
        return await trigger_workflow("ai-civilization-morning.yml")
