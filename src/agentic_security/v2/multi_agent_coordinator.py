"""Multi-agent coordination via QUIC synchronization"""

import logging
import subprocess
import asyncio
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class MultiAgentCoordinator:
    """Coordinates multiple security agents via QUIC sync"""

    def __init__(self, db_path: str = "./agentdb.db"):
        self.db_path = db_path
        self.server_process = None
        self.connected_agents = {}
        self.sync_server = None

    async def start_sync_server(
        self,
        port: int = 4433,
        auth_token: Optional[str] = None
    ) -> Dict:
        """Start QUIC synchronization server"""
        if self.server_process:
            raise RuntimeError("Sync server already running")

        logger.info(f"Starting sync server on port {port}")

        cmd = [
            'npx', 'agentdb', 'sync', 'start-server',
            '--port', str(port)
        ]

        if auth_token:
            cmd.extend(['--auth-token', auth_token])

        self.server_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Wait a bit for server to start
        await asyncio.sleep(2)

        self.sync_server = {
            'port': port,
            'auth_token': auth_token,
            'status': 'running'
        }

        logger.info(f"Sync server started on port {port}")
        return self.sync_server

    async def connect_to_server(
        self,
        host: str,
        port: int,
        auth_token: str
    ) -> bool:
        """Connect to a remote sync server"""
        logger.info(f"Connecting to sync server at {host}:{port}")

        cmd = [
            'npx', 'agentdb', 'sync', 'connect',
            host, str(port),
            '--auth-token', auth_token
        ]

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            await proc.communicate()

            if proc.returncode == 0:
                self.connected_agents[f"{host}:{port}"] = {
                    'host': host,
                    'port': port,
                    'connected_at': asyncio.get_event_loop().time()
                }
                logger.info(f"Connected to {host}:{port}")
                return True
        except Exception as e:
            logger.error(f"Failed to connect: {e}")

        return False

    async def sync_push(
        self,
        server: str,
        incremental: bool = True
    ) -> bool:
        """Push local changes to server"""
        logger.info(f"Pushing changes to {server}")

        cmd = [
            'npx', 'agentdb', 'sync', 'push',
            '--server', server
        ]

        if incremental:
            cmd.append('--incremental')

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            await proc.communicate()
            return proc.returncode == 0
        except Exception as e:
            logger.error(f"Sync push failed: {e}")
            return False

    async def sync_pull(
        self,
        server: str,
        incremental: bool = True
    ) -> bool:
        """Pull remote changes from server"""
        logger.info(f"Pulling changes from {server}")

        cmd = [
            'npx', 'agentdb', 'sync', 'pull',
            '--server', server
        ]

        if incremental:
            cmd.append('--incremental')

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            await proc.communicate()
            return proc.returncode == 0
        except Exception as e:
            logger.error(f"Sync pull failed: {e}")
            return False

    async def stop_sync_server(self):
        """Stop the sync server"""
        if self.server_process:
            logger.info("Stopping sync server")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
            self.server_process = None
            self.sync_server = None

    def get_connected_agents(self) -> List[Dict]:
        """Get list of connected agents"""
        return list(self.connected_agents.values())
