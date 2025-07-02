"""
FastAPI backend for LLM Assistant Bot
"""

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from typing import Any, Dict

from claude_integration import AdvancedClaudeCodeManager
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from mcp_manager import MCPManager
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize managers
claude_manager = AdvancedClaudeCodeManager()
mcp_manager = MCPManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing MCP servers...")
    asyncio.create_task(mcp_manager.connect_all_enabled())
    yield
    # Shutdown
    logger.info("Shutting down, cleaning up MCP connections...")
    await mcp_manager.disconnect_all()
    claude_manager.cleanup_all_sessions()


app = FastAPI(title="LLM Assistant Bot", version="0.1.0", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Models
class ChatMessage(BaseModel):
    message: str
    session_id: str = "default"


class ClaudeResponse(BaseModel):
    response: str
    session_id: str
    success: bool
    error: str = None


class MCPToolRequest(BaseModel):
    server_name: str
    tool_name: str
    arguments: Dict[str, Any] = {}


class MCPResourceRequest(BaseModel):
    server_name: str
    uri: str


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client {client_id} connected")

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Client {client_id} disconnected")

    async def send_personal_message(self, message: dict, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(json.dumps(message))

    async def broadcast(self, message: dict):
        for connection in self.active_connections.values():
            await connection.send_text(json.dumps(message))


manager = ConnectionManager()


# Routes
@app.get("/")
async def root():
    return {"message": "LLM Assistant Bot API is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "llm-assistant-bot"}


@app.get("/api/sessions")
async def list_sessions():
    """List all active sessions"""
    return {"sessions": claude_manager.list_sessions()}


@app.get("/api/sessions/{session_id}")
async def get_session_info(session_id: str):
    """Get information about a specific session"""
    session_info = claude_manager.get_session_info(session_id)
    if session_info is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return session_info


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a specific session"""
    session_info = claude_manager.get_session_info(session_id)
    if session_info is None:
        raise HTTPException(status_code=404, detail="Session not found")

    claude_manager.cleanup_session(session_id)
    return {"message": f"Session {session_id} deleted successfully"}


# ===== MCP API Endpoints =====


@app.get("/api/mcp/servers")
async def list_mcp_servers():
    """List all MCP servers and their status"""
    return {"servers": mcp_manager.list_servers()}


@app.post("/api/mcp/servers/{server_name}/connect")
async def connect_mcp_server(server_name: str):
    """Connect to an MCP server"""
    success = await mcp_manager.connect_server(server_name)
    if success:
        return {"message": f"Connected to {server_name}", "success": True}
    else:
        raise HTTPException(status_code=400, detail=f"Failed to connect to {server_name}")


@app.post("/api/mcp/servers/{server_name}/disconnect")
async def disconnect_mcp_server(server_name: str):
    """Disconnect from an MCP server"""
    success = await mcp_manager.disconnect_server(server_name)
    if success:
        return {"message": f"Disconnected from {server_name}", "success": True}
    else:
        raise HTTPException(status_code=400, detail=f"Failed to disconnect from {server_name}")


@app.get("/api/mcp/tools")
async def list_mcp_tools(server_name: str = None):
    """List available MCP tools"""
    tools = mcp_manager.list_tools(server_name)
    return {"tools": [tool.model_dump() for tool in tools]}


@app.get("/api/mcp/resources")
async def list_mcp_resources(server_name: str = None):
    """List available MCP resources"""
    resources = mcp_manager.list_resources(server_name)
    return {"resources": [resource.model_dump() for resource in resources]}


@app.post("/api/mcp/tools/execute")
async def execute_mcp_tool(request: MCPToolRequest):
    """Execute an MCP tool"""
    result = await mcp_manager.execute_tool(request.server_name, request.tool_name, request.arguments)
    return result


@app.post("/api/mcp/resources/get")
async def get_mcp_resource(request: MCPResourceRequest):
    """Get an MCP resource"""
    result = await mcp_manager.get_resource(request.server_name, request.uri)
    return result


@app.post("/api/chat", response_model=ClaudeResponse)
async def chat_endpoint(message: ChatMessage):
    """Process chat message through Claude Code CLI"""
    try:
        result = await claude_manager.execute_command(message.message, message.session_id)

        return ClaudeResponse(
            response=result["response"], session_id=message.session_id, success=result["success"], error=result["error"]
        )

    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            # Process message through Claude Code CLI with session support
            session_id = message_data.get("session_id", "default")
            result = await claude_manager.execute_command(message_data.get("message", ""), session_id)

            # Send response back to client
            response = {
                "type": "response",
                "data": {
                    "response": result["response"],
                    "success": result["success"],
                    "error": result["error"],
                    "session_id": result.get("session_id", session_id),
                },
            }

            await manager.send_personal_message(response, client_id)

    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        manager.disconnect(client_id)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
