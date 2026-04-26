import os
from google.adk.agents.llm_agent import LlmAgent
from google.adk.a2a.utils.agent_to_a2a import to_a2a

def check_mcp_vulnerability(server_name: str) -> str:
    """Simulates a technical scan of an MCP server's exposed tools."""
    # In a real scenario, this would execute a subprocess or a network scan
    return f"CRITICAL: Vulnerability confirmed in {server_name}. Unauthenticated tool execution exposed."

# Define the specialized worker
verification_agent = LlmAgent(
    name="mcp_verification_agent",
    model="gemini-2.0-flash",
    description="Specialized agent for verifying MCP server vulnerabilities.",
    instruction=(
        "You are a Security Verification Agent. Use the check_mcp_vulnerability tool "
        "to confirm security alerts. Return a concise, structured verdict."
    ),
    tools=[check_mcp_vulnerability]
)

# Convert the agent into a deployable A2A server
app = to_a2a(verification_agent)


FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
RUN uv pip install --system google-adk uvicorn

COPY verification_server.py .
# Port 8080 is the default for Cloud Run
CMD ["uvicorn", "verification_server:app", "--host", "0.0.0.0", "--port", "8080"]
Dep


# Deploy to Cloud Run without public access
gcloud run deploy mcp-verifier \
    --source . \
    --no-allow-unauthenticated \
    --region us-central1
    
    

# 1. Create the Service Account
gcloud iam service-accounts create orchestrator-sa \
    --display-name="Orchestrator Identity"

# 2. Grant it permission to call the specific Verification service
gcloud run services add-iam-policy-binding mcp-verifier \
    --region us-central1 \
    --member="serviceAccount:orchestrator-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/run.invoker"
    
    
    import json
from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.runners import Runner

# Connect to the Secure Cloud Run endpoint via A2A
remote_verifier = RemoteA2aAgent(
    name="remote_mcp_verifier",
    description="Specialized agent for verifying MCP server vulnerabilities.",
    url="https://mcp-verifier-xyz.a.run.app/.well-known/agent-card.json" # Your Cloud Run URL
)

orchestrator = LlmAgent(
    name="security_orchestrator",
    model="gemini-1.5-pro",
    description="Orchestrating agent who knows which routes the call to appropriate verification and remediation agent",
    instruction="Analyze the incoming security alert and delegate verification to the remote agent.",
    tools=[remote_verifier]
)
    

# Mock Data: A simulated high-severity alert
mock_alert = {
    "target_service": "mongodb-mcp-server",
    "threat_level": "High",
    "exposed_components": ["schema-compression-codecs", "materialized-views"]
}

runner = Runner(agent=orchestrator)
print(runner.run(json.dumps(mock_alert)).content)



impport os
from google.adk.cli.fast_api import get_fast_api_app
from fastapi import FastAPI

# Set GOOGLE_CLOUD_PROJECT for seamless OpenTelemetry cloud tracing
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", os.getenv("PROJECT_ID", "your-gcp-project-id"))

# Discover the orchestrator agent in the current working directory
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))

# The ADK dynamically creates the FastAPI app and endpoints
app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=True,
    trace_to_cloud=True,
)

app.title = "security-orchestrator"
app.description = "API for interacting with the Security Triage Orchestrator"

# Main execution for Cloud Run
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
    
    
  [Orchestrator] Received Alert: SEC-2026-891 (mongodb-mcp-server)
[Orchestrator] Handoff initiated. Generating OIDC token for Cloud Run...
[A2A Gateway] Authentication Successful. Invoking 'mcp-verifier-agent'...

[Remote Verifier] Task Received: Verify 'mongodb-mcp-server' configuration.
[Remote Verifier] Executing tool: check_mcp_vulnerability()
[Remote Verifier] Result: Unauthenticated tool execution confirmed on port 443.
[A2A Gateway] Task complete. Returning result to Orchestrator.

[Orchestrator] Final Synthesis complete.  
    
    
    
    # 1. Define the new expert endpoint
remote_remediator = RemoteA2aAgent(
    name="remediation_agent",
    url="https://mcp-remediator-xyz.a.run.app/.well-known/agent-card.json",
    description="Expert at generating and applying security patches."
)


# 2. Add it to the Orchestrator's toolkit
orchestrator = LlmAgent(
    name="security_orchestrator",
    model="gemini-1.5-pro",
    description="Orchestrating agent who knows which routes the call to appropriate verification and remediation agent",
    instruction=(
        "If the 'remote_mcp_verifier' confirms a threat, "
        "immediately delegate the fix to 'remediation_agent'. "
        "Your goal is a zero-touch 'Detect-Verify-Patch' pipeline."
    ),
    tools=[remote_verifier, remote_remediator]
   )