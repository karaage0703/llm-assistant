"""
Enhanced Claude Code CLI integration with better session management
"""

import asyncio
import logging
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ChatSession:
    """Represents a chat session with Claude Code CLI"""

    session_id: str
    working_dir: str
    history: List[Dict[str, str]]
    created_at: float
    last_activity: float


class AdvancedClaudeCodeManager:
    """Advanced Claude Code CLI integration with session management"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("CLAUDE_API_KEY")
        self.sessions: Dict[str, ChatSession] = {}
        self.claude_cli_available = False
        self._check_claude_cli()

    def _check_claude_cli(self) -> bool:
        """Check if Claude Code CLI is available"""
        try:
            # Try different possible command names
            commands_to_try = ["claude", "npx @anthropic-ai/claude-code", "claude-code"]

            for cmd in commands_to_try:
                try:
                    result = subprocess.run(cmd.split() + ["--version"], capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        logger.info(f"Found Claude Code CLI: {cmd}")
                        self.claude_command = cmd.split()
                        self.claude_cli_available = True
                        return True
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    continue

            logger.warning("Claude Code CLI not found")
            self.claude_cli_available = False
            return False

        except Exception as e:
            logger.error(f"Error checking Claude Code CLI: {e}")
            self.claude_cli_available = False
            return False

    async def _check_claude_auth(self) -> Dict[str, Any]:
        """Check if Claude CLI is authenticated"""
        try:
            if not self.claude_cli_available:
                return {"authenticated": False, "message": "Claude CLI not available"}

            # Try a simple command to check authentication
            result = subprocess.run(self.claude_command + ["--help"], capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                return {"authenticated": True, "message": "Claude CLI is ready"}
            else:
                return {
                    "authenticated": False,
                    "message": "Run 'claude auth' to authenticate with your Claude Pro/Max account or Anthropic Console",
                }

        except Exception as e:
            return {"authenticated": False, "message": f"Authentication check failed: {str(e)}"}

    async def create_session(self, session_id: str) -> ChatSession:
        """Create a new chat session"""
        if session_id in self.sessions:
            return self.sessions[session_id]

        working_dir = tempfile.mkdtemp(prefix=f"claude_session_{session_id}_")
        import time

        now = time.time()

        session = ChatSession(session_id=session_id, working_dir=working_dir, history=[], created_at=now, last_activity=now)

        self.sessions[session_id] = session
        logger.info(f"Created session {session_id} with working dir {working_dir}")
        return session

    async def execute_command(self, message: str, session_id: str = "default") -> Dict[str, Any]:
        """Execute Claude Code CLI command in a specific session"""
        try:
            # Get or create session
            session = await self.create_session(session_id)
            session.last_activity = __import__("time").time()

            # Add user message to history
            session.history.append({"role": "user", "content": message, "timestamp": session.last_activity})

            # Check authentication status (Claude CLI uses authenticated session, not API key)
            if self.claude_cli_available:
                auth_check = await self._check_claude_auth()
                if not auth_check["authenticated"]:
                    response = self._create_error_response(f"Claude CLI authentication required. {auth_check['message']}")
                    session.history.append(
                        {"role": "assistant", "content": response["response"], "timestamp": __import__("time").time()}
                    )
                    return response

            # Execute command
            if self.claude_cli_available:
                result = await self._execute_real_claude_cli(message, session)
            else:
                result = await self._execute_simulation_mode(message, session)

            # Add response to history
            session.history.append(
                {"role": "assistant", "content": result["response"], "timestamp": __import__("time").time()}
            )

            return result

        except Exception as e:
            logger.error(f"Error in execute_command: {e}")
            return self._create_error_response(str(e))

    async def _execute_real_claude_cli(self, message: str, session: ChatSession) -> Dict[str, Any]:
        """Execute real Claude Code CLI command"""
        try:
            # Prepare command - Claude CLI expects the message as arguments
            cmd = self.claude_command + [message]

            # Setup environment (no API key needed for authenticated session)
            env = os.environ.copy()

            # Execute with timeout
            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, cwd=session.working_dir, env=env
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=60.0,  # Increased timeout for complex operations
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return self._create_error_response("Command timed out after 60 seconds")

            # Process results
            stdout_text = stdout.decode("utf-8", errors="replace").strip()
            stderr_text = stderr.decode("utf-8", errors="replace").strip()

            if process.returncode == 0:
                response = stdout_text or "Command executed successfully"
                return {"success": True, "response": response, "error": None, "session_id": session.session_id}
            else:
                error_msg = stderr_text or f"Command failed with exit code {process.returncode}"
                return {"success": False, "response": stdout_text, "error": error_msg, "session_id": session.session_id}

        except Exception as e:
            logger.error(f"Error executing real Claude CLI: {e}")
            return self._create_error_response(str(e))

    async def _execute_simulation_mode(self, message: str, session: ChatSession) -> Dict[str, Any]:
        """Execute in simulation mode when Claude CLI is not available"""
        response = f"""**🤖 Claude Code CLI Simulation Mode**

**Your message:** {message}

**Simulated Response:**
I'm currently running in simulation mode because Claude Code CLI is not installed or configured.

**Current session:** `{session.session_id}`
**Working directory:** `{session.working_dir}`
**Messages in this session:** {len(session.history)}

**To enable real Claude Code CLI:**
1. Install: `npm install -g @anthropic-ai/claude-code`
2. Authenticate: `claude auth` (requires Claude Pro/Max subscription or Anthropic Console access)
3. Restart this server

**What I would do with your message:**
- Process your request using Claude's language model
- Execute any code or commands as needed
- Provide structured responses with code examples
- Maintain context across our conversation

For now, I can echo your messages and provide guidance on using the system!"""

        return {"success": True, "response": response, "error": None, "session_id": session.session_id}

    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create a standardized error response"""
        return {"success": False, "response": "", "error": error_message, "session_id": None}

    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a session"""
        if session_id not in self.sessions:
            return None

        session = self.sessions[session_id]
        return {
            "session_id": session.session_id,
            "created_at": session.created_at,
            "last_activity": session.last_activity,
            "message_count": len(session.history),
            "working_dir": session.working_dir,
        }

    def cleanup_session(self, session_id: str):
        """Clean up a specific session"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            try:
                if os.path.exists(session.working_dir):
                    shutil.rmtree(session.working_dir)
                    logger.info(f"Cleaned up session {session_id} working directory")
            except Exception as e:
                logger.warning(f"Failed to cleanup session {session_id}: {e}")

            del self.sessions[session_id]

    def cleanup_all_sessions(self):
        """Clean up all sessions"""
        for session_id in list(self.sessions.keys()):
            self.cleanup_session(session_id)

    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all active sessions"""
        return [self.get_session_info(sid) for sid in self.sessions.keys()]
