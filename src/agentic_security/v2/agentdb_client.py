"""
AgentDB Python client wrapper for persistent memory and learning.

This module provides a Python interface to AgentDB (v1.6.1) for:
- Episode storage and reflexion
- Skill library management
- Causal reasoning
- Multi-agent synchronization
"""

import subprocess
import json
import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class Episode:
    """Reflexion episode representing a learning experience"""
    session_id: str
    task: str
    reward: float
    success: bool
    critique: Optional[str] = None
    input_data: Optional[str] = None
    output_data: Optional[str] = None
    latency_ms: Optional[int] = None
    tokens: Optional[int] = None
    metadata: Optional[Dict] = None

    def to_dict(self):
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class Skill:
    """Reusable skill pattern"""
    name: str
    description: str
    code: Optional[str] = None
    metadata: Optional[Dict] = None
    success_rate: Optional[float] = None
    usage_count: Optional[int] = None

    def to_dict(self):
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class CausalEdge:
    """Causal relationship between cause and effect"""
    cause: str
    effect: str
    uplift: float
    confidence: float
    sample_size: int

    def to_dict(self):
        return asdict(self)


class AgentDBClient:
    """
    Python client for AgentDB operations

    Usage:
        agentdb = AgentDBClient("./agentdb.db")

        # Store episode
        await agentdb.store_episode(episode)

        # Query experiences
        results = await agentdb.retrieve_episodes("scan:auth", k=5)

        # Search skills
        skills = await agentdb.search_skills("SQL injection")
    """

    def __init__(self, db_path: str = "./agentdb.db"):
        self.db_path = Path(db_path)
        self.ensure_initialized()

    def ensure_initialized(self):
        """Ensure database exists and is initialized"""
        if not self.db_path.exists():
            logger.info(f"Initializing AgentDB at {self.db_path}")
            self._run_command([
                'init', str(self.db_path),
                '--dimension', '1536',
                '--preset', 'medium'
            ])
            logger.info("AgentDB initialized successfully")

    def _run_command(self, args: List[str],
                     capture_output: bool = True) -> subprocess.CompletedProcess:
        """Run agentdb command via npx"""
        cmd = ['npx', 'agentdb'] + args

        logger.debug(f"Running command: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=capture_output,
            text=True,
            check=False
        )

        if result.returncode != 0:
            logger.error(f"Command failed: {result.stderr}")
            raise RuntimeError(f"AgentDB command failed: {result.stderr}")

        return result

    async def _run_command_async(self, args: List[str]) -> str:
        """Run agentdb command asynchronously"""
        cmd = ['npx', 'agentdb'] + args

        logger.debug(f"Running async command: {' '.join(cmd)}")

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            logger.error(f"Command failed: {stderr.decode()}")
            raise RuntimeError(f"AgentDB command failed: {stderr.decode()}")

        return stdout.decode()

    # === REFLEXION OPERATIONS ===

    async def store_episode(self, episode: Episode) -> bool:
        """
        Store a reflexion episode

        Args:
            episode: Episode to store

        Returns:
            Success boolean

        Example:
            episode = Episode(
                session_id="scan-001",
                task="scan:authentication",
                reward=0.85,
                success=True,
                critique="Found SQL injection, applied parameterized queries"
            )
            await agentdb.store_episode(episode)
        """
        cmd = [
            'reflexion', 'store',
            episode.session_id,
            episode.task,
            str(episode.reward),
            str(episode.success).lower()
        ]

        if episode.critique:
            cmd.append(episode.critique)

        if episode.input_data:
            cmd.append(episode.input_data)

        if episode.output_data:
            cmd.append(episode.output_data)

        if episode.latency_ms:
            cmd.append(str(episode.latency_ms))

        if episode.tokens:
            cmd.append(str(episode.tokens))

        try:
            await self._run_command_async(cmd)
            logger.debug(f"Stored episode: {episode.task}")
            return True
        except Exception as e:
            logger.error(f"Failed to store episode: {e}")
            return False

    async def retrieve_episodes(
        self,
        task: str,
        k: int = 5,
        min_reward: Optional[float] = None,
        only_failures: bool = False,
        only_successes: bool = False,
        synthesize_context: bool = True,
        filters: Optional[str] = None
    ) -> Dict:
        """
        Retrieve relevant past episodes

        Args:
            task: Task description to search for
            k: Number of results
            min_reward: Minimum reward threshold
            only_failures: Only failed episodes
            only_successes: Only successful episodes
            synthesize_context: Generate coherent summary
            filters: MongoDB-style JSON filters

        Returns:
            Dict with episodes and optionally synthesized context

        Example:
            results = await agentdb.retrieve_episodes(
                task="SQL injection scan",
                k=10,
                only_successes=True,
                synthesize_context=True
            )
            print(results['synthesized_context'])
        """
        cmd = [
            'reflexion', 'retrieve',
            task,
            '--k', str(k),
            '--format', 'json'
        ]

        if min_reward is not None:
            cmd.extend(['--min-reward', str(min_reward)])

        if only_failures:
            cmd.append('--only-failures')

        if only_successes:
            cmd.append('--only-successes')

        if synthesize_context:
            cmd.append('--synthesize-context')

        if filters:
            cmd.extend(['--filters', filters])

        try:
            output = await self._run_command_async(cmd)
            return json.loads(output) if output.strip() else {'episodes': []}
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse response: {e}")
            return {'episodes': []}
        except Exception as e:
            logger.error(f"Failed to retrieve episodes: {e}")
            return {'episodes': []}

    async def critique_summary(
        self,
        task: str,
        only_failures: bool = False
    ) -> Dict:
        """Get aggregated critique lessons for a task"""
        cmd = ['reflexion', 'critique-summary', task]

        if only_failures:
            cmd.append('true')

        try:
            output = await self._run_command_async(cmd)
            return json.loads(output) if output.strip() else {}
        except Exception as e:
            logger.error(f"Failed to get critique summary: {e}")
            return {}

    # === SKILL OPERATIONS ===

    async def create_skill(self, skill: Skill) -> bool:
        """
        Create a reusable skill

        Args:
            skill: Skill to create

        Returns:
            Success boolean

        Example:
            skill = Skill(
                name="sql_injection_parameterized",
                description="Fix SQL injection with parameterized queries",
                code="# Use parameterized queries...",
                metadata={'language': 'python', 'category': 'sql'}
            )
            await agentdb.create_skill(skill)
        """
        cmd = [
            'skill', 'create',
            skill.name,
            skill.description
        ]

        if skill.code:
            cmd.append(skill.code)

        try:
            await self._run_command_async(cmd)
            logger.info(f"Created skill: {skill.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create skill: {e}")
            return False

    async def search_skills(
        self,
        query: str,
        k: int = 5
    ) -> List[Dict]:
        """
        Find applicable skills by similarity

        Args:
            query: Search query
            k: Number of results

        Returns:
            List of matching skills

        Example:
            skills = await agentdb.search_skills("SQL injection", k=5)
            for skill in skills:
                print(f"{skill['name']}: {skill['description']}")
        """
        cmd = ['skill', 'search', query, str(k)]

        try:
            output = await self._run_command_async(cmd)
            return json.loads(output) if output.strip() else []
        except Exception as e:
            logger.error(f"Failed to search skills: {e}")
            return []

    async def consolidate_skills(
        self,
        min_attempts: int = 3,
        min_reward: float = 0.7,
        time_window_days: int = 7,
        extract_patterns: bool = True
    ) -> Dict:
        """
        Auto-create skills from successful episodes

        Args:
            min_attempts: Minimum occurrences
            min_reward: Minimum reward threshold
            time_window_days: Time window for analysis
            extract_patterns: Use ML pattern extraction

        Returns:
            Consolidation results

        Example:
            results = await agentdb.consolidate_skills(
                min_attempts=3,
                min_reward=0.7,
                extract_patterns=True
            )
            print(f"Created {len(results.get('skills', []))} new skills")
        """
        cmd = [
            'skill', 'consolidate',
            str(min_attempts),
            str(min_reward),
            str(time_window_days)
        ]

        if extract_patterns:
            cmd.append('true')

        try:
            output = await self._run_command_async(cmd)
            return json.loads(output) if output.strip() else {'skills': []}
        except Exception as e:
            logger.error(f"Failed to consolidate skills: {e}")
            return {'skills': []}

    # === CAUSAL OPERATIONS ===

    async def add_causal_edge(self, edge: CausalEdge) -> bool:
        """Add a causal edge manually"""
        cmd = [
            'causal', 'add-edge',
            edge.cause,
            edge.effect,
            str(edge.uplift),
            str(edge.confidence),
            str(edge.sample_size)
        ]

        try:
            await self._run_command_async(cmd)
            logger.debug(f"Added causal edge: {edge.cause} → {edge.effect}")
            return True
        except Exception as e:
            logger.error(f"Failed to add causal edge: {e}")
            return False

    async def query_causal_edges(
        self,
        cause: Optional[str] = None,
        effect: Optional[str] = None,
        min_confidence: float = 0.7,
        min_uplift: float = 0.0,
        limit: int = 10
    ) -> List[Dict]:
        """Query causal edges with filters"""
        cmd = ['causal', 'query']

        if cause:
            cmd.append(cause)
        if effect:
            cmd.append(effect)

        cmd.extend([
            str(min_confidence),
            str(min_uplift),
            str(limit)
        ])

        try:
            output = await self._run_command_async(cmd)
            return json.loads(output) if output.strip() else []
        except Exception as e:
            logger.error(f"Failed to query causal edges: {e}")
            return []

    # === LEARNER OPERATIONS ===

    async def discover_patterns(
        self,
        min_attempts: int = 3,
        min_success_rate: float = 0.6,
        min_confidence: float = 0.7,
        dry_run: bool = False
    ) -> Dict:
        """
        Discover causal edges from episode patterns

        Args:
            min_attempts: Minimum attempts required
            min_success_rate: Minimum success rate
            min_confidence: Minimum confidence
            dry_run: Don't actually store edges

        Returns:
            Discovered patterns
        """
        cmd = [
            'learner', 'run',
            str(min_attempts),
            str(min_success_rate),
            str(min_confidence)
        ]

        if dry_run:
            cmd.append('true')

        try:
            output = await self._run_command_async(cmd)
            return json.loads(output) if output.strip() else {'patterns': []}
        except Exception as e:
            logger.error(f"Failed to discover patterns: {e}")
            return {'patterns': []}

    # === QUERY OPERATIONS ===

    async def semantic_query(
        self,
        query: str,
        domain: Optional[str] = None,
        k: int = 5,
        min_confidence: float = 0.0,
        synthesize_context: bool = True,
        filters: Optional[str] = None
    ) -> Dict:
        """
        Semantic search across stored episodes and patterns

        Args:
            query: Query string
            domain: Domain filter
            k: Number of results
            min_confidence: Minimum confidence
            synthesize_context: Generate summary
            filters: MongoDB-style filters

        Returns:
            Query results with optional context
        """
        cmd = [
            'query',
            '--query', query,
            '--k', str(k),
            '--min-confidence', str(min_confidence),
            '--format', 'json'
        ]

        if domain:
            cmd.extend(['--domain', domain])

        if synthesize_context:
            cmd.append('--synthesize-context')

        if filters:
            cmd.extend(['--filters', filters])

        try:
            output = await self._run_command_async(cmd)
            return json.loads(output) if output.strip() else {}
        except Exception as e:
            logger.error(f"Failed to query: {e}")
            return {}

    # === SYNC OPERATIONS ===

    async def sync_push(
        self,
        server: str,
        incremental: bool = True,
        filter_pattern: Optional[str] = None
    ) -> bool:
        """Push local changes to remote server"""
        cmd = [
            'sync', 'push',
            '--server', server
        ]

        if incremental:
            cmd.append('--incremental')

        if filter_pattern:
            cmd.extend(['--filter', filter_pattern])

        try:
            await self._run_command_async(cmd)
            logger.info(f"Synced changes to {server}")
            return True
        except Exception as e:
            logger.error(f"Failed to push sync: {e}")
            return False

    async def sync_pull(
        self,
        server: str,
        incremental: bool = True,
        filter_pattern: Optional[str] = None
    ) -> bool:
        """Pull remote changes from server"""
        cmd = [
            'sync', 'pull',
            '--server', server
        ]

        if incremental:
            cmd.append('--incremental')

        if filter_pattern:
            cmd.extend(['--filter', filter_pattern])

        try:
            await self._run_command_async(cmd)
            logger.info(f"Pulled changes from {server}")
            return True
        except Exception as e:
            logger.error(f"Failed to pull sync: {e}")
            return False

    # === UTILITY OPERATIONS ===

    async def get_stats(self) -> Dict:
        """Get database statistics"""
        try:
            result = self._run_command(['stats', str(self.db_path)])
            output = result.stdout

            # Parse output into structured data
            stats = {}
            for line in output.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    stats[key.strip()] = value.strip()

            return stats
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {}

    async def export_database(
        self,
        output_file: str,
        compress: bool = False
    ) -> bool:
        """Export database to JSON"""
        cmd = ['export', str(self.db_path), output_file]

        if compress:
            cmd.append('--compress')

        try:
            await self._run_command_async(cmd)
            logger.info(f"Exported database to {output_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to export: {e}")
            return False

    async def import_database(
        self,
        input_file: str,
        decompress: bool = False
    ) -> bool:
        """Import database from JSON"""
        cmd = ['import', input_file, str(self.db_path)]

        if decompress:
            cmd.append('--decompress')

        try:
            await self._run_command_async(cmd)
            logger.info(f"Imported database from {input_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to import: {e}")
            return False

    def __str__(self):
        return f"AgentDBClient(db_path={self.db_path})"

    def __repr__(self):
        return self.__str__()
