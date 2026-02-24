"""
FastMCP Gmail Server (Silver Tier)

Standalone HTTP MCP server that exposes Gmail API tools.
Run this server independently, then connect via MCPClient.

Usage:
    python -m ai_employee.mcp.gmail_mcp_server

    Or with uvicorn:
    uvicorn ai_employee.mcp.gmail_mcp_server:app --host 0.0.0.0 --port 8000
"""
from mcp.server.fastmcp import FastMCP
from email.mime.text import MIMEText
import base64
from .gmail_client import get_gmail_service
from fastapi import FastAPI  

# Create MCP server
mcp = FastMCP("AI-Employee-Gmail", stateless_http=True)

service = get_gmail_service()

@mcp.tool()
def gmail_list_messages(max_results: int = 5, query: str = "") -> list:
    results = service.users().messages().list(
        userId="me", maxResults=max_results, q=query
    ).execute()
    messages = results.get("messages", [])
    output = []
    for m in messages:
        msg = service.users().messages().get(userId="me", id=m["id"], format="metadata").execute()
        snippet = msg.get("snippet", "")
        output.append({"id": m["id"], "snippet": snippet})
    return output

@mcp.tool()
def gmail_get_message(message_id: str) -> dict:
    msg = service.users().messages().get(userId="me", id=message_id, format="full").execute()
    headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}
    body_data = ""
    if "parts" in msg["payload"]:
        for part in msg["payload"]["parts"]:
            if part["mimeType"] == "text/plain" and "data" in part["body"]:
                body_data = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
    else:
        body_data = base64.urlsafe_b64decode(msg["payload"]["body"].get("data", "")).decode("utf-8")

    return {
        "subject": headers.get("Subject", ""),
        "from": headers.get("From", ""),
        "to": headers.get("To", ""),
        "snippet": msg.get("snippet", ""),
        "body": body_data,
    }


@mcp.tool()
def gmail_send_email(to: str, subject: str, body: str) -> dict:
    """Send email via Gmail API and return structured result."""
    message = MIMEText(body)
    message["to"] = to
    message["subject"] = subject

    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    send_message = service.users().messages().send(
        userId="me", body={"raw": encoded_message}
    ).execute()

    return {
        "status": "success",
        "message_id": send_message.get("id", ""),
        "to": to,
        "subject": subject
    }


mcp_app = mcp.streamable_http_app()
app = FastAPI()
app.mount("/", mcp_app)


if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("FastMCP Gmail Server - Silver Tier")
    print("=" * 60)
    print("Starting server on http://localhost:8000")
    print("MCP endpoint: http://localhost:8000/mcp")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000)

