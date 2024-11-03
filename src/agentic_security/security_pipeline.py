#!/usr/bin/env python3

import subprocess
import json
import os
from datetime import datetime
import yaml
import requests
from pathlib import Path
from typing import Dict, List, Optional, Union

# Configuration Variables
OPENAI_MODEL = "gpt-4-1106-preview"  # o1-preview model
CLAUDE_MODEL = "claude-3-sonnet-20240229"  # Latest Sonnet model
DEFAULT_CONFIG = {
    "security": {
        "critical_threshold": 7.0,
        "max_fix_attempts": 3,
        "scan_targets": []
    }
}

class SecurityPipeline:
    def __init__(self, config_file='config.yml'):
        self.load_config(config_file)
        self.critical_threshold = self.config['security']['critical_threshold']
        self.max_fix_attempts = self.config['security']['max_fix_attempts']
        self.branch_name = f"security-fixes-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    def load_config(self, config_file: str) -> None:
        """Load configuration from YAML file or use defaults"""
        try:
            with open(config_file, 'r') as f:
                self.config = yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_file}")

    def setup_environment(self) -> None:
        """Set up necessary environment variables and paths"""
        required_vars = ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'SLACK_WEBHOOK']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

    def run_architecture_review(self) -> Dict:
        """Run architecture review using OpenAI o1-preview"""
        print("Running architecture review with OpenAI o1-preview...")
        
        result = subprocess.run([
            "aider",
            "--model", OPENAI_MODEL,
            "--edit-format", "diff",
            "/ask",
            "Review the architecture for security vulnerabilities and suggest improvements:",
            "."
        ], capture_output=True, text=True, check=True)
        
        return {"output": result.stdout, "suggestions": self._parse_ai_suggestions(result.stdout)}

    def _parse_ai_suggestions(self, output: str) -> List[str]:
        """Parse AI suggestions from output"""
        # Simple parsing logic - can be enhanced based on actual output format
        suggestions = []
        for line in output.split('\n'):
            if line.strip().startswith('- '):
                suggestions.append(line.strip()[2:])
        return suggestions

    def implement_fixes(self, suggestions: List[str]) -> bool:
        """Implement fixes using Claude 3.5 Sonnet"""
        print("Implementing fixes with Claude 3.5 Sonnet...")
        
        success = True
        for suggestion in suggestions:
            try:
                result = subprocess.run([
                    "aider",
                    "--model", CLAUDE_MODEL,
                    "--edit-format", "diff",
                    "/code",
                    f"Implement the following security fix: {suggestion}",
                    "."
                ], capture_output=True, text=True, check=True)
                
                if "No changes made" in result.stdout:
                    print(f"Warning: No changes made for suggestion: {suggestion}")
                    success = False
            except subprocess.CalledProcessError:
                print(f"Error implementing fix for: {suggestion}")
                success = False
        
        return success

    def run_security_checks(self) -> Dict:
        """Run comprehensive security scans"""
        results = {"web": [], "code": []}
        
        for target in self.config['security']['scan_targets']:
            if target['type'] == 'web':
                results['web'].append(self._run_web_security_checks(target['url']))
            elif target['type'] == 'code':
                results['code'].append(self._run_code_security_checks(target['path']))
        
        return results

    def _run_web_security_checks(self, url: str) -> Dict:
        """Run web-specific security checks"""
        print(f"Running web security checks for {url}")
        results = {}
        
        # OWASP ZAP scan
        try:
            zap_result = subprocess.run([
                "docker", "run", "-t", "owasp/zap2docker-stable", "zap-baseline.py",
                "-t", url, "-J", "zap-report.json"
            ], capture_output=True, text=True)
            results['zap'] = self._parse_zap_results("zap-report.json")
        except Exception as e:
            print(f"Error running ZAP scan: {str(e)}")
            results['zap'] = {"error": str(e)}

        # Nuclei scan
        try:
            nuclei_result = subprocess.run([
                "nuclei", "-u", url, "-json", "-o", "nuclei-report.jsonl"
            ], capture_output=True, text=True)
            results['nuclei'] = self._parse_nuclei_results("nuclei-report.jsonl")
        except Exception as e:
            print(f"Error running Nuclei scan: {str(e)}")
            results['nuclei'] = {"error": str(e)}

        return results

    def _run_code_security_checks(self, path: str) -> Dict:
        """Run code-specific security checks"""
        print(f"Running code security checks for {path}")
        results = {}
        
        # Dependency check
        try:
            dep_check_result = subprocess.run([
                "./dependency-check/bin/dependency-check.sh",
                "--scan", path,
                "--format", "JSON",
                "--out", "dependency-check-report.json"
            ], capture_output=True, text=True)
            results['dependency'] = self._parse_dependency_results("dependency-check-report.json")
        except Exception as e:
            print(f"Error running dependency check: {str(e)}")
            results['dependency'] = {"error": str(e)}

        return results

    def _parse_zap_results(self, report_file: str) -> Dict:
        """Parse ZAP scan results"""
        try:
            with open(report_file, 'r') as f:
                data = json.load(f)
                return data
        except Exception as e:
            return {"error": f"Failed to parse ZAP results: {str(e)}"}

    def _parse_nuclei_results(self, report_file: str) -> List[Dict]:
        """Parse Nuclei scan results"""
        results = []
        try:
            with open(report_file, 'r') as f:
                for line in f:
                    if line.strip():
                        results.append(json.loads(line))
            return results
        except Exception as e:
            return [{"error": f"Failed to parse Nuclei results: {str(e)}"}]

    def _parse_dependency_results(self, report_file: str) -> Dict:
        """Parse dependency check results"""
        try:
            with open(report_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            return {"error": f"Failed to parse dependency check results: {str(e)}"}

    def _get_max_severity(self, result: Dict) -> float:
        """Get maximum severity from a result set"""
        try:
            if 'zap' in result:
                return max(float(alert.get('riskcode', 0)) for alert in result['zap'].get('alerts', []))
            elif 'nuclei' in result:
                severity_map = {'critical': 9.0, 'high': 7.0, 'medium': 5.0, 'low': 3.0, 'info': 0.0}
                return max(severity_map.get(str(finding.get('severity', '')).lower(), 0.0) 
                         for finding in result['nuclei'])
            elif 'dependency' in result:
                return max(float(vuln.get('cvssScore', 0)) 
                         for vuln in result['dependency'].get('vulnerabilities', []))
        except Exception as e:
            print(f"Error calculating severity: {str(e)}")
            return 0.0
        return 0.0

    def create_fix_branch(self) -> bool:
        """Create a new branch for security fixes"""
        try:
            print(f"Creating fix branch: {self.branch_name}")
            subprocess.run(["git", "checkout", "-b", self.branch_name], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error creating branch: {str(e)}")
            return False

    def create_pull_request(self) -> bool:
        """Create PR with AI-generated description"""
        try:
            print("Creating pull request...")
            
            # Get changed files
            result = subprocess.run(
                ["git", "diff", "--name-only", "main", self.branch_name],
                capture_output=True,
                text=True,
                check=True
            )
            changed_files = result.stdout.strip().split('\n')
            
            # Generate PR description using o1-preview
            pr_description = subprocess.run([
                "aider",
                "--model", OPENAI_MODEL,
                "/ask",
                "Generate a detailed PR description for these security changes:",
                *changed_files
            ], capture_output=True, text=True, check=True).stdout.strip()
            
            # Create PR
            subprocess.run([
                "gh", "pr", "create",
                "--title", "Security: AI-Reviewed Security Fixes",
                "--body", pr_description,
                "--head", self.branch_name,
                "--base", "main"
            ], check=True)
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error creating pull request: {str(e)}")
            return False

    def run_pipeline(self) -> bool:
        """Execute the complete security pipeline"""
        try:
            # Architecture review with o1-preview
            review_results = self.run_architecture_review()
            
            # Run initial security checks
            security_results = self.run_security_checks()
            
            # Check if fixes are needed
            max_severity = max(
                self._get_max_severity(result)
                for check_type in security_results.values()
                for result in check_type
            )
            
            if max_severity >= self.critical_threshold:
                # Create fix branch
                if not self.create_fix_branch():
                    return False
                
                # Implement fixes
                fix_attempts = 0
                while fix_attempts < self.max_fix_attempts:
                    if self.implement_fixes(review_results.get('suggestions', [])):
                        if self.validate_fixes():
                            break
                    fix_attempts += 1
                
                # Create PR if fixes were successful
                if fix_attempts < self.max_fix_attempts:
                    return self.create_pull_request()
                else:
                    print("Max fix attempts reached without success")
                    return False
            
            print("No critical vulnerabilities found")
            return True
            
        except Exception as e:
            print(f"Pipeline failed: {str(e)}")
            return False

    def validate_fixes(self) -> bool:
        """Validate implemented fixes"""
        print("Validating fixes...")
        
        # Re-run security checks
        results = self.run_security_checks()
        
        # Check if any critical vulnerabilities remain
        for check_type, check_results in results.items():
            for result in check_results:
                if self._get_max_severity(result) >= self.critical_threshold:
                    return False
        
        return True