"""Skill management system for reusable security fixes"""

import logging
from typing import Dict, List, Optional
from .agentdb_client import AgentDBClient, Skill

logger = logging.getLogger(__name__)


class SkillManager:
    """Manages skill library and application"""

    def __init__(self, agentdb: AgentDBClient):
        self.agentdb = agentdb

    async def search_applicable_skills(
        self,
        vulnerability_type: str,
        k: int = 5
    ) -> List[Dict]:
        """Search for skills applicable to vulnerability type"""
        return await self.agentdb.search_skills(vulnerability_type, k=k)

    async def apply_best_skill(self, vulnerability: Dict) -> Optional[Dict]:
        """Apply the best matching skill to a vulnerability"""
        vuln_type = vulnerability.get('type', 'unknown')

        # Search for applicable skills
        skills = await self.search_applicable_skills(vuln_type)

        if not skills:
            logger.debug(f"No skills found for {vuln_type}")
            return None

        # Apply best skill
        best_skill = skills[0]
        logger.info(f"Applying skill: {best_skill.get('name')}")

        # This would integrate with actual fix application (e.g., via Aider)
        # For now, return simulated result
        return {
            'skill_used': best_skill.get('name'),
            'type': vuln_type,
            'success': True,
            'file': vulnerability.get('file'),
            'description': f"Applied {best_skill.get('name')}"
        }

    async def consolidate_skills(
        self,
        min_attempts: int = 3,
        min_reward: float = 0.7
    ) -> Dict:
        """Consolidate successful episodes into new skills"""
        logger.info("Consolidating skills from successful episodes...")

        results = await self.agentdb.consolidate_skills(
            min_attempts=min_attempts,
            min_reward=min_reward,
            extract_patterns=True
        )

        skills_created = len(results.get('skills', []))
        logger.info(f"Created {skills_created} new skills")

        return results

    async def create_skill(self, skill: Skill) -> bool:
        """Create a new skill manually"""
        return await self.agentdb.create_skill(skill)
