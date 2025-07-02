"""
MCP (Model Context Protocol) Manager
Handles MCP server connections and tool execution
"""

import asyncio
import json
import logging
import os
import subprocess
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from pydantic import BaseModel

logger = logging.getLogger(__name__)


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server"""

    name: str
    command: str
    args: List[str] = None
    env: Dict[str, str] = None
    working_dir: Optional[str] = None
    description: str = ""
    enabled: bool = True


class MCPToolInfo(BaseModel):
    """Information about an available MCP tool"""

    name: str
    description: str
    server_name: str
    parameters: Dict[str, Any] = {}


class MCPResourceInfo(BaseModel):
    """Information about an available MCP resource"""

    uri: str
    name: str
    description: str
    server_name: str
    mime_type: Optional[str] = None


@dataclass
class MCPConnection:
    """Active MCP server connection"""

    config: MCPServerConfig
    session: ClientSession
    process: Optional[subprocess.Popen]
    tools: List[MCPToolInfo]
    resources: List[MCPResourceInfo]
    connected: bool = True


class MCPManager:
    """Manages MCP server connections and tool execution"""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "mcp-servers.json"
        self.connections: Dict[str, MCPConnection] = {}
        self.server_configs: Dict[str, MCPServerConfig] = {}
        self._load_configs()

    def _load_configs(self):
        """Load MCP server configurations from file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r") as f:
                    data = json.load(f)

                for name, config_data in data.get("servers", {}).items():
                    self.server_configs[name] = MCPServerConfig(
                        name=name,
                        command=config_data["command"],
                        args=config_data.get("args", []),
                        env=config_data.get("env", {}),
                        working_dir=config_data.get("working_dir"),
                        description=config_data.get("description", ""),
                        enabled=config_data.get("enabled", True),
                    )

                logger.info(f"Loaded {len(self.server_configs)} MCP server configurations")
            else:
                logger.info(f"No MCP config file found at {self.config_path}, creating default")
                self._create_default_config()

        except Exception as e:
            logger.error(f"Error loading MCP configs: {e}")
            self._create_default_config()

    def _create_default_config(self):
        """Create a default MCP configuration file"""
        default_config = {
            "servers": {
                "filesystem": {
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
                    "description": "File system access server",
                    "enabled": False,
                },
                "brave-search": {
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-brave-search"],
                    "env": {"BRAVE_API_KEY": "your_brave_api_key_here"},
                    "description": "Brave search server",
                    "enabled": False,
                },
                "memory": {
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-memory"],
                    "description": "Persistent memory server",
                    "enabled": False,
                },
            }
        }

        try:
            with open(self.config_path, "w") as f:
                json.dump(default_config, f, indent=2)
            logger.info(f"Created default MCP config at {self.config_path}")
        except Exception as e:
            logger.error(f"Error creating default config: {e}")

    async def connect_server(self, server_name: str) -> bool:
        """Connect to an MCP server"""
        if server_name not in self.server_configs:
            logger.error(f"Server config not found: {server_name}")
            return False

        if server_name in self.connections:
            logger.warning(f"Already connected to server: {server_name}")
            return True

        config = self.server_configs[server_name]
        if not config.enabled:
            logger.info(f"Server {server_name} is disabled")
            return False

        try:
            # Prepare environment
            env = os.environ.copy()
            if config.env:
                env.update(config.env)

            # Start the MCP server process
            cmd = [config.command] + (config.args or [])

            # Create server parameters
            server_params = StdioServerParameters(command=cmd[0], args=cmd[1:] if len(cmd) > 1 else [], env=env)

            # Create MCP client session
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    # Initialize the session
                    await session.initialize()

                    # Get available tools and resources
                    tools_result = await session.list_tools()
                    resources_result = await session.list_resources()

                    # Convert to our data structures
                    tools = [
                        MCPToolInfo(
                            name=tool.name,
                            description=tool.description or "",
                            server_name=server_name,
                            parameters=tool.inputSchema.get("properties", {}) if tool.inputSchema else {},
                        )
                        for tool in tools_result.tools
                    ]

                    resources = [
                        MCPResourceInfo(
                            uri=resource.uri,
                            name=resource.name or resource.uri,
                            description=resource.description or "",
                            server_name=server_name,
                            mime_type=resource.mimeType,
                        )
                        for resource in resources_result.resources
                    ]

                    # Store the connection (we'll need to keep this alive differently)
                    connection = MCPConnection(
                        config=config,
                        session=session,
                        process=None,  # Process is managed by stdio_client
                        tools=tools,
                        resources=resources,
                    )

                    self.connections[server_name] = connection
                    logger.info(f"Connected to MCP server: {server_name} ({len(tools)} tools, {len(resources)} resources)")
                    return True

        except Exception as e:
            logger.error(f"Error connecting to MCP server {server_name}: {e}")
            return False

    async def disconnect_server(self, server_name: str) -> bool:
        """Disconnect from an MCP server"""
        if server_name not in self.connections:
            logger.warning(f"Not connected to server: {server_name}")
            return False

        try:
            connection = self.connections[server_name]
            connection.connected = False

            # Close the session and process (if managed by us)
            if connection.process:
                connection.process.terminate()
                await connection.process.wait()

            del self.connections[server_name]
            logger.info(f"Disconnected from MCP server: {server_name}")
            return True

        except Exception as e:
            logger.error(f"Error disconnecting from MCP server {server_name}: {e}")
            return False

    async def execute_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool on an MCP server"""
        if server_name not in self.connections:
            return {"success": False, "error": f"Not connected to server: {server_name}", "result": None}

        try:
            connection = self.connections[server_name]
            if not connection.connected:
                return {"success": False, "error": f"Connection to {server_name} is not active", "result": None}

            # Execute the tool
            result = await connection.session.call_tool(tool_name, arguments)

            return {"success": True, "error": None, "result": result.content[0].text if result.content else None}

        except Exception as e:
            logger.error(f"Error executing tool {tool_name} on {server_name}: {e}")
            return {"success": False, "error": str(e), "result": None}

    async def get_resource(self, server_name: str, uri: str) -> Dict[str, Any]:
        """Get a resource from an MCP server"""
        if server_name not in self.connections:
            return {"success": False, "error": f"Not connected to server: {server_name}", "content": None}

        try:
            connection = self.connections[server_name]
            if not connection.connected:
                return {"success": False, "error": f"Connection to {server_name} is not active", "content": None}

            # Get the resource
            result = await connection.session.read_resource(uri)

            return {"success": True, "error": None, "content": result.contents[0].text if result.contents else None}

        except Exception as e:
            logger.error(f"Error getting resource {uri} from {server_name}: {e}")
            return {"success": False, "error": str(e), "content": None}

    def list_servers(self) -> Dict[str, Dict[str, Any]]:
        """List all configured servers and their connection status"""
        servers = {}

        for name, config in self.server_configs.items():
            connection = self.connections.get(name)
            servers[name] = {
                "name": name,
                "description": config.description,
                "enabled": config.enabled,
                "connected": connection is not None and connection.connected,
                "tools_count": len(connection.tools) if connection else 0,
                "resources_count": len(connection.resources) if connection else 0,
            }

        return servers

    def list_tools(self, server_name: Optional[str] = None) -> List[MCPToolInfo]:
        """List available tools from connected servers"""
        tools = []

        if server_name:
            connection = self.connections.get(server_name)
            if connection and connection.connected:
                tools.extend(connection.tools)
        else:
            for connection in self.connections.values():
                if connection.connected:
                    tools.extend(connection.tools)

        return tools

    def list_resources(self, server_name: Optional[str] = None) -> List[MCPResourceInfo]:
        """List available resources from connected servers"""
        resources = []

        if server_name:
            connection = self.connections.get(server_name)
            if connection and connection.connected:
                resources.extend(connection.resources)
        else:
            for connection in self.connections.values():
                if connection.connected:
                    resources.extend(connection.resources)

        return resources

    async def connect_all_enabled(self):
        """Connect to all enabled servers"""
        tasks = []
        for name, config in self.server_configs.items():
            if config.enabled:
                tasks.append(self.connect_server(name))

        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            connected_count = sum(1 for result in results if result is True)
            logger.info(f"Connected to {connected_count}/{len(tasks)} enabled MCP servers")

    async def disconnect_all(self):
        """Disconnect from all servers"""
        tasks = []
        for name in list(self.connections.keys()):
            tasks.append(self.disconnect_server(name))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
            logger.info("Disconnected from all MCP servers")
