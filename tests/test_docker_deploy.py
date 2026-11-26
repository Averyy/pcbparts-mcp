"""Deploy failure handling with a shell-function Docker stub; no containers or network."""

import os
from pathlib import Path
import shutil
import subprocess

import pytest
import yaml


@pytest.mark.skipif(os.name == "nt" or not shutil.which("sh"), reason="requires a POSIX shell")
@pytest.mark.parametrize("failed, succeeds", [
    ("", True),
    ("compose up -d --remove-orphans pcbparts-mcp", False),
    ("compose pull pcbparts-dashboard", True),
    ("compose up -d pcbparts-dashboard", True),
], ids=["success", "server", "dashboard-pull", "dashboard-start"])
def test_deploy_requires_server_start_and_keeps_dashboard_best_effort(tmp_path, failed, succeeds):
    root = Path(__file__).resolve().parents[1]
    workflow = yaml.safe_load((root / ".github/workflows/docker-build.yml").read_text(encoding="utf-8"))
    script = next(step["with"]["script"] for step in workflow["jobs"]["build-and-push"]["steps"]
                  if str(step.get("uses", "")).startswith("appleboy/ssh-action"))
    # Run only the service update and cleanup; every Docker command resolves to this function.
    script = script[script.index("export COMPOSE_PROFILES=dashboard"):]
    log = tmp_path / "docker.log"
    stub = '''
docker() {
    printf '%s\\n' "$*" >> "$DEPLOY_TEST_LOG"
    if [ "$*" = "$DEPLOY_TEST_FAILURE" ]; then return 42; fi
    return 0
}
'''
    result = subprocess.run(["sh", "-c", stub + script], capture_output=True, text=True,
                            encoding="utf-8", timeout=10,
                            env={**os.environ, "DEPLOY_TEST_LOG": str(log), "DEPLOY_TEST_FAILURE": failed})
    assert (result.returncode == 0) is succeeds, result.stderr
    assert ("Deployed successfully!" in result.stdout) is succeeds
    calls = log.read_text(encoding="utf-8").splitlines()
    if succeeds:
        assert calls[-1] == "image prune -f"
    else:
        assert "MCP server failed to start; deployment failed." in result.stdout
        assert calls == ["compose pull pcbparts-mcp", "compose up -d --remove-orphans pcbparts-mcp"]
