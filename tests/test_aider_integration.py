import pytest
import os
import yaml
import time
import sys
import random
import subprocess
import shutil
from pathlib import Path
from typing import Optional, Tuple
from unittest.mock import Mock, patch

# Cyberpunk styling
CYAN = '\033[0;36m'
MAGENTA = '\033[0;35m'
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[0;33m'
NC = '\033[0m'
BOLD = '\033[1m'
DIM = '\033[2m'

CYBER_BANNER = f"""
{CYAN}
    █████╗ ██╗██████╗ ███████╗██████╗ 
   ██╔══██╗██║██╔══██╗██╔════╝██╔══██╗
   ███████║██║██║  ██║█████╗  ██████╔╝
   ██╔══██║██║██║  ██║██╔══╝  ██╔══██╗
   ██║  ██║██║██████╔╝███████╗██║  ██║
   ╚═╝  ╚═╝╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝
{MAGENTA}████████╗███████╗███████╗████████╗███████╗
╚══██╔══╝██╔════╝██╔════╝╚══██╔══╝██╔════╝
   ██║   █████╗  ███████╗   ██║   ███████╗
   ██║   ██╔══╝  ╚════██║   ██║   ╚════██║
   ██║   ███████╗███████║   ██║   ███████║
   ╚═╝   ╚══════╝╚══════╝   ╚═╝   ╚══════╝{NC}

{CYAN}[ Aider Integration Test Suite ]{NC}
{MAGENTA}[ Validating AI-Powered Code Analysis ]{NC}

{DIM}Initializing Aider communication protocols...{NC}
"""

def verify_aider_installation():
    """Verify or install Aider"""
    try:
        import aider
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "aider-chat"], check=True)

def run_aider_command(command: str, files: list, config_file: Path = None, auto_approve: bool = True, timeout: int = 120) -> tuple:
    """Run an Aider command and return the result"""
    try:
        # Find aider executable
        aider_path = shutil.which('aider')
        if not aider_path:
            verify_aider_installation()
            aider_path = shutil.which('aider')
            if not aider_path:
                raise RuntimeError("Aider not found even after installation")
            
        # Check if all files exist
        for file in files:
            if not os.path.exists(file):
                raise RuntimeError(f"No such file or directory: {file}")
            
        cmd = [aider_path]
        
        # Add CLI mode flags
        cmd.extend([
            "--yes-always", 
            "--no-stream",
            "--auto-commits",
            "--model", "gpt-4",  # Use standard model name
            "--commit-prompt", "[SECURITY] {msg}"  # Use commit-prompt instead
        ])
        
        # Add message
        if command:
            cmd.extend(["--message", command])
            
        # Add files with --file flag
        for file in files:
            cmd.extend(["--file", file])
        
        # Start process with environment
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(Path(files[0]).parent) if files else None
        )
        
        # Wait for completion with timeout
        stdout, stderr = process.communicate(timeout=timeout)
        
        if process.returncode != 0:
            raise RuntimeError(f"Aider command failed: {stderr}")
                
        return process.returncode, stdout, stderr
        
    except subprocess.TimeoutExpired:
        if 'process' in locals():
            process.kill()
        raise TimeoutError(f"Aider command timed out after {timeout} seconds")
    except Exception as e:
        raise RuntimeError(str(e))

def animate_loading(message, duration=0.5):
    """Show cyberpunk-styled loading animation"""
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    start_time = time.time()
    i = 0
    
    while time.time() - start_time < duration:
        sys.stdout.write(f"\r{CYAN}[{frames[i % len(frames)]}]{NC} {message}")
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1
    
    sys.stdout.write(f"\r{GREEN}[✓]{NC} {message}\n")
    sys.stdout.flush()

def print_section(name):
    """Print cyberpunk-styled section header"""
    print(f"\n{CYAN}╔{'═' * 50}╗{NC}")
    print(f"{CYAN}║{NC} {BOLD}{name}{' ' * (49 - len(name))}{CYAN}║{NC}")
    print(f"{CYAN}╠{'═' * 50}╣{NC}")
    print(f"{CYAN}║{NC} {DIM}Initializing test sequence...{' ' * 25}{CYAN}║{NC}")
    print(f"{CYAN}╚{'═' * 50}╝{NC}\n")

@pytest.fixture(autouse=True)
def setup_environment():
    """Setup test environment"""
    required_vars = ['OPENAI_API_KEY']
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        pytest.skip(f"Missing required environment variables: {', '.join(missing)}")
    
    # Ensure git is configured
    subprocess.run(["git", "config", "--global", "user.name", "Test User"])
    subprocess.run(["git", "config", "--global", "user.email", "test@example.com"])

@pytest.fixture
def test_repo(tmp_path):
    """Create a test repository with sample code"""
    animate_loading("Creating test repository")
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    
    # Initialize git repo
    subprocess.run(["git", "init"], cwd=repo_path, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_path, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_path, capture_output=True)
    
    # Copy sample files
    samples_dir = Path(__file__).parent / "samples"
    for sample_file in samples_dir.glob("*.py"):
        shutil.copy2(sample_file, repo_path)
    
    # Initial commit
    subprocess.run(["git", "add", "."], cwd=repo_path, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_path, capture_output=True)
    
    return repo_path

