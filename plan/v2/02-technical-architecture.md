# Agentic Security v2.0 - Technical Architecture

## Table of Contents
1. [System Overview](#system-overview)
2. [Core Components](#core-components)
3. [Data Flow](#data-flow)
4. [Integration Architecture](#integration-architecture)
5. [Deployment Models](#deployment-models)
6. [Scalability & Performance](#scalability--performance)
7. [Security Architecture](#security-architecture)

---

## System Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Agentic Security v2.0                       │
│                   AI-Native Security Platform                   │
└─────────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┴───────────────┐
                │                               │
┌───────────────▼──────────────┐   ┌───────────▼─────────────┐
│   User Interaction Layer     │   │  External Integrations  │
├──────────────────────────────┤   ├─────────────────────────┤
│  • Cyberpunk CLI             │   │  • GitHub/GitLab        │
│  • Streamlit Web GUI         │   │  • CI/CD Pipelines      │
│  • REST API Server           │   │  • Slack/Discord        │
│  • MCP Interface             │   │  • IDE Extensions       │
└──────────────┬───────────────┘   └───────────┬─────────────┘
               │                               │
               └───────────────┬───────────────┘
                               │
┌──────────────────────────────▼────────────────────────────────┐
│                   Core Orchestration Layer                     │
├────────────────────────────────────────────────────────────────┤
│  • Security Pipeline Orchestrator                              │
│  • AI Model Router (GPT-4, Claude-3.5, Gemini, Local)        │
│  • Task Queue Manager                                          │
│  • Event Bus (Pub/Sub)                                        │
└──────────────────────────────┬────────────────────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
┌─────────▼──────────┐  ┌──────▼────────┐  ┌──────▼─────────┐
│  Security Engines  │  │  AI Systems   │  │ Memory Systems │
├────────────────────┤  ├───────────────┤  ├────────────────┤
│ • OWASP ZAP        │  │ • AIDefence   │  │ • AgentDB      │
│ • Nuclei           │  │ • Aider       │  │ • Vector Store │
│ • Dependency-Check │  │ • LangChain   │  │ • Skill Lib    │
│ • Pattern Matcher  │  │ • Prompt Mgr  │  │ • Episode DB   │
│ • Code Analyzer    │  │ • Output Val  │  │ • Causal Graph │
└────────────────────┘  └───────────────┘  └────────────────┘
          │                    │                    │
          └────────────────────┼────────────────────┘
                               │
┌──────────────────────────────▼────────────────────────────────┐
│                      Data & Storage Layer                      │
├────────────────────────────────────────────────────────────────┤
│  • SQLite (AgentDB Vectors, Episodes, Skills)                 │
│  • Redis (Caching, Rate Limiting)                             │
│  • File System (Reports, Backups, Logs)                       │
│  • S3/Object Storage (Optional Cloud Sync)                    │
└────────────────────────────────────────────────────────────────┘
                               │
┌──────────────────────────────▼────────────────────────────────┐
│                   Multi-Agent Coordination                     │
├────────────────────────────────────────────────────────────────┤
│  • QUIC Sync Server (UDP-based, TLS 1.3 encrypted)           │
│  • Agent Discovery (mDNS/DNS-SD)                              │
│  • Distributed Lock Manager                                    │
│  • State Synchronization                                       │
└────────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. User Interaction Layer

#### 1.1 Enhanced CLI (`security_cli.py`)
```python
class SecurityCLI:
    """
    v2.0 Enhancements:
    - AgentDB query integration
    - Real-time learning feedback
    - Skill recommendation system
    - Interactive reflexion mode
    """

    # New Commands for v2.0
    commands = {
        'analyze': 'Scan with learning enabled',
        'fix': 'Apply fixes using skill library',
        'learn': 'Query AgentDB for patterns',
        'sync': 'Synchronize with team agents',
        'protect': 'Enable AIDefence protection',
        'reflect': 'Review and learn from episodes',
        'consolidate': 'Build skills from episodes',
    }
```

**New Features**:
- `agentic-security learn "SQL injection"` - Query past experiences
- `agentic-security sync start` - Start multi-agent coordination
- `agentic-security protect --server http://localhost:3000` - Enable AIDefence
- `agentic-security reflect --task "authentication"` - Review past security fixes

#### 1.2 Web GUI (`gui/app.py`)
```python
# New v2.0 Pages
streamlit_pages = {
    'Dashboard': 'Overview with learning metrics',
    'Scan': 'Traditional security scanning',
    'Memory': 'AgentDB episode browser',
    'Skills': 'Skill library management',
    'Patterns': 'Discovered vulnerability patterns',
    'Agents': 'Multi-agent coordination',
    'AI Protection': 'AIDefence monitoring',
}
```

#### 1.3 REST API Server (New)
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Agentic Security API v2.0")

# Core endpoints
@app.post("/api/v2/scan")
async def scan_with_learning(config: ScanConfig):
    """Scan with AgentDB integration"""
    pass

@app.get("/api/v2/memory/query")
async def query_memory(query: str, k: int = 5):
    """Query AgentDB for relevant episodes"""
    pass

@app.post("/api/v2/skills/consolidate")
async def consolidate_skills():
    """Trigger skill consolidation"""
    pass

@app.get("/api/v2/patterns/discovered")
async def get_patterns():
    """Get automatically discovered patterns"""
    pass
```

### 2. Core Orchestration Layer

#### 2.1 Enhanced Security Pipeline
```python
class SecurityPipelineV2:
    """
    v2.0 Enhancements:
    - AgentDB integration for memory
    - AIDefence for AI security
    - Learning from every scan
    - Skill-based fix application
    """

    def __init__(self):
        self.agentdb = AgentDBClient()
        self.aidefence = AIDefenceClient()
        self.skill_library = SkillLibrary()
        self.pattern_learner = PatternLearner()

    async def scan_with_learning(self, target):
        """Enhanced scanning with learning"""
        # 1. Query past experiences
        past_episodes = await self.agentdb.query_similar(target)

        # 2. Apply learned skills
        relevant_skills = self.skill_library.search(target)

        # 3. Traditional scanning
        scan_results = await self.traditional_scan(target)

        # 4. AI-enhanced analysis with protection
        protected_analysis = await self.ai_analyze_protected(
            scan_results,
            past_context=past_episodes
        )

        # 5. Store episode for learning
        await self.store_episode(
            task=f"scan:{target}",
            results=protected_analysis,
            success=True,
            metadata={'skills_used': relevant_skills}
        )

        # 6. Trigger pattern learning
        await self.pattern_learner.learn_from_scan(scan_results)

        return protected_analysis
```

#### 2.2 AI Model Router
```python
class AIModelRouter:
    """
    Intelligent routing to best model for task
    """

    models = {
        'strategic_analysis': 'gpt-4-turbo-preview',
        'code_review': 'claude-3-5-sonnet-20241022',
        'deep_audit': 'claude-3-opus-20240229',
        'pattern_recognition': 'gemini-pro',
        'quick_scan': 'gpt-3.5-turbo',
        'local_privacy': 'codellama-34b',
    }

    async def route_task(self, task_type: str, content: str):
        """Route to appropriate model"""
        model = self.models.get(task_type)

        # AIDefence protection
        if await self.aidefence.detect(content):
            raise PromptInjectionError("Threat detected in input")

        response = await self.call_model(model, content)

        # Validate output
        if await self.aidefence.analyze(response):
            raise OutputValidationError("Threat detected in output")

        return response
```

### 3. Memory Systems

#### 3.1 AgentDB Integration
```python
class AgentDBMemory:
    """
    Central memory system for learning
    """

    def __init__(self, db_path="./agentdb.db"):
        self.db_path = db_path
        self.init_database()

    async def store_episode(self, session_id, task, reward,
                           success, critique, metadata):
        """Store security scanning episode"""
        await self.reflexion_store(
            session_id=session_id,
            task=task,
            reward=reward,
            success=success,
            critique=critique,
            metadata={
                **metadata,
                'timestamp': datetime.now(),
                'version': '2.0',
            }
        )

    async def query_similar(self, query, k=5,
                           synthesize=True):
        """Query for similar past experiences"""
        results = await self.reflexion_retrieve(
            task=query,
            k=k,
            synthesize_context=synthesize,
            filters={'success': True, 'reward': {'$gte': 0.7}}
        )
        return results

    async def consolidate_skills(self, min_attempts=3,
                                 min_reward=0.7):
        """Auto-create skills from successful patterns"""
        await self.skill_consolidate(
            min_attempts=min_attempts,
            min_reward=min_reward,
            time_window_days=7,
            extract_patterns=True
        )
```

#### 3.2 Skill Library
```python
class SkillLibrary:
    """
    Reusable security fix patterns
    """

    def __init__(self, agentdb: AgentDBMemory):
        self.agentdb = agentdb
        self.cache = {}

    async def create_skill(self, name, description, code,
                          metadata):
        """Create a new security skill"""
        await self.agentdb.skill_create(
            name=name,
            description=description,
            code=code,
            metadata={
                **metadata,
                'created_at': datetime.now(),
                'category': 'security',
            }
        )

    async def search_applicable(self, vulnerability_type, k=5):
        """Find applicable skills for vulnerability"""
        skills = await self.agentdb.skill_search(
            query=vulnerability_type,
            k=k
        )
        return skills

    async def apply_skill(self, skill, target_file):
        """Apply skill to fix vulnerability"""
        # Use Aider to apply the skill
        result = await self.aider.apply_fix(
            file=target_file,
            template=skill['code'],
            metadata=skill['metadata']
        )

        # Update skill statistics
        await self.update_skill_stats(skill['name'], result)

        return result
```

### 4. AI Security Layer

#### 4.1 AIDefence Integration
```python
class AIDefenceProtection:
    """
    Protect all AI interactions from manipulation
    """

    def __init__(self, gateway_url="http://localhost:3000"):
        self.gateway_url = gateway_url
        self.server_process = None

    async def start_gateway(self, port=3000):
        """Start AIMDS Gateway server"""
        self.server_process = subprocess.Popen([
            'aidefence', 'server',
            '--port', str(port),
            '--host', '0.0.0.0'
        ])

    async def detect(self, text: str) -> bool:
        """Detect prompt injection attempts"""
        response = await requests.post(
            f"{self.gateway_url}/detect",
            json={'text': text}
        )
        return response.json()['is_threat']

    async def analyze_deep(self, text: str):
        """Deep analysis with behavioral verification"""
        response = await requests.post(
            f"{self.gateway_url}/analyze",
            json={'text': text, 'deep': True}
        )
        return response.json()

    async def protect_pipeline(self):
        """Add protection to all AI calls"""
        # Intercept all LLM calls
        for model in self.ai_models:
            model.add_middleware(self.validate_input)
            model.add_postprocessing(self.validate_output)
```

### 5. Multi-Agent Coordination

#### 5.1 QUIC Sync Server
```python
class MultiAgentCoordinator:
    """
    Coordinate multiple security agents
    """

    def __init__(self):
        self.server_process = None
        self.connected_agents = {}

    async def start_server(self, port=4433):
        """Start QUIC synchronization server"""
        # Generate auth token
        auth_token = secrets.token_urlsafe(32)

        # Start server
        cmd = [
            'agentdb', 'sync', 'start-server',
            '--port', str(port),
            '--auth-token', auth_token
        ]
        self.server_process = subprocess.Popen(cmd)

        return {
            'port': port,
            'auth_token': auth_token,
            'status': 'running'
        }

    async def connect_agent(self, host, port, auth_token):
        """Connect to remote sync server"""
        cmd = [
            'agentdb', 'sync', 'connect',
            host, str(port),
            '--auth-token', auth_token
        ]
        result = subprocess.run(cmd, capture_output=True)
        return result.returncode == 0

    async def sync_push(self, server, incremental=True):
        """Push local changes to server"""
        cmd = [
            'agentdb', 'sync', 'push',
            '--server', server,
        ]
        if incremental:
            cmd.append('--incremental')

        result = subprocess.run(cmd, capture_output=True)
        return result.returncode == 0

    async def sync_pull(self, server, incremental=True):
        """Pull remote changes from server"""
        cmd = [
            'agentdb', 'sync', 'pull',
            '--server', server,
        ]
        if incremental:
            cmd.append('--incremental')

        result = subprocess.run(cmd, capture_output=True)
        return result.returncode == 0
```

---

## Data Flow

### Scan with Learning Flow

```
User Request
    │
    ├─→ [1] Query AgentDB for Past Experiences
    │       │
    │       ├─→ Vector similarity search
    │       ├─→ Episode retrieval with context synthesis
    │       └─→ Skill library search
    │
    ├─→ [2] Execute Security Scan
    │       │
    │       ├─→ OWASP ZAP (Web scanning)
    │       ├─→ Nuclei (Template-based)
    │       ├─→ Dependency-Check (Packages)
    │       └─→ Pattern Matcher (Code analysis)
    │
    ├─→ [3] AI Analysis (Protected)
    │       │
    │       ├─→ AIDefence input validation
    │       ├─→ Route to appropriate model
    │       │   • GPT-4: Strategic analysis
    │       │   • Claude-3.5: Code review
    │       │   • Gemini: Pattern recognition
    │       ├─→ Context from past experiences
    │       └─→ AIDefence output validation
    │
    ├─→ [4] Generate Fixes (Skill-Based)
    │       │
    │       ├─→ Search skill library
    │       ├─→ Apply relevant skills with Aider
    │       ├─→ Validate fixes
    │       └─→ Generate PR with context
    │
    ├─→ [5] Store Learning Episode
    │       │
    │       ├─→ Store in AgentDB
    │       ├─→ Update skill statistics
    │       ├─→ Add causal edge (fix → result)
    │       └─→ Trigger pattern learning
    │
    └─→ [6] Synchronize (Multi-Agent)
            │
            ├─→ Push changes to QUIC server
            ├─→ Share discovered patterns
            └─→ Update team knowledge base

Result to User (with learning insights)
```

---

## Integration Architecture

### AIDefence Integration Points

```python
# Integration in security_pipeline.py

class SecurityPipelineV2:
    def __init__(self):
        # Initialize AIDefence
        self.aidefence = AIDefenceProtection()

    async def ai_analyze_protected(self, scan_results,
                                   past_context):
        """Protected AI analysis"""

        # 1. Build prompt with context
        prompt = self.build_analysis_prompt(
            results=scan_results,
            context=past_context
        )

        # 2. Validate input for prompt injection
        threat_detected = await self.aidefence.detect(prompt)
        if threat_detected:
            logger.warning("Prompt injection detected, sanitizing")
            prompt = self.sanitize_prompt(prompt)

        # 3. Call AI model
        response = await self.ai_model.analyze(prompt)

        # 4. Validate output
        output_threat = await self.aidefence.analyze_deep(response)
        if output_threat['is_threat']:
            logger.error("Threat in AI output, rejecting")
            raise AISecurityError("Unsafe AI output detected")

        return response
```

### AgentDB Integration Points

```python
# Integration throughout the application

# In security_cli.py
@click.command()
@click.option('--learn', is_flag=True, help='Enable learning mode')
async def analyze(path, learn):
    if learn:
        # Query past experiences
        episodes = await agentdb.query_similar(
            query=f"scan:{path}",
            k=5,
            synthesize=True
        )
        console.print(f"Found {len(episodes)} relevant past scans")

    # Execute scan
    results = await pipeline.scan(path, context=episodes)

    if learn:
        # Store episode
        await agentdb.store_episode(
            session_id=session_id,
            task=f"scan:{path}",
            reward=calculate_reward(results),
            success=results['success'],
            critique=results.get('lessons'),
            metadata=results['metadata']
        )

# In fix_cycle.py
async def apply_fix_with_skills(vulnerability):
    # Search for applicable skills
    skills = await agentdb.skill_search(
        query=vulnerability['type'],
        k=5
    )

    if skills:
        # Apply best skill
        result = await apply_skill(skills[0], vulnerability)

        # Update skill stats
        await agentdb.update_skill_success(
            skill_id=skills[0]['id'],
            success=result['success']
        )
    else:
        # Traditional fix
        result = await traditional_fix(vulnerability)

        # Consider creating new skill
        if result['success']:
            await agentdb.skill_create(
                name=f"fix_{vulnerability['type']}",
                description=result['description'],
                code=result['code']
            )
```

---

## Deployment Models

### 1. Single Developer (Local)
```yaml
deployment: local
components:
  - security_cli
  - agentdb (SQLite)
  - aidefence (local server)
  - ai_models (API-based)
features:
  - Local learning
  - No network dependencies
  - Fast iterations
```

### 2. Team Collaboration
```yaml
deployment: distributed
components:
  - multiple agents (developers)
  - quic_sync_server (central)
  - shared agentdb
  - aidefence gateway
features:
  - Knowledge sharing
  - Distributed scanning
  - Team skill library
  - Real-time sync
```

### 3. Enterprise CI/CD
```yaml
deployment: cloud_native
components:
  - kubernetes pods
  - redis cluster
  - s3 storage
  - load balancer
features:
  - Auto-scaling
  - High availability
  - Audit logging
  - Compliance reports
```

### 4. Air-Gapped (Secure)
```yaml
deployment: isolated
components:
  - local_models (no API)
  - sqlite (no cloud)
  - isolated_network
features:
  - Complete privacy
  - No external dependencies
  - Regulatory compliance
  - Offline operation
```

---

## Scalability & Performance

### Performance Targets

| Metric | v1.0 | v2.0 Target |
|--------|------|-------------|
| Scan Time (1000 files) | 120s | 60s |
| Memory Query | N/A | <2s |
| Skill Search | N/A | <100ms |
| Agent Sync | N/A | <500ms |
| AI Response | 5-10s | 3-7s |
| Pattern Learning | N/A | <5s |

### Optimization Strategies

1. **Caching**
   ```python
   # Multi-level caching
   L1: In-memory (LRU cache)
   L2: Redis (distributed)
   L3: SQLite (persistent)
   L4: S3 (archival)
   ```

2. **Parallel Processing**
   ```python
   # Concurrent scans
   async with asyncio.TaskGroup() as group:
       tasks = [
           group.create_task(zap_scan(target)),
           group.create_task(nuclei_scan(target)),
           group.create_task(dependency_scan(target)),
       ]
   ```

3. **Incremental Sync**
   ```python
   # Only sync changes
   agentdb sync push --incremental
   agentdb sync pull --incremental
   ```

4. **Vector Search Optimization**
   ```python
   # Use appropriate presets
   agentdb init --preset large  # >100K vectors
   agentdb init --dimension 768  # Smaller dimensions
   ```

---

## Security Architecture

### Defense in Depth

```
┌─────────────────────────────────────────────┐
│  Layer 1: Input Validation                  │
│  • AIDefence prompt injection detection     │
│  • Schema validation                        │
│  • Rate limiting                            │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│  Layer 2: Authentication & Authorization    │
│  • JWT tokens                               │
│  • API keys                                 │
│  • RBAC (Role-Based Access Control)        │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│  Layer 3: Secure Processing                │
│  • Sandboxed code execution                │
│  • AI output validation                    │
│  • Resource limits                         │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│  Layer 4: Data Protection                   │
│  • Encryption at rest (AES-256)            │
│  • Encryption in transit (TLS 1.3)         │
│  • Secure key management                   │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│  Layer 5: Audit & Monitoring               │
│  • Complete audit logs                     │
│  • Anomaly detection                       │
│  • Security alerts                         │
└─────────────────────────────────────────────┘
```

### Threat Model

| Threat | Mitigation |
|--------|-----------|
| **Prompt Injection** | AIDefence detection + validation |
| **Code Injection** | Sandboxed execution + output validation |
| **Data Exfiltration** | Encrypted storage + access controls |
| **MitM Attacks** | TLS 1.3 + certificate pinning |
| **DoS** | Rate limiting + resource quotas |
| **Unauthorized Access** | JWT + RBAC + audit logs |

---

## Technology Stack

### Core Dependencies

```toml
[dependencies]
# AI & ML
openai = "^1.53.0"
anthropic = "^0.38.0"
aider-chat = "^0.61.0"

# Security
aidefence = "^2.1.0"  # NEW
defusedxml = "^0.7.1"
cryptography = "^41.0.0"
bcrypt = "^4.0.1"

# Memory & Data
agentdb = "^1.6.1"  # NEW
redis = "^5.0.0"  # NEW
sqlite3 = "built-in"

# API & Web
fastapi = "^0.104.0"  # NEW
streamlit = "^1.28.0"
click = "^8.1.7"

# Testing
pytest = "^7.4.3"
pytest-asyncio = "^0.21.0"
```

---

**Next Document**: [Feature Specifications](03-feature-specifications.md)
