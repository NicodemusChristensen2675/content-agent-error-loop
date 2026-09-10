"""A small content-agent loop with build, release, and diagnostic events."""
import traceback
from collections.abc import Callable
from typing import Any

from infrai_client import InfraiClient


def run_content_step(
    client: InfraiClient,
    agent: str,
    step: str,
    operation: Callable[..., Any],
    **inputs: Any,
) -> Any:
    """Run one creator-tool step and capture a grouped diagnostic when it fails."""
    try:
        return operation(**inputs)
    except Exception as exc:
        client.capture(
            title=f"{agent}/{step} failed",
            message=f"{type(exc).__name__}: {exc}",
            level="error",
            fingerprint=[agent, step],
            exception=traceback.format_exc(),
            context={"agent": agent, "step": step, "inputs": inputs},
        )
        raise


def build_release_plan(asset_id: str, revision: str) -> dict[str, str]:
    """Return the release decision used by a publishing worker."""
    if not asset_id.strip() or not revision.strip():
        return {"status": "blocked", "reason": "asset and revision are required"}
    return {"status": "ready", "asset_id": asset_id, "revision": revision}


if __name__ == "__main__":
    client = InfraiClient()
    plan = build_release_plan("clip-042", "rev-7")
    print(plan)

    def render(**_: Any) -> str:
        raise ValueError("missing caption track")

    try:
        run_content_step(client, "editor-agent", "render-preview", render, asset_id="clip-042")
    except ValueError:
        print("diagnostic captured for editor-agent/render-preview")
