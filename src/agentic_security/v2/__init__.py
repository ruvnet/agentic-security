"""
Agentic Security v2.0 - AI-Native Security Intelligence Platform

This module provides the v2.0 enhanced security features including:
- AIDefence integration for prompt injection protection
- AgentDB integration for persistent memory and learning
- Multi-agent coordination via QUIC
- Pattern discovery and skill consolidation
"""

from .aidefence_client import AIDefenceClient, ThreatResult
from .agentdb_client import AgentDBClient, Episode, Skill, CausalEdge
from .security_pipeline_v2 import SecurityPipelineV2
from .pattern_learner import PatternLearner
from .skill_manager import SkillManager
from .multi_agent_coordinator import MultiAgentCoordinator

__version__ = "2.0.0"

__all__ = [
    "AIDefenceClient",
    "ThreatResult",
    "AgentDBClient",
    "Episode",
    "Skill",
    "CausalEdge",
    "SecurityPipelineV2",
    "PatternLearner",
    "SkillManager",
    "MultiAgentCoordinator",
]
