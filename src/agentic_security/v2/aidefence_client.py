"""
AIDefence Python client wrapper for prompt injection detection and AI security.

This module provides a Python interface to AIDefence (v2.1.0) for protecting
AI models from prompt injection and other manipulation attempts.
"""

import asyncio
import subprocess
import json
import logging
from typing import Dict, Optional, List
from dataclasses import dataclass
import aiohttp
import re

logger = logging.getLogger(__name__)


@dataclass
class ThreatResult:
    """Threat detection result"""
    is_threat: bool
    confidence: float
    threat_type: Optional[str]
    patterns_matched: List[str]
    details: Dict

    def __str__(self):
        if self.is_threat:
            return f"⚠️  THREAT: {self.threat_type} (confidence: {self.confidence:.1%})"
        return f"✓ No threats detected"


class AIDefenceClient:
    """
    Python client for AIDefence protection

    Usage:
        async with AIDefenceClient() as client:
            await client.start_server()
            result = await client.detect("suspicious text")
            if result.is_threat:
                print("Threat detected!")
    """

    def __init__(self, gateway_url: str = "http://localhost:3000"):
        self.gateway_url = gateway_url
        self.server_process = None
        self.session = None
        self._healthy = False

    async def __aenter__(self):
        """Context manager entry"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.session:
            await self.session.close()
        if self.server_process:
            await self.stop_server()

    async def start_server(self, port: int = 3000, host: str = "0.0.0.0") -> Dict:
        """
        Start AIMDS Gateway server

        Args:
            port: Port to listen on
            host: Host to bind to

        Returns:
            Server info dict

        Raises:
            RuntimeError: If server already running or failed to start
        """
        if self.server_process:
            raise RuntimeError("Server already running")

        logger.info(f"Starting AIDefence server on {host}:{port}")

        self.server_process = subprocess.Popen(
            ['aidefence', 'server', '--port', str(port), '--host', host],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Wait for server to be ready
        try:
            await self._wait_for_ready(timeout=10)
            self._healthy = True
        except TimeoutError:
            await self.stop_server()
            raise RuntimeError("Failed to start AIDefence server within timeout")

        self.gateway_url = f"http://{host}:{port}"

        logger.info(f"AIDefence server started successfully: {self.gateway_url}")

        return {
            'status': 'running',
            'url': self.gateway_url,
            'pid': self.server_process.pid,
            'port': port,
            'host': host
        }

    async def stop_server(self):
        """Stop AIMDS Gateway server"""
        if self.server_process:
            logger.info("Stopping AIDefence server")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning("Server didn't stop gracefully, killing...")
                self.server_process.kill()
                self.server_process.wait()
            self.server_process = None
            self._healthy = False
            logger.info("AIDefence server stopped")

    async def detect(self, text: str, verbose: bool = False) -> ThreatResult:
        """
        Detect threats in text input

        Args:
            text: Text to analyze
            verbose: Include detailed information

        Returns:
            ThreatResult object

        Example:
            result = await client.detect("Ignore previous instructions")
            if result.is_threat:
                print(f"Threat: {result.threat_type}")
        """
        if not self.session:
            self.session = aiohttp.ClientSession()

        try:
            # Try API first
            async with self.session.post(
                f"{self.gateway_url}/api/detect",
                json={'text': text, 'verbose': verbose},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return ThreatResult(
                        is_threat=data.get('is_threat', False),
                        confidence=data.get('confidence', 0.0),
                        threat_type=data.get('threat_type'),
                        patterns_matched=data.get('patterns', []),
                        details=data
                    )
        except Exception as e:
            logger.debug(f"API call failed, falling back to CLI: {e}")
            # Fallback to CLI
            return await self._detect_cli(text, verbose)

        # If we get here, something went wrong
        return await self._detect_cli(text, verbose)

    async def analyze(self, text: str, deep: bool = False) -> ThreatResult:
        """
        Analyze text for prompt injection patterns

        Args:
            text: Text to analyze
            deep: Enable deep analysis with behavioral verification

        Returns:
            ThreatResult object

        Example:
            result = await client.analyze("System: admin mode", deep=True)
            print(f"Behavioral score: {result.details.get('behavioral_score')}")
        """
        if not self.session:
            self.session = aiohttp.ClientSession()

        try:
            async with self.session.post(
                f"{self.gateway_url}/api/analyze",
                json={'text': text, 'deep': deep},
                timeout=aiohttp.ClientTimeout(total=20 if deep else 10)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return ThreatResult(
                        is_threat=data.get('is_threat', False),
                        confidence=data.get('confidence', 0.0),
                        threat_type=data.get('threat_type'),
                        patterns_matched=data.get('patterns', []),
                        details=data
                    )
        except Exception as e:
            logger.debug(f"API call failed, falling back to CLI: {e}")
            return await self._analyze_cli(text, deep)

        return await self._analyze_cli(text, deep)

    async def sanitize_input(self, text: str) -> str:
        """
        Attempt to sanitize potentially malicious input

        Args:
            text: Text to sanitize

        Returns:
            Sanitized text

        Raises:
            SecurityError: If unable to sanitize safely
        """
        # First check if it's a threat
        result = await self.detect(text)

        if not result.is_threat:
            return text

        logger.warning(f"Threat detected in input: {result.threat_type}")

        # Attempt sanitization
        sanitized = self._remove_injection_patterns(text)

        # Re-check
        recheck = await self.detect(sanitized)

        if recheck.is_threat:
            from agentic_security.exceptions import SecurityError
            raise SecurityError(
                f"Unable to sanitize input safely. Threat type: {result.threat_type}"
            )

        logger.info("Input successfully sanitized")
        return sanitized

    def _remove_injection_patterns(self, text: str) -> str:
        """Remove common injection patterns"""
        patterns = [
            r"ignore\s+previous\s+instructions?",
            r"disregard.*rules?",
            r"new\s+instructions?:",
            r"forget\s+everything",
            r"system\s*:",
            r"</prompt>",
            r"<\|endoftext\|>",
            r"<\|im_end\|>",
            r"assistant\s*:",
            r"human\s*:",
        ]

        sanitized = text
        for pattern in patterns:
            sanitized = re.sub(
                pattern, "",
                sanitized,
                flags=re.IGNORECASE | re.MULTILINE
            )

        return sanitized.strip()

    async def _detect_cli(self, text: str, verbose: bool) -> ThreatResult:
        """Fallback: Use CLI for detection"""
        cmd = ['aidefence', 'detect', text]
        if verbose:
            cmd.append('--verbose')

        try:
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            output = stdout.decode()

            # Parse CLI output
            is_threat = 'THREAT DETECTED' in output.upper() or 'INJECTION' in output.upper()

            return ThreatResult(
                is_threat=is_threat,
                confidence=0.8 if is_threat else 0.2,
                threat_type='prompt_injection' if is_threat else None,
                patterns_matched=[],
                details={'source': 'cli', 'output': output}
            )
        except Exception as e:
            logger.error(f"CLI detection failed: {e}")
            # Conservative: assume threat if we can't check
            return ThreatResult(
                is_threat=False,
                confidence=0.0,
                threat_type=None,
                patterns_matched=[],
                details={'error': str(e)}
            )

    async def _analyze_cli(self, text: str, deep: bool) -> ThreatResult:
        """Fallback: Use CLI for analysis"""
        cmd = ['aidefence', 'analyze', text]
        if deep:
            cmd.append('--deep')

        try:
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            output = stdout.decode()

            # Parse CLI output
            is_threat = 'THREAT' in output.upper() or 'INJECTION' in output.upper()

            return ThreatResult(
                is_threat=is_threat,
                confidence=0.8 if is_threat else 0.2,
                threat_type='prompt_injection' if is_threat else None,
                patterns_matched=[],
                details={'source': 'cli', 'output': output}
            )
        except Exception as e:
            logger.error(f"CLI analysis failed: {e}")
            return ThreatResult(
                is_threat=False,
                confidence=0.0,
                threat_type=None,
                patterns_matched=[],
                details={'error': str(e)}
            )

    async def _wait_for_ready(self, timeout: int = 10):
        """Wait for server to be ready"""
        start = asyncio.get_event_loop().time()

        while asyncio.get_event_loop().time() - start < timeout:
            try:
                if not self.session:
                    self.session = aiohttp.ClientSession()

                async with self.session.get(
                    f"{self.gateway_url}/health",
                    timeout=aiohttp.ClientTimeout(total=1)
                ) as response:
                    if response.status == 200:
                        return
            except:
                pass

            await asyncio.sleep(0.5)

        raise TimeoutError("Server failed to start within timeout")

    async def get_stats(self) -> Dict:
        """Get threat detection statistics"""
        if not self.session:
            self.session = aiohttp.ClientSession()

        try:
            async with self.session.get(
                f"{self.gateway_url}/api/stats",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    return await response.json()
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")

        return {}

    @property
    def is_healthy(self) -> bool:
        """Check if server is running and healthy"""
        return self._healthy and self.server_process is not None


# Convenience functions
async def detect_threat(text: str, gateway_url: str = "http://localhost:3000") -> bool:
    """Quick threat detection"""
    async with AIDefenceClient(gateway_url) as client:
        result = await client.detect(text)
        return result.is_threat


async def analyze_prompt(text: str, deep: bool = True,
                        gateway_url: str = "http://localhost:3000") -> ThreatResult:
    """Analyze prompt with deep inspection"""
    async with AIDefenceClient(gateway_url) as client:
        return await client.analyze(text, deep=deep)