class TestAiderIntegration:
    """Test Aider integration with security pipeline"""
    
    def test_auto_approve_mode(self, test_repo):
        """Test Aider with auto-approve mode"""
        print_section("Auto-Approve Mode Tests")
        animate_loading("Testing auto-approve functionality")
        
        command = "Fix the SQL injection vulnerability in this code"
        returncode, stdout, stderr = run_aider_command(
            command=command,
            files=[str(test_repo / "app.py")],
            auto_approve=True
        )
        
        assert returncode == 0, f"Aider command failed: {stderr}"
        assert any(term in stdout.lower() for term in [
            "parameterized", 
            "prepared statement",
            "parameterize",
            "sql injection fix"
        ])
        
        # Verify changes were committed
        git_log = subprocess.run(
            ["git", "log", "--oneline"],
            cwd=test_repo,
            capture_output=True,
            text=True
        )
        assert "[SECURITY]" in git_log.stdout
        print(f"{GREEN}[✓]{NC} Auto-approve mode test passed")
    
    def test_security_scan_mode(self, test_repo):
        """Test Aider's security scanning capabilities"""
        print_section("Security Scan Tests")
        animate_loading("Testing security scanning")
        
        command = """
        Perform a security audit of this code and fix all vulnerabilities.
        Focus on:
        1. SQL Injection
        2. Command Injection
        3. XSS
        4. Input Validation
        """
        
        returncode, stdout, stderr = run_aider_command(
            command=command,
            files=[str(test_repo / "app.py"), str(test_repo / "auth.py"), str(test_repo / "api.py")],
            auto_approve=True
        )
        
        assert returncode == 0, f"Aider command failed: {stderr}"
        
        # Read updated files
        with open(test_repo / "app.py", "r") as f:
            app_code = f.read()
        with open(test_repo / "auth.py", "r") as f:
            auth_code = f.read()
        with open(test_repo / "api.py", "r") as f:
            api_code = f.read()
        
        # Check for security improvements
        security_checks = [
            ("SQL Injection", ["parameterize", "prepared", "placeholder"], app_code),
            ("Command Injection", ["subprocess.run", "shlex.quote", "escape"], app_code),
            ("XSS", ["escape", "sanitize", "html.escape"], app_code),
            ("Input Validation", ["validate", "sanitize", "check"], app_code),
            ("Password Storage", ["bcrypt", "argon2", "pbkdf2"], auth_code),
            ("Token Security", ["secrets", "uuid", "random"], auth_code),
            ("API Security", ["verify=True", "ssl", "tls"], api_code),
            ("XML Security", ["defusedxml", "disable_external_entities"], api_code)
        ]
        
        for issue, patterns, code in security_checks:
            found = any(pattern in code.lower() for pattern in patterns)
            if found:
                print(f"{GREEN}[✓]{NC} {issue} fixed")
            else:
                print(f"{RED}[!]{NC} {issue} not properly addressed")
                assert False, f"{issue} vulnerability not properly fixed"
    
    def test_error_handling(self, test_repo):
        """Test Aider's error handling"""
        print_section("Error Handling Tests")
        animate_loading("Testing error handling")
        
        # Test with nonexistent file
        with pytest.raises(RuntimeError) as exc_info:
            run_aider_command(
                command="Fix security issues",
                files=[str(test_repo / "nonexistent.py")],
                auto_approve=True
            )
        assert "No such file" in str(exc_info.value)
        print(f"{GREEN}[✓]{NC} Invalid file error handled")
        
        # Test with timeout
        with pytest.raises(TimeoutError):
            run_aider_command(
                command="Fix all possible security issues in great detail",
                files=[str(test_repo / "app.py")],
                auto_approve=True,
                timeout=1
            )
        print(f"{GREEN}[✓]{NC} Timeout error handled")

# Print completion banner
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    passed = len([i for i in terminalreporter.stats.get('passed', [])])
    failed = len([i for i in terminalreporter.stats.get('failed', [])])
    total = passed + failed
    
    # Calculate pass percentage
    pass_percentage = (passed / total) * 100 if total > 0 else 0
    
    # Create progress bar
    bar_length = 30
    filled_length = int(bar_length * pass_percentage / 100)
    bar = "█" * filled_length + "░" * (bar_length - filled_length)
    
    print(f"\n{CYAN}╔{'═' * 50}╗{NC}")
    print(f"{CYAN}║{NC} {BOLD}Aider Integration Test Complete{' ' * 24}{CYAN}║{NC}")
    print(f"{CYAN}╠{'═' * 50}╣{NC}")
    print(f"{CYAN}║{NC} Progress: {bar} {pass_percentage:0.1f}%{' ' * (6 - len(f'{pass_percentage:0.1f}'))}{CYAN}║{NC}")
    print(f"{CYAN}║{NC} Total Tests: {total}{' ' * (38 - len(str(total)))}{CYAN}║{NC}")
    print(f"{CYAN}║{NC} Passed: {GREEN}{passed}{NC}{' ' * (42 - len(str(passed)))}{CYAN}║{NC}")
    print(f"{CYAN}║{NC} Failed: {RED}{failed}{NC}{' ' * (42 - len(str(failed)))}{CYAN}║{NC}")
    print(f"{CYAN}╚{'═' * 50}╝{NC}")
    
    if failed == 0:
        print(f"\n{GREEN}[✓] All Aider integration tests completed successfully{NC}")
    else:
        print(f"\n{RED}[!] Aider integration tests detected {failed} failure(s){NC}")
    
    print(f"\n{DIM}End of test sequence. Aider systems disengaged.{NC}\n")