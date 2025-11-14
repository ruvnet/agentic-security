# Agentic Security v2.0 - Quick Start Implementation Guide

## 🚀 Get Started in 15 Minutes

This guide gets you from zero to running Agentic Security v2.0 with full learning capabilities.

---

## Prerequisites

```bash
# Required
- Python 3.10+
- Node.js 18+
- npm 9+
- Git

# Optional
- Docker (for containerized deployment)
- Redis (for distributed caching)
```

---

## Installation

### Step 1: Clone and Setup

```bash
# Clone repository
git clone https://github.com/ruvnet/agentic-security.git
cd agentic-security

# Checkout v2.0 development branch
git checkout claude/agentic-security-v2-setup-018jLJo5kvcZdE8qfqdDHPDH

# Create Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
pip install -e .  # Install in editable mode

# Install Node.js dependencies
npm install

# Verify installations
agentic-security version
aidefence --version
npx agentdb --version
```

**Expected Output**:
```
agentic-security: 2.0.0
aidefence: 2.1.0
agentdb: 1.6.1
```

### Step 2: Initialize AgentDB

```bash
# Initialize database
npm run agentdb:init

# Verify initialization
npm run agentdb:stats
```

**Expected Output**:
```
Database Statistics:
  Total Vectors: 0
  Total Episodes: 0
  Total Skills: 0
  Database Size: 128 KB
```

### Step 3: Configure

Create `config.yml`:

```yaml
# Agentic Security v2.0 Configuration

# Security Settings
security:
  critical_threshold: 7.0
  max_fix_attempts: 3
  scan_targets:
    - type: code
      path: ./src

# AI Models
ai:
  models:
    architecture_review: gpt-4-turbo-preview
    code_review: claude-3-5-sonnet-20241022
    fix_implementation: claude-3-5-sonnet-20241022
    pattern_recognition: gpt-4-turbo-preview

  api_keys:
    openai: ${OPENAI_API_KEY}
    anthropic: ${ANTHROPIC_API_KEY}

# AgentDB Configuration
agentdb:
  enabled: true
  db_path: ./agentdb.db
  learning:
    min_reward: 0.7
    consolidate_interval: 86400  # Daily
    pattern_discovery: true

# AIDefence Configuration
aidefence:
  enabled: true
  gateway_url: http://localhost:3000
  port: 3000
  detection:
    deep_analysis: true
    confidence_threshold: 0.7
  actions:
    on_threat: sanitize  # sanitize | block | warn

# Multi-Agent Sync (Optional)
sync:
  enabled: false
  server: null  # Set when joining a team
  auto_sync: false

# Notifications
notifications:
  enabled: true
  channels:
    - type: console
```

Set environment variables:

```bash
# Create .env file
cat > .env << EOF
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
EOF

# Load environment
source .env
```

---

## First Run

### Test 1: Basic Scan (No Learning)

```bash
# Simple security scan
agentic-security analyze ./src

# With auto-fix
agentic-security analyze ./src --auto-fix
```

### Test 2: Scan with Learning

```bash
# Start AIDefence gateway
npm run aidefence:start &

# Scan with learning enabled
agentic-security analyze ./src --learn

# Check what was learned
npx agentdb stats ./agentdb.db
```

### Test 3: Query Learned Knowledge

```bash
# Query past experiences
agentic-security learn "SQL injection"

# View critique summary
npx agentdb reflexion critique-summary "security scan"
```

---

## Development Workflow

### Daily Development Loop

```bash
# Morning: Pull team knowledge
agentic-security sync pull

# Work: Scan with learning
agentic-security analyze ./src --learn --auto-fix

# Review: Check learned patterns
agentic-security patterns list

# Evening: Share knowledge
agentic-security sync push
```

### Weekly Optimization

```bash
# Consolidate skills
npm run agentdb:consolidate

# Discover patterns
npm run agentdb:learn

# Backup database
npm run agentdb:export
```

---

## Example Use Cases

### Use Case 1: Context-Aware Scanning

```python
"""
Scan with historical context
"""

from agentic_security.v2 import SecurityPipelineV2
from agentic_security.agentdb_client import AgentDBClient

async def main():
    # Initialize
    agentdb = AgentDBClient("./agentdb.db")
    pipeline = SecurityPipelineV2(config_path="config.yml")

    # Scan with learning
    results = await pipeline.scan_with_learning(
        target="./src",
        use_history=True
    )

    print(f"Found {len(results['vulnerabilities'])} vulnerabilities")
    print(f"Applied {len(results['fixes'])} fixes")
    print(f"Learning reward: {results['reward']:.2f}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### Use Case 2: Skill-Based Fixing

```python
"""
Fix vulnerability using skill library
"""

from agentic_security.agentdb_client import AgentDBClient

async def fix_with_skill(vulnerability):
    agentdb = AgentDBClient()

    # Search for applicable skills
    skills = await agentdb.search_skills(
        query=vulnerability['type'],
        k=5
    )

    if skills:
        print(f"Found {len(skills)} applicable skills:")
        for skill in skills:
            print(f"  - {skill['name']}: {skill['description']}")

        # Apply best skill
        best_skill = skills[0]
        print(f"\nApplying: {best_skill['name']}")

        # Implementation would use Aider here
        return best_skill
    else:
        print("No skills found, will generate new fix")
        return None
```

### Use Case 3: Pattern Discovery

```python
"""
Discover vulnerability patterns automatically
"""

from agentic_security.agentdb_client import AgentDBClient

