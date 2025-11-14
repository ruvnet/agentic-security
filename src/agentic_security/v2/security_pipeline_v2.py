"""
Agentic Security v2.0 Pipeline

Enhanced security pipeline with learning capabilities, AI protection, and team coordination.
"""

import logging
import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from ..security_pipeline import SecurityPipeline
from .aidefence_client import AIDefenceClient
from .agentdb_client import AgentDBClient, Episode, CausalEdge
from .pattern_learner import PatternLearner
from .skill_manager import SkillManager

logger = logging.getLogger(__name__)


class SecurityPipelineV2(SecurityPipeline):
    """
    v2.0 Security Pipeline with learning and AI protection

    Enhancements over v1.0:
    - AIDefence integration for prompt injection protection
    - AgentDB integration for persistent memory
    - Pattern learning and skill consolidation
    - Causal reasoning for fix effectiveness
    - Multi-agent coordination (optional)

    Usage:
        pipeline = SecurityPipelineV2(config_file='config.yml')
        await pipeline.initialize()

        # Scan with learning
        results = await pipeline.scan_with_learning(
            target='./src',
            use_history=True
        )

        # Cleanup
        await pipeline.shutdown()
    """

    def __init__(self, config_file='config.yml', timeout: int = 300):
        # Initialize parent
        super().__init__(config_file, timeout)

        # V2 components
        self.aidefence = None
        self.agentdb = None
        self.pattern_learner = None
        self.skill_manager = None

        # V2 configuration
        self.v2_config = self.config.get('v2', {})
        self.learning_enabled = self.v2_config.get('learning_enabled', True)
        self.aidefence_enabled = self.v2_config.get('aidefence_enabled', True)

        # Session tracking
        self.session_id = None

    async def initialize(self):
        """
        Initialize v2.0 components

        This should be called before using the pipeline.
        """
        logger.info("Initializing Agentic Security v2.0")

        # Generate session ID
        self.session_id = f"session-{uuid.uuid4().hex[:8]}"

        # Initialize AgentDB if enabled
        if self.learning_enabled:
            db_path = self.v2_config.get('agentdb', {}).get('db_path', './agentdb.db')
            self.agentdb = AgentDBClient(db_path)
            logger.info(f"AgentDB initialized: {db_path}")

            # Initialize pattern learner
            self.pattern_learner = PatternLearner(self.agentdb)

            # Initialize skill manager
            self.skill_manager = SkillManager(self.agentdb)

        # Initialize AIDefence if enabled
        if self.aidefence_enabled:
            aidefence_config = self.v2_config.get('aidefence', {})
            gateway_url = aidefence_config.get('gateway_url', 'http://localhost:3000')
            self.aidefence = AIDefenceClient(gateway_url)

            # Start server if configured
            if aidefence_config.get('auto_start', False):
                port = aidefence_config.get('port', 3000)
                try:
                    await self.aidefence.start_server(port=port)
                    logger.info(f"AIDefence server started on port {port}")
                except Exception as e:
                    logger.warning(f"Failed to start AIDefence server: {e}")
                    self.aidefence_enabled = False

        logger.info("v2.0 initialization complete")

    async def shutdown(self):
        """Cleanup v2.0 components"""
        logger.info("Shutting down v2.0 components")

        if self.aidefence and hasattr(self.aidefence, 'server_process'):
            await self.aidefence.stop_server()

        logger.info("v2.0 shutdown complete")

    async def scan_with_learning(
        self,
        target: str,
        use_history: bool = True,
        store_episode: bool = True,
        **kwargs
    ) -> Dict:
        """
        Scan with learning enabled

        Args:
            target: Path to scan
            use_history: Use past scanning history
            store_episode: Store this scan as an episode
            **kwargs: Additional arguments for scan

        Returns:
            Enhanced scan results with learning insights

        Example:
            results = await pipeline.scan_with_learning(
                target='./src',
                use_history=True
            )
            print(f"Learning reward: {results['reward']}")
        """
        start_time = datetime.now()

        # Step 1: Query past experiences if enabled
        past_context = {}
        if use_history and self.learning_enabled:
            logger.info("Querying past experiences...")
            past_context = await self._query_past_experiences(target)

        # Step 2: Execute traditional scan with context
        logger.info(f"Scanning {target}...")
        scan_results = await self._execute_scan(target, past_context, **kwargs)

        # Step 3: AI-enhanced analysis with protection
        if scan_results.get('vulnerabilities'):
            logger.info("Performing AI analysis...")
            scan_results['ai_analysis'] = await self._protected_ai_analysis(
                scan_results,
                past_context
            )

        # Step 4: Apply fixes using skills if available
        if kwargs.get('auto_fix') and self.learning_enabled:
            logger.info("Applying skill-based fixes...")
            fix_results = await self._apply_skill_based_fixes(
                scan_results.get('vulnerabilities', [])
            )
            scan_results['fixes'] = fix_results

        # Step 5: Calculate reward and store episode
        duration = (datetime.now() - start_time).total_seconds()
        reward = self._calculate_reward(scan_results)
        scan_results['reward'] = reward
        scan_results['duration'] = duration

        if store_episode and self.learning_enabled:
            await self._store_scan_episode(
                target=target,
                results=scan_results,
                reward=reward,
                duration=duration
            )

        # Step 6: Trigger learning if configured
        if self.learning_enabled:
            asyncio.create_task(self._trigger_background_learning())

        return scan_results

    async def _query_past_experiences(self, target: str) -> Dict:
        """Query AgentDB for relevant past experiences"""
        if not self.agentdb:
            return {}

        try:
            # Query similar scans
            episodes = await self.agentdb.retrieve_episodes(
                task=f"scan:{target}",
                k=10,
                only_successes=True,
                synthesize_context=True
            )

            # Query relevant skills
            skills = await self.agentdb.search_skills(
                query=f"security scan {target}",
                k=5
            )

            return {
                'episodes': episodes.get('episodes', []),
                'synthesized_context': episodes.get('synthesized_context', ''),
                'relevant_skills': skills,
                'past_patterns': await self._get_learned_patterns()
            }
        except Exception as e:
            logger.error(f"Failed to query past experiences: {e}")
            return {}

    async def _execute_scan(self, target: str, context: Dict, **kwargs) -> Dict:
        """Execute scan using parent pipeline with context"""
        # Use parent's scan functionality
        # Note: This is a simplified version. In production, you'd call
        # the actual parent scan methods properly

        return {
            'target': target,
            'vulnerabilities': [],  # Populated by actual scan
            'timestamp': datetime.now().isoformat(),
            'context_used': bool(context),
        }

    async def _protected_ai_analysis(self, results: Dict, context: Dict) -> Dict:
        """
        AI analysis with AIDefence protection

        Validates all inputs/outputs for prompt injection
        """
        if not self.aidefence_enabled or not self.aidefence:
            # Fallback to unprotected analysis
            return await self._unprotected_ai_analysis(results, context)

        try:
            # Build analysis prompt
            prompt = self._build_analysis_prompt(results, context)

            # Validate prompt for injection
            threat_check = await self.aidefence.detect(prompt)
            if threat_check.is_threat:
                logger.warning(f"Threat detected in prompt: {threat_check.threat_type}")
                prompt = await self.aidefence.sanitize_input(prompt)

            # Call AI model (placeholder - would use actual AI client)
            ai_response = await self._call_ai_model(prompt)

            # Validate response
            response_check = await self.aidefence.analyze(ai_response, deep=True)
            if response_check.is_threat:
                logger.error(f"Threat in AI response: {response_check.threat_type}")
                raise SecurityError("Unsafe AI output detected")

            return {
                'analysis': ai_response,
                'protected': True,
                'threat_checks': {
                    'input': threat_check.to_dict() if hasattr(threat_check, 'to_dict') else {},
                    'output': response_check.to_dict() if hasattr(response_check, 'to_dict') else {}
                }
            }
        except Exception as e:
            logger.error(f"Protected AI analysis failed: {e}")
            return await self._unprotected_ai_analysis(results, context)

    async def _unprotected_ai_analysis(self, results: Dict, context: Dict) -> Dict:
        """Fallback AI analysis without protection"""
        # Implement actual AI analysis here
        return {
            'analysis': 'AI analysis placeholder',
            'protected': False
        }

    def _build_analysis_prompt(self, results: Dict, context: Dict) -> str:
        """Build prompt for AI analysis"""
        prompt_parts = [
            "Analyze the following security scan results:",
            f"\nVulnerabilities found: {len(results.get('vulnerabilities', []))}",
        ]

        if context.get('synthesized_context'):
            prompt_parts.append(f"\nPast context: {context['synthesized_context']}")

        return "\n".join(prompt_parts)

    async def _call_ai_model(self, prompt: str) -> str:
        """Call AI model (placeholder for actual implementation)"""
        # This would integrate with actual AI providers
        # For now, return placeholder
        return "AI analysis result placeholder"

    async def _apply_skill_based_fixes(self, vulnerabilities: List[Dict]) -> List[Dict]:
        """Apply fixes using skill library"""
        if not self.skill_manager:
            return []

        fixes = []
        for vuln in vulnerabilities:
            try:
                fix_result = await self.skill_manager.apply_best_skill(vuln)
                if fix_result:
                    fixes.append(fix_result)
            except Exception as e:
                logger.error(f"Failed to apply skill for {vuln.get('type')}: {e}")

        return fixes

    def _calculate_reward(self, results: Dict) -> float:
        """
        Calculate reward score for this scan

        Factors:
        - Vulnerabilities found (true positives)
        - False positives
        - Fix success rate
        - Duration
        """
        vulns_found = len(results.get('vulnerabilities', []))
        false_positives = results.get('false_positives', 0)
        fix_rate = results.get('fix_success_rate', 0.0)
        duration = results.get('duration', 0)

        # Normalize duration to 5 minutes
        duration_penalty = min(duration / 300, 1.0)

        reward = (
            (vulns_found * 0.3) -
            (false_positives * 0.2) +
            (fix_rate * 0.4) -
            (duration_penalty * 0.1)
        )

        return max(0.0, min(1.0, reward))

    async def _store_scan_episode(
        self,
        target: str,
        results: Dict,
        reward: float,
        duration: float
    ):
        """Store scan as learning episode"""
        if not self.agentdb:
            return

        try:
            episode = Episode(
                session_id=self.session_id,
                task=f"scan:{target}",
                reward=reward,
                success=results.get('success', True),
                critique=self._generate_critique(results),
                latency_ms=int(duration * 1000),
                metadata={
                    'vulnerabilities_found': len(results.get('vulnerabilities', [])),
                    'false_positives': results.get('false_positives', 0),
                    'fixes_applied': len(results.get('fixes', [])),
                    'ai_protected': results.get('ai_analysis', {}).get('protected', False),
                }
            )

            await self.agentdb.store_episode(episode)
            logger.info(f"Stored episode with reward {reward:.2f}")

            # Store causal edges for fixes
            for fix in results.get('fixes', []):
                if fix.get('success'):
                    await self.agentdb.add_causal_edge(CausalEdge(
                        cause=f"fix:{fix['type']}",
                        effect="vulnerability_resolved",
                        uplift=0.8,
                        confidence=0.9,
                        sample_size=1
                    ))
        except Exception as e:
            logger.error(f"Failed to store episode: {e}")

    def _generate_critique(self, results: Dict) -> str:
        """Generate self-critique for learning"""
        critiques = []

        if results.get('success'):
            vuln_count = len(results.get('vulnerabilities', []))
            critiques.append(f"✓ Successfully found {vuln_count} vulnerabilities")

        if results.get('false_positives', 0) > 0:
            critiques.append(f"⚠ {results['false_positives']} false positives")

        if results.get('fixes'):
            success_count = sum(1 for f in results['fixes'] if f.get('success'))
            critiques.append(f"✓ Applied {success_count}/{len(results['fixes'])} fixes")

        return "\n".join(critiques)

    async def _get_learned_patterns(self) -> List[Dict]:
        """Get learned vulnerability patterns"""
        if not self.pattern_learner:
            return []

        try:
            return await self.pattern_learner.get_active_patterns()
        except Exception as e:
            logger.error(f"Failed to get patterns: {e}")
            return []

    async def _trigger_background_learning(self):
        """Trigger background pattern learning and skill consolidation"""
        try:
            # Discover new patterns
            if self.pattern_learner:
                await self.pattern_learner.discover_patterns()

            # Consolidate skills
            if self.skill_manager:
                await self.skill_manager.consolidate_skills()
        except Exception as e:
            logger.error(f"Background learning failed: {e}")


class SecurityError(Exception):
    """Security-related error"""
    pass
