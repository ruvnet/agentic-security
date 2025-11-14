# Agentic Security v2.0 - AgentDB Integration Guide

## Table of Contents
1. [Overview](#overview)
2. [Installation & Setup](#installation--setup)
3. [Core Integration Patterns](#core-integration-patterns)
4. [Implementation Guide](#implementation-guide)
5. [Development Optimization](#development-optimization)
6. [Best Practices](#best-practices)

---

## Overview

### What is AgentDB?

AgentDB (v1.6.1) is a **frontier memory system** for AI agents, providing:

**Core Capabilities**:
1. **Vector Search**: Semantic similarity matching
2. **Reflexion**: Episode storage with self-critique
3. **Skill Library**: Reusable code patterns
4. **Causal Reasoning**: Understand what actions work
5. **Multi-Agent Sync**: QUIC-based coordination
6. **Pattern Learning**: Automatic discovery

### Why AgentDB for Agentic Security?

Transform from **stateless scanning** to **learning security intelligence**:

```
v1.0: Scan → Results → Forget
v2.0: Scan → Learn → Remember → Improve → Share
```

**Benefits**:
- 📚 **Persistent Memory**: Never forget a security lesson
- 🎯 **Pattern Recognition**: Auto-discover vulnerabilities
- 🛠️ **Skill Building**: Reusable fix templates
- 📊 **Causal Analysis**: Know what fixes work
- 🤝 **Team Coordination**: Share knowledge in real-time

---

## Installation & Setup

### 1. Install AgentDB CLI

```bash
# AgentDB is installed via npx (no global install needed)
npx agentdb --version  # Should show 1.6.1
```

### 2. Initialize Database

```bash
# Initialize AgentDB for Agentic Security
cd /home/user/agentic-security

# Create database with optimal settings
npx agentdb init ./agentdb.db \
  --dimension 1536 \
  --preset medium

# Verify initialization
npx agentdb stats ./agentdb.db
```

**Output**:
```
Database Statistics:
  Total Vectors: 0
  Total Episodes: 0
  Total Skills: 0
  Causal Edges: 0
  Database Size: 128 KB
  Index Type: HNSW
  Dimension: 1536
```

### 3. Python Wrapper

Create `src/agentic_security/agentdb_client.py`:

```python
"""
AgentDB Python client wrapper
"""

import subprocess
import json
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path


@dataclass
class Episode:
    """Reflexion episode"""
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


@dataclass
class Skill:
    """Reusable skill"""
    name: str
    description: str
    code: Optional[str] = None
    metadata: Optional[Dict] = None


@dataclass
class CausalEdge:
    """Causal relationship"""
    cause: str
    effect: str
    uplift: float
    confidence: float
    sample_size: int


class AgentDBClient:
    """
    Python client for AgentDB operations
    """

    def __init__(self, db_path: str = "./agentdb.db"):
        self.db_path = Path(db_path)
        self.ensure_initialized()

    def ensure_initialized(self):
        """Ensure database exists"""
        if not self.db_path.exists():
            self._run_command([
                'init', str(self.db_path),
                '--dimension', '1536',
                '--preset', 'medium'
            ])

    def _run_command(self, args: List[str],
                     capture_output: bool = True) -> subprocess.CompletedProcess:
        """Run agentdb command"""
        cmd = ['npx', 'agentdb'] + args
        return subprocess.run(
            cmd,
            capture_output=capture_output,
            text=True,
            check=True
        )

    # === REFLEXION OPERATIONS ===

    async def store_episode(self, episode: Episode) -> bool:
        """
        Store a reflexion episode

        Args:
            episode: Episode to store

        Returns:
            Success boolean
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
            self._run_command(cmd)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to store episode: {e}")
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
        """
        cmd = [
            'reflexion', 'retrieve',
            task,
            '--k', str(k)
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

        result = self._run_command(cmd)

        # Parse JSON output
        return json.loads(result.stdout)

    async def critique_summary(
        self,
        task: str,
        only_failures: bool = False
    ) -> Dict:
        """Get aggregated critique lessons"""
        cmd = ['reflexion', 'critique-summary', task]

        if only_failures:
            cmd.append('true')

        result = self._run_command(cmd)
        return json.loads(result.stdout)

    # === SKILL OPERATIONS ===

    async def create_skill(self, skill: Skill) -> bool:
        """
        Create a reusable skill

        Args:
            skill: Skill to create

        Returns:
            Success boolean
        """
        cmd = [
            'skill', 'create',
            skill.name,
            skill.description
        ]

        if skill.code:
            cmd.append(skill.code)

        try:
            self._run_command(cmd)
            return True
        except subprocess.CalledProcessError:
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
        """
        cmd = ['skill', 'search', query, str(k)]

        result = self._run_command(cmd)
        return json.loads(result.stdout)

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
        """
        cmd = [
            'skill', 'consolidate',
            str(min_attempts),
            str(min_reward),
            str(time_window_days)
        ]

        if extract_patterns:
            cmd.append('true')

        result = self._run_command(cmd)
        return json.loads(result.stdout)

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
            self._run_command(cmd)
            return True
        except subprocess.CalledProcessError:
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

        result = self._run_command(cmd)
        return json.loads(result.stdout)

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

        result = self._run_command(cmd)
        return json.loads(result.stdout)

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

        result = self._run_command(cmd)
        return json.loads(result.stdout)

    # === SYNC OPERATIONS ===

    async def start_sync_server(
        self,
        port: int = 4433,
        auth_token: Optional[str] = None
    ) -> Dict:
        """Start QUIC sync server"""
        cmd = [
            'sync', 'start-server',
            '--port', str(port)
        ]

        if auth_token:
            cmd.extend(['--auth-token', auth_token])

        result = self._run_command(cmd)

        # Extract auth token from output if generated
        output = result.stdout
        # Parse output for token and connection info

        return {
            'port': port,
            'status': 'running',
            'auth_token': auth_token,
            'output': output
        }

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
            self._run_command(cmd)
            return True
        except subprocess.CalledProcessError:
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
            self._run_command(cmd)
            return True
        except subprocess.CalledProcessError:
            return False

    # === UTILITY OPERATIONS ===

    async def get_stats(self) -> Dict:
        """Get database statistics"""
        result = self._run_command(['stats', str(self.db_path)])

        # Parse output into structured data
        stats = {}
        for line in result.stdout.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                stats[key.strip()] = value.strip()

        return stats

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
            self._run_command(cmd)
            return True
        except subprocess.CalledProcessError:
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
            self._run_command(cmd)
            return True
        except subprocess.CalledProcessError:
            return False
```

---

## Core Integration Patterns

### Pattern 1: Scan with Memory

```python
"""
Context-aware security scanning
"""

from agentic_security.agentdb_client import AgentDBClient, Episode


async def scan_with_memory(target: str, agentdb: AgentDBClient):
    """Scan with historical context"""

    # 1. Query past experiences
    past_scans = await agentdb.retrieve_episodes(
        task=f"scan:{target}",
        k=10,
        only_successes=True,
        synthesize_context=True
    )

    console.print(f"""
[cyan]📚 Found {len(past_scans.get('episodes', []))} relevant past scans[/cyan]

Context Summary:
{past_scans.get('synthesized_context', 'No context available')}
    """)

    # 2. Execute scan with context
    scan_results = await traditional_scan(
        target=target,
        context=past_scans
    )

    # 3. Calculate reward
    reward = calculate_scan_reward(scan_results)

    # 4. Store episode
    episode = Episode(
        session_id=generate_session_id(),
        task=f"scan:{target}",
        reward=reward,
        success=scan_results['success'],
        critique=generate_self_critique(scan_results),
        metadata={
            'vulnerabilities_found': len(scan_results['vulnerabilities']),
            'false_positives': scan_results['false_positives'],
            'scan_duration': scan_results['duration'],
            'target_type': scan_results['type']
        }
    )

    await agentdb.store_episode(episode)

    console.print(f"[green]✓[/green] Stored episode (reward: {reward:.2f})")

    return scan_results


def calculate_scan_reward(results: Dict) -> float:
    """Calculate reward score for scan"""
    # Factors:
    # + Vulnerabilities found (true positives)
    # - False positives
    # + Fix success rate
    # - Time taken

    true_positives = results['vulnerabilities_confirmed']
    false_positives = results['false_positives']
    fix_rate = results.get('fix_success_rate', 0.0)
    duration_penalty = min(results['duration'] / 300, 1.0)  # Normalize to 5 min

    reward = (
        (true_positives * 0.3) -
        (false_positives * 0.2) +
        (fix_rate * 0.4) -
        (duration_penalty * 0.1)
    )

    return max(0.0, min(1.0, reward))
```

### Pattern 2: Skill-Based Fixes

```python
"""
Apply learned skills to fix vulnerabilities
"""

async def fix_with_skills(vulnerability: Dict, agentdb: AgentDBClient):
    """Fix vulnerability using skill library"""

    # 1. Search for applicable skills
    skills = await agentdb.search_skills(
        query=vulnerability['type'],
        k=5
    )

    if not skills:
        console.print("[yellow]No skills found, using AI generation[/yellow]")
        return await traditional_fix(vulnerability)

    # 2. Display skills
    console.print("\n[bold]Found applicable skills:[/bold]")
    for i, skill in enumerate(skills):
        console.print(f"""
{i+1}. {skill['name']}
   {skill['description']}
   Success Rate: {skill.get('success_rate', 'Unknown')}
   Times Used: {skill.get('usage_count', 0)}
        """)

    # 3. Apply best skill
    best_skill = skills[0]
    console.print(f"\n[cyan]Applying skill: {best_skill['name']}[/cyan]")

    result = await apply_skill_with_aider(
        skill=best_skill,
        vulnerability=vulnerability
    )

    # 4. Record outcome
    await record_skill_usage(
        agentdb=agentdb,
        skill=best_skill,
        result=result
    )

    return result


async def record_skill_usage(agentdb: AgentDBClient,
                             skill: Dict,
                             result: Dict):
    """Record skill usage for learning"""

    # Store as episode
    episode = Episode(
        session_id=generate_session_id(),
        task=f"apply_skill:{skill['name']}",
        reward=1.0 if result['success'] else 0.0,
        success=result['success'],
        critique=result.get('feedback'),
        metadata={
            'skill_id': skill['id'],
            'skill_name': skill['name'],
            'vulnerability_type': result['vulnerability_type'],
            'fix_validated': result.get('validated', False)
        }
    )

    await agentdb.store_episode(episode)

    # Update causal edge
    if result['success']:
        await agentdb.add_causal_edge(CausalEdge(
            cause=f"skill:{skill['name']}",
            effect="vulnerability_fixed",
            uplift=0.8,
            confidence=0.9,
            sample_size=1
        ))
```

### Pattern 3: Pattern Learning

```python
"""
Automatic pattern discovery from scan history
"""

async def learn_patterns(agentdb: AgentDBClient):
    """Discover vulnerability patterns automatically"""

    console.print("[cyan]🔬 Analyzing scan history for patterns...[/cyan]")

    # 1. Discover causal patterns
    patterns = await agentdb.discover_patterns(
        min_attempts=3,
        min_success_rate=0.6,
        min_confidence=0.7,
        dry_run=False
    )

    console.print(f"\n[green]✓[/green] Discovered {len(patterns)} patterns")

    # 2. Display patterns
    for pattern in patterns:
        console.print(f"""
Pattern: {pattern['cause']} → {pattern['effect']}
  Confidence: {pattern['confidence']:.1%}
  Uplift: {pattern['uplift']:.2f}
  Sample Size: {pattern['sample_size']}
        """)

    # 3. Consolidate into skills
    console.print("\n[cyan]Building skills from patterns...[/cyan]")

    skills_created = await agentdb.consolidate_skills(
        min_attempts=3,
        min_reward=0.7,
        time_window_days=7,
        extract_patterns=True
    )

    console.print(f"[green]✓[/green] Created {len(skills_created)} new skills")

    return {
        'patterns': patterns,
        'skills': skills_created
    }
```

---

## Development Optimization

### Using AgentDB During Development

#### 1. Track Development Sessions

```python
"""
Track development progress with AgentDB
"""

async def track_development_session(task: str, agentdb: AgentDBClient):
    """Wrapper to track any development task"""
    session_id = generate_session_id()
    start_time = datetime.now()

    try:
        # Execute task
        result = await execute_task(task)

        # Calculate metrics
        duration = (datetime.now() - start_time).total_seconds() * 1000
        success = result['success']
        reward = calculate_reward(result)

        # Store episode
        await agentdb.store_episode(Episode(
            session_id=session_id,
            task=task,
            reward=reward,
            success=success,
            critique=generate_critique(result),
            latency_ms=int(duration),
            metadata=result.get('metadata', {})
        ))

        return result

    except Exception as e:
        # Store failure
        duration = (datetime.now() - start_time).total_seconds() * 1000

        await agentdb.store_episode(Episode(
            session_id=session_id,
            task=task,
            reward=0.0,
            success=False,
            critique=f"Failed: {str(e)}",
            latency_ms=int(duration),
            metadata={'error': str(e)}
        ))

        raise
```

#### 2. Learn from Past Development

```bash
# Query past development experiences
npx agentdb query \
  --query "implementing authentication" \
  --k 10 \
  --synthesize-context

# Learn from failures
npx agentdb reflexion retrieve "bug fix" \
  --only-failures \
  --k 10 \
  --synthesize-context

# Find effective approaches
npx agentdb causal query \
  --min-confidence 0.8 \
  --min-uplift 0.1
```

#### 3. Build Development Skills

```bash
# Consolidate successful patterns into skills
npx agentdb skill consolidate 3 0.7 7 true

# Search for reusable patterns
npx agentdb skill search "authentication implementation"

# List all skills
npx agentdb skill search "" 100
```

---

## Best Practices

### 1. Reward Design

Design reward functions that capture what matters:

```python
def calculate_comprehensive_reward(results: Dict) -> float:
    """Multi-factor reward calculation"""

    factors = {
        # Effectiveness (50%)
        'true_positives': results['true_positives'] * 0.3,
        'fix_success': results['fix_success_rate'] * 0.2,

        # Efficiency (25%)
        'time_score': (1.0 - min(results['duration'] / 600, 1.0)) * 0.15,
        'resource_score': (1.0 - results['resource_usage']) * 0.10,

        # Quality (25%)
        'false_positive_penalty': -results['false_positives'] * 0.15,
        'severity_score': results['critical_found'] * 0.10,
    }

    total = sum(factors.values())
    return max(0.0, min(1.0, total))
```

### 2. Critique Generation

Self-critique helps learning:

```python
async def generate_self_critique(results: Dict) -> str:
    """Generate learning-oriented critique"""

    critiques = []

    # What went well
    if results['success']:
        critiques.append(f"✓ Successfully found {results['vulns']} vulnerabilities")

    # What could improve
    if results['false_positives'] > 0:
        critiques.append(f"⚠ {results['false_positives']} false positives - review detection patterns")

    if results['duration'] > 300:
        critiques.append("⚠ Scan took >5 minutes - consider optimization")

    # Lessons learned
    if results['novel_patterns']:
        critiques.append(f"💡 Discovered {len(results['novel_patterns'])} new patterns")

    return "\n".join(critiques)
```

### 3. Metadata Organization

Consistent metadata enables better querying:

```python
def standardize_metadata(scan_results: Dict) -> Dict:
    """Standardize metadata structure"""

    return {
        # Categorization
        'category': 'security_scan',
        'subcategory': scan_results['scan_type'],

        # Metrics
        'metrics': {
            'duration_ms': scan_results['duration'],
            'files_scanned': scan_results['file_count'],
            'lines_scanned': scan_results['line_count'],
        },

        # Results
        'results': {
            'vulnerabilities_found': len(scan_results['vulnerabilities']),
            'critical': scan_results['critical_count'],
            'high': scan_results['high_count'],
            'medium': scan_results['medium_count'],
            'low': scan_results['low_count'],
        },

        # Context
        'target': scan_results['target'],
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0',
    }
```

### 4. Regular Maintenance

```bash
# Weekly: Consolidate skills
npx agentdb skill consolidate 3 0.7 7 true

# Monthly: Discover patterns
npx agentdb learner run 3 0.6 0.7

# Monthly: Prune old data
npx agentdb reflexion prune 90 0.3
npx agentdb skill prune 5 0.4 90

# Quarterly: Export backup
npx agentdb export ./agentdb.db ./backups/agentdb-$(date +%Y%m%d).json.gz --compress
```

### 5. Team Sync Strategy

```python
async def team_sync_routine(agentdb: AgentDBClient):
    """Regular sync with team"""

    # Pull latest knowledge every hour
    await agentdb.sync_pull(
        server=SYNC_SERVER,
        incremental=True
    )

    # Push changes at end of day
    await agentdb.sync_push(
        server=SYNC_SERVER,
        incremental=True
    )

    # Full sync weekly
    if is_weekly_sync_time():
        await full_bidirectional_sync(agentdb)
```

---

## Performance Optimization

### 1. Batch Operations

```python
async def batch_store_episodes(episodes: List[Episode],
                                agentdb: AgentDBClient):
    """Store multiple episodes efficiently"""

    # Use asyncio for parallel execution
    tasks = [
        agentdb.store_episode(episode)
        for episode in episodes
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    successes = sum(1 for r in results if r is True)
    console.print(f"Stored {successes}/{len(episodes)} episodes")
```

### 2. Caching

```python
from functools import lru_cache

class CachedAgentDB:
    def __init__(self, agentdb: AgentDBClient):
        self.agentdb = agentdb
        self.cache = {}

    @lru_cache(maxsize=100)
    async def cached_search_skills(self, query: str, k: int = 5):
        """Cache skill searches"""
        cache_key = f"{query}:{k}"

        if cache_key in self.cache:
            return self.cache[cache_key]

        result = await self.agentdb.search_skills(query, k)
        self.cache[cache_key] = result

        return result
```

---

**Next Document**: [Development Roadmap](06-development-roadmap.md)