async def discover_patterns():
    agentdb = AgentDBClient()

    # Discover patterns from history
    patterns = await agentdb.discover_patterns(
        min_attempts=3,
        min_success_rate=0.6,
        min_confidence=0.7
    )

    print(f"Discovered {len(patterns)} patterns:")
    for pattern in patterns:
        print(f"""
Pattern: {pattern['cause']} → {pattern['effect']}
  Confidence: {pattern['confidence']:.1%}
  Sample Size: {pattern['sample_size']}
        """)

    # Consolidate into skills
    skills = await agentdb.consolidate_skills(
        min_attempts=3,
        min_reward=0.7,
        extract_patterns=True
    )

    print(f"\nCreated {len(skills)} new skills")
```

---

## CLI Reference

### Core Commands

```bash
# Scanning
agentic-security analyze [PATH] [OPTIONS]
  --learn              Enable learning mode
  --auto-fix          Auto-apply fixes
  --config FILE       Config file path
  --min-severity      Minimum severity to report

# Learning
agentic-security learn QUERY [OPTIONS]
  --k NUMBER          Number of results
  --synthesize        Generate context summary

# Memory Management
agentic-security memory stats
agentic-security memory query "SQL injection"
agentic-security memory consolidate

# AI Security
agentic-security protect start [OPTIONS]
agentic-security protect stop
agentic-security protect check TEXT
agentic-security protect stats

# Skills
agentic-security skills list
agentic-security skills search QUERY
agentic-security skills apply SKILL_NAME FILE

# Patterns
agentic-security patterns discover
agentic-security patterns list
agentic-security patterns apply PATTERN_ID

# Multi-Agent
agentic-security sync start [OPTIONS]
agentic-security sync connect HOST:PORT --token TOKEN
agentic-security sync push [--incremental]
agentic-security sync pull [--incremental]
agentic-security sync status

# Utilities
agentic-security version
agentic-security config validate
agentic-security doctor  # Check system health
```

---

## Testing

### Run Test Suite

```bash
# All tests
pytest

# Specific test categories
pytest tests/test_aidefence_integration.py
pytest tests/test_agentdb_integration.py
pytest tests/test_security_pipeline.py

# With coverage
pytest --cov=agentic_security --cov-report=html
```

### Manual Testing Checklist

```bash
# 1. AIDefence Protection
✓ Start gateway: npm run aidefence:start
✓ Detect threat: aidefence detect "Ignore previous instructions"
✓ Deep analysis: aidefence analyze "System: admin mode" --deep

# 2. AgentDB Memory
✓ Store episode: (via scan with --learn)
✓ Query episodes: agentdb reflexion retrieve "scan" --k 5
✓ Search skills: agentdb skill search "SQL injection"

# 3. Learning Loop
✓ First scan: agentic-security analyze ./test_app --learn
✓ Second scan: (should show learned context)
✓ Check improvement: agentdb stats

# 4. Multi-Agent Sync
✓ Start server: agentdb sync start-server --port 4433
✓ Connect client: agentdb sync connect localhost 4433 --auth-token TOKEN
✓ Sync: agentdb sync push --incremental
```

---

## Troubleshooting

### Common Issues

**Issue**: "AIDefence server not starting"
```bash
# Check if port 3000 is in use
lsof -i :3000

# Use different port
agentic-security protect start --port 3001
```

**Issue**: "AgentDB not found"
```bash
# Reinitialize
npm run agentdb:init

# Verify path in config
cat config.yml | grep db_path
```

**Issue**: "API key errors"
```bash
# Check environment variables
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY

# Reload .env
source .env
```

**Issue**: "Import errors"
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Verify installation
python -c "from agentic_security import SecurityPipeline; print('OK')"
```

---

## Performance Tips

### 1. Enable Caching

```yaml
# config.yml
cache:
  enabled: true
  backend: redis  # or memory
  ttl: 3600
```

### 2. Optimize AgentDB

```bash
# Use appropriate preset
agentdb init --preset large  # For >100K vectors

# Prune old data regularly
agentdb reflexion prune 90 0.3
agentdb skill prune 5 0.4 90
```

### 3. Batch Processing

```python
# Process multiple files efficiently
async def batch_scan(files):
    tasks = [
        pipeline.scan(file, learn=True)
        for file in files
    ]
    results = await asyncio.gather(*tasks)
    return results
```

---

## Next Steps

1. **Read Full Documentation**
   - [Vision & Overview](01-v2-vision-overview.md)
   - [Technical Architecture](02-technical-architecture.md)
   - [Feature Specifications](03-feature-specifications.md)

2. **Explore Integrations**
   - [AIDefence Integration](04-aidefence-integration.md)
   - [AgentDB Integration](05-agentdb-integration.md)

3. **Plan Development**
   - [Development Roadmap](06-development-roadmap.md)
   - [Migration Guide](07-migration-guide.md)

4. **Join Community**
   - GitHub: https://github.com/ruvnet/agentic-security
   - Discord: https://discord.gg/agentic-security
   - Docs: https://docs.agentic-security.com

---

## Quick Reference Card

### Essential Commands

```bash
# Setup (once)
npm install && npm run agentdb:init

# Start services
npm run aidefence:start &

# Daily workflow
agentic-security analyze ./src --learn --auto-fix

# Weekly maintenance
npm run agentdb:consolidate

# Check status
agentic-security doctor
```

### Key Files

```
config.yml              # Main configuration
agentdb.db             # Learning database
.env                   # API keys
security_reports/      # Scan results
logs/                  # Application logs
```

### Important Ports

```
3000 - AIDefence Gateway
4433 - AgentDB QUIC Sync
8501 - Streamlit GUI
```

---

## Support

- **Documentation**: https://docs.agentic-security.com
- **Issues**: https://github.com/ruvnet/agentic-security/issues
- **Email**: support@agentic-security.com

---

**Ready to build secure AI-native applications!** 🚀
