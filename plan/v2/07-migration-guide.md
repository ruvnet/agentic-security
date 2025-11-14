# Agentic Security v1.0 → v2.0 Migration Guide

## Table of Contents
1. [Overview](#overview)
2. [Breaking Changes](#breaking-changes)
3. [Migration Steps](#migration-steps)
4. [Compatibility Mode](#compatibility-mode)
5. [Feature Mapping](#feature-mapping)
6. [Troubleshooting](#troubleshooting)

---

## Overview

### What's Changing?

Agentic Security v2.0 introduces **learning and AI security capabilities** while maintaining backward compatibility with v1.0 workflows.

**Key Changes**:
- ✅ New: AgentDB for persistent memory
- ✅ New: AIDefence for AI security
- ✅ New: Skill-based fixes
- ✅ New: Multi-agent coordination
- ⚠️ Changed: Configuration file format
- ⚠️ Changed: CLI command structure
- ✅ Compatible: Existing scan results
- ✅ Compatible: Security patterns

### Migration Strategy

```
Option 1: Gradual Migration (Recommended)
├─ Keep v1.0 running
├─ Install v2.0 alongside
├─ Test v2.0 with learning disabled
├─ Enable learning features gradually
└─ Full migration when ready

Option 2: Clean Migration
├─ Backup v1.0 data
├─ Uninstall v1.0
├─ Install v2.0
└─ Migrate data and config
```

---

## Breaking Changes

### 1. Configuration File Format

**v1.0 (`config.yml`)**:
```yaml
security:
  critical_threshold: 7.0
  max_fix_attempts: 3

ai:
  model: gpt-4-1106-preview
```

**v2.0 (`config.yml`)**:
```yaml
security:
  critical_threshold: 7.0
  max_fix_attempts: 3

ai:
  models:  # Changed: Now supports multiple models
    architecture_review: gpt-4-1106-preview
    fix_implementation: claude-3-5-sonnet-20241022

# New sections
agentdb:
  enabled: true
  db_path: ./agentdb.db

aidefence:
  enabled: true
  port: 3000
```

**Migration**: Use the auto-migration tool:
```bash
agentic-security migrate config --from config.yml --to config-v2.yml
```

### 2. CLI Commands

**v1.0**:
```bash
agentic-security analyze ./src
agentic-security fix ./src/auth.py
```

**v2.0** (backward compatible + new):
```bash
# Old commands still work
agentic-security analyze ./src

# New commands available
agentic-security analyze ./src --learn  # Enable learning
agentic-security learn "SQL injection"   # Query memory
agentic-security protect start           # Start AIDefence
agentic-security sync start              # Multi-agent sync
```

### 3. Python API

**v1.0**:
```python
from agentic_security import SecurityPipeline

pipeline = SecurityPipeline(config)
results = await pipeline.scan(target)
```

**v2.0** (backward compatible):
```python
from agentic_security import SecurityPipeline

# v1.0 style still works
pipeline = SecurityPipeline(config)
results = await pipeline.scan(target)

# v2.0 style with learning
from agentic_security.v2 import SecurityPipelineV2

pipeline = SecurityPipelineV2(config)
results = await pipeline.scan_with_learning(target)
```

---

## Migration Steps

### Step 1: Backup Existing Data

```bash
# Backup v1.0 configuration
cp config.yml config.yml.v1.backup

# Backup security reports
tar -czf security_reports_backup.tar.gz security_reports/

# Backup custom patterns (if any)
cp -r custom_patterns/ custom_patterns.v1.backup/
```

### Step 2: Install v2.0

```bash
# Install via pip
pip install --upgrade agentic-security

# Verify installation
agentic-security version  # Should show 2.0.0

# Install Node.js dependencies
npm install

# Initialize AgentDB
npx agentdb init ./agentdb.db --dimension 1536 --preset medium
```

### Step 3: Migrate Configuration

```bash
# Auto-migrate config
agentic-security migrate config \
  --from config.yml \
  --to config-v2.yml

# Review changes
diff config.yml config-v2.yml

# Apply if satisfied
mv config-v2.yml config.yml
```

### Step 4: Test Compatibility

```bash
# Test with learning disabled (v1.0 mode)
agentic-security analyze ./src --config config.yml

# If successful, test with learning enabled
agentic-security analyze ./src --learn
```

### Step 5: Migrate Historical Data (Optional)

```bash
# Import past scan results into AgentDB
agentic-security migrate history \
  --from ./security_reports \
  --format v1

# Verify import
npx agentdb stats ./agentdb.db
```

### Step 6: Enable New Features

```yaml
# config.yml - Enable features gradually

# Week 1: Enable memory
agentdb:
  enabled: true

# Week 2: Enable AI security
aidefence:
  enabled: true

# Week 3: Enable multi-agent (optional)
sync:
  enabled: true
  server: 192.168.1.100:4433
```

---

## Compatibility Mode

### Running v2.0 in v1.0 Mode

Completely disable learning features:

```yaml
# config.yml
v1_compatibility_mode: true

# This disables:
# - AgentDB storage
# - AIDefence (uses basic validation)
# - Skill-based fixes
# - Multi-agent sync
```

Or via CLI:
```bash
agentic-security analyze ./src --v1-mode
```

### Side-by-Side Installation

Run both versions simultaneously:

```bash
# Install v2.0 in separate environment
python -m venv venv-v2
source venv-v2/bin/activate
pip install agentic-security==2.0.0

# v1.0 in original environment
deactivate
source venv-v1/bin/activate
pip install agentic-security==1.0.0

# Use different configs
agentic-security-v1 analyze --config config-v1.yml
agentic-security-v2 analyze --config config-v2.yml
```

---

## Feature Mapping

### Scan Features

| v1.0 Feature | v2.0 Equivalent | Notes |
|--------------|-----------------|-------|
| `analyze` | `analyze` or `analyze --learn` | Learning optional |
| `--auto-fix` | `--auto-fix` (uses skills if available) | Enhanced with skill library |
| `--config` | `--config` | Compatible, extended |
| Pattern detection | Pattern detection + learning | Auto-discovers new patterns |
| Static rules | Static rules + dynamic patterns | Learns over time |

### Fix Features

| v1.0 Feature | v2.0 Equivalent | Notes |
|--------------|-----------------|-------|
| `fix` | `fix` or `fix --use-skills` | Skill-based by default |
| AI-generated fixes | AI + skill library | Better quality |
| Manual templates | Skills + templates | Reusable across team |
| Single fix attempt | Causal-guided fixes | Higher success rate |

### Reporting

| v1.0 Feature | v2.0 Equivalent | Notes |
|--------------|-----------------|-------|
| JSON reports | JSON reports + learning insights | Extended format |
| HTML dashboard | Enhanced GUI with memory explorer | More features |
| SARIF output | SARIF output (compatible) | No changes |
| Custom reports | Custom reports + analytics | More data available |

---

## Troubleshooting

### Issue: "AgentDB not initialized"

**Solution**:
```bash
npx agentdb init ./agentdb.db --dimension 1536 --preset medium
```

### Issue: "AIDefence server not running"

**Solution**:
```bash
# Start server manually
agentic-security protect start --port 3000

# Or disable in config
aidefence:
  enabled: false
```

### Issue: "Import Error: No module named 'aiohttp'"

**Solution**:
```bash
pip install aiohttp>=3.9.0 redis>=5.0.0
```

### Issue: "Slow performance after migration"

**Solution**:
```bash
# Check database size
npx agentdb stats ./agentdb.db

# Optimize if needed
npx agentdb optimize-memory --compress true --consolidate-patterns true

# Clear cache
agentic-security cache clear
```

### Issue: "v1.0 patterns not working"

**Solution**:
```bash
# Migrate patterns to v2.0 format
agentic-security migrate patterns \
  --from custom_patterns/ \
  --to ./agentdb.db
```

### Issue: "High memory usage"

**Cause**: AgentDB storing too much data

**Solution**:
```bash
# Configure retention
agentdb:
  retention_days: 90  # Keep only 90 days
  max_episodes: 10000  # Limit total episodes

# Or prune manually
npx agentdb reflexion prune 90 0.3
```

---

## Rollback Plan

If issues occur, rollback to v1.0:

```bash
# 1. Stop v2.0 services
agentic-security protect stop
pkill -f aidefence

# 2. Restore v1.0 config
mv config.yml.v1.backup config.yml

# 3. Uninstall v2.0
pip uninstall agentic-security

# 4. Reinstall v1.0
pip install agentic-security==1.0.0

# 5. Verify
agentic-security version  # Should show 1.0.0
```

---

## Migration Checklist

Use this checklist to track migration progress:

### Pre-Migration
- [ ] Backup v1.0 configuration
- [ ] Backup security reports
- [ ] Document custom patterns
- [ ] Review v2.0 requirements
- [ ] Test in non-production environment

### Installation
- [ ] Install v2.0 package
- [ ] Install Node.js dependencies
- [ ] Initialize AgentDB
- [ ] Verify installation

### Configuration
- [ ] Migrate config file
- [ ] Update CI/CD pipelines
- [ ] Update documentation
- [ ] Configure new features

### Testing
- [ ] Test in v1.0 compatibility mode
- [ ] Test basic scanning
- [ ] Test with learning enabled
- [ ] Test fix generation
- [ ] Performance testing

### Data Migration
- [ ] Import historical scan data
- [ ] Verify data integrity
- [ ] Test queries on migrated data

### Deployment
- [ ] Deploy to staging
- [ ] User acceptance testing
- [ ] Deploy to production
- [ ] Monitor for issues

### Post-Migration
- [ ] Train team on new features
- [ ] Update internal documentation
- [ ] Collect feedback
- [ ] Optimize configuration

---

## Support

Need help with migration?

- **Documentation**: https://docs.agentic-security.com/v2/migration
- **GitHub Issues**: https://github.com/ruvnet/agentic-security/issues
- **Community**: https://discord.gg/agentic-security
- **Email**: support@agentic-security.com

---

**Estimated Migration Time**:
- Small projects (<1000 files): 1-2 hours
- Medium projects (1000-10K files): 2-4 hours
- Large projects (>10K files): 4-8 hours
- Enterprise deployments: 1-2 days

**Recommended Approach**: Gradual migration with 2-4 week transition period.
