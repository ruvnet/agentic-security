#!/usr/bin/env python3

# Cyberpunk color scheme
COLORS = {
    "neon_blue": "\033[38;5;51m",
    "neon_pink": "\033[38;5;198m", 
    "neon_green": "\033[38;5;46m",
    "neon_yellow": "\033[38;5;226m",
    "neon_red": "\033[38;5;196m",
    "neon_purple": "\033[38;5;165m",
    "reset": "\033[0m",
    "bold": "\033[1m",
    "blink": "\033[5m"
}

# Cyberpunk decorators
DECORATORS = {
    "box_top": f"{COLORS['neon_blue']}╔{'═'*60}╗{COLORS['reset']}",
    "box_bottom": f"{COLORS['neon_blue']}╚{'═'*60}╝{COLORS['reset']}",
    "box_line": f"{COLORS['neon_blue']}║{COLORS['reset']}",
    "arrow": f"{COLORS['neon_pink']}[►]{COLORS['reset']}"
}

from datetime import datetime
from pathlib import Path
import click
import yaml
import os
import sys
import time
from dotenv import load_dotenv
from .security_pipeline import SecurityPipeline
from .fix_cycle import FixCycle
from typing import Optional

CYBER_BANNER = f"""
{COLORS['neon_blue']}
    █████╗  ██████╗ ███████╗███╗   ██╗████████╗██╗ ██████╗
   ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝██║██╔════╝
   ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║   ██║██║     
   ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║   ██║██║     
   ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║   ██║╚██████╗
   ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═╝ ╚═════╝
{COLORS['neon_pink']}   ███████╗███████╗ ██████╗██╗   ██╗██████╗ ██╗████████╗██╗   ██╗
   ██╔════╝██╔════╝██╔════╝██║   ██║██╔══██╗██║╚══██╔══╝╚██╗ ██╔╝
   ███████╗█████╗  ██║     ██║   ██║██████╔╝██║   ██║    ╚████╔╝ 
   ╚════██║██╔══╝  ██║     ██║   ██║██╔══██╗██║   ██║     ╚██╔╝  
   ███████║███████╗╚██████╗╚██████╔╝██║  ██║██║   ██║      ██║   
   ╚══════╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝   ╚═╝      ╚═╝   
{COLORS['reset']}
{COLORS['neon_purple']}[ {COLORS['blink']}AI-Powered Security Scanner & Auto-Fix Pipeline{COLORS['reset']}{COLORS['neon_purple']} ]{COLORS['reset']}
{COLORS['neon_green']}[ Created by rUv, cause he could. ]{COLORS['reset']}

"""

CYBER_HELP = """
\033[36m╔══════════════════════════════════════════════════════════════╗
║                     Available Commands                      ║
╚══════════════════════════════════════════════════════════════╝\033[0m

\033[35m[>] analyze\033[0m
    Analyze security issues and optionally implement fixes
    Usage: agentic-security analyze [--config CONFIG] [--auto-fix]

\033[35m[>] fix\033[0m
    Apply security fixes to specified files
    Usage: agentic-security fix [FILES] [--message MESSAGE] [--template TEMPLATE]

\033[35m[>] fix-from-report\033[0m
    Apply fixes based on a security report
    Usage: agentic-security fix-from-report REPORT_PATH [--min-severity LEVEL]

\033[36m╔══════════════════════════════════════════════════════════════╗
║                         Options                             ║
╚══════════════════════════════════════════════════════════════╝\033[0m

\033[35m--config, -c\033[0m
    Path to configuration file (default: config.yml)

\033[35m--path, -p\033[0m
    Paths to scan or review (can be specified multiple times)

\033[35m--output, -o\033[0m
    Output markdown report path

\033[35m--verbose, -v\033[0m
    Enable verbose output

\033[35m--auto-fix\033[0m
    Automatically apply fixes without prompting

\033[35m--template, -t\033[0m
    Use predefined fix template (sql|xss|injection|general)

\033[35m--min-severity\033[0m
    Minimum severity level to process (low|medium|high)

\033[35m--max-attempts\033[0m
    Maximum number of fix attempts (default: 3)

\033[35m--help\033[0m
    Show this cyberpunk-styled help message
"""

def print_cyber_status(message: str, status: str = "info") -> None:
    """Print cyberpunk-styled status messages"""
    status_styles = {
        "info": f"{COLORS['neon_blue']}{COLORS['bold']}",
        "success": f"{COLORS['neon_green']}{COLORS['bold']}",
        "warning": f"{COLORS['neon_yellow']}{COLORS['bold']}",
        "error": f"{COLORS['neon_red']}{COLORS['blink']}"
    }
    
    status_icons = {
        "info": "ℹ",
        "success": "✓",
        "warning": "⚠",
        "error": "✗"
    }
    
    color = status_styles.get(status, status_styles["info"])
    icon = status_icons.get(status, "►")
    
    print(f"{DECORATORS['box_line']} {color}{icon} {message}{COLORS['reset']}")

def load_config(config_file: str) -> dict:
    """Load configuration from file"""
    try:
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print_cyber_status(f"Config file not found: {config_file}", "error")
        return {}
    except yaml.YAMLError as e:
        print_cyber_status(f"Error parsing config file: {str(e)}", "error")
        return {}

def validate_environment() -> bool:
    """Validate required environment variables"""
    # Load environment variables from .env file securely
    load_dotenv(override=True)
    
    required_vars = ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print_cyber_status("Missing required environment variables:", "error")
        for var in missing_vars:
            print_cyber_status(f"  - {var}", "error")
        return False
    return True

class CyberpunkGroup(click.Group):
    def format_help(self, ctx, formatter):
        print(CYBER_BANNER)
        print(CYBER_HELP)

@click.group(cls=CyberpunkGroup)
def cyber_spinner():
    """Cyberpunk-styled spinner animation"""
    frames = [
        f"{COLORS['neon_purple']}◢{COLORS['reset']}",
        f"{COLORS['neon_blue']}◣{COLORS['reset']}",
        f"{COLORS['neon_pink']}◤{COLORS['reset']}",
        f"{COLORS['neon_green']}◥{COLORS['reset']}"
    ]
    return frames

@click.group(cls=CyberpunkGroup)
@click.option('--verbose/--no-verbose', '-v/', default=False, help='Verbose output')
def cli(verbose):
    """Agentic Security CLI - AI-powered security scanning and fixing pipeline"""
    pass


@cli.command()
@click.option('--path', '-p', multiple=True, help='Paths to analyze')
@click.option('--config', '-c', default='config.yml', help='Path to configuration file')
@click.option('--auto-fix/--no-auto-fix', default=False, help='Automatically implement fixes')
@click.option('--verbose/--no-verbose', '-v/', default=False, help='Verbose output')
def analyze(path: tuple, config: str, auto_fix: bool, verbose: bool):
    """Analyze security issues and optionally implement fixes"""
    try:
        print(CYBER_BANNER)
        if not validate_environment():
            sys.exit(1)
        
        print_cyber_status("Initializing security analysis...", "info")
        pipeline = SecurityPipeline(config)
        
        if not path:
            path = ['.']  # Default to current directory if no path specified
            
        # Run security analysis on specified paths
        results = pipeline.scan_paths(path, auto_fix=auto_fix)
        
        # Generate unique report filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_dir = Path('security_reports')
        report_dir.mkdir(exist_ok=True)
        report_file = report_dir / f'security_report_{timestamp}.md'
        
        # Generate the report
        pipeline.generate_review_report(results, str(report_file))
        print_cyber_status(f"\nSecurity report generated: {report_file}", "success")
        
        if verbose:
            print("\nAnalysis Results:")
            for vuln in results.get('vulnerabilities', []):
                print(f"\nFile: {vuln['file']}")
                print(f"Type: {vuln['type']}")
                print(f"Severity: {vuln['severity']}")
                if vuln.get('details', {}).get('description'):
                    print(f"Details: {vuln['details']['description']}")
        
        # Exit after completion
        sys.exit(0)
                
    except KeyboardInterrupt:
        print("\n\033[33m[!] Analysis interrupted. Saving partial results...\033[0m")
        # Still try to save the report if interrupted
        if 'results' in locals() and results:
            pipeline.generate_review_report(results, str(report_file))
            print_cyber_status(f"\nPartial report saved: {report_file}", "warning")
        sys.exit(1)
    except Exception as e:
        print_cyber_status(f"Error during analysis: {str(e)}", "error")
        sys.exit(1)


@cli.command()
@click.argument('paths', nargs=-1, type=click.Path(exists=True))
@click.option('--message', '-m', help='Custom security fix instructions')
@click.option('--max-attempts', default=3, type=int, help='Maximum fix attempts')
@click.option('--template', '-t', type=click.Choice(['sql', 'xss', 'injection', 'general']), 
              help='Use predefined fix template')
@click.option('--extensions', '-e', multiple=True, default=['.py'],
              help='File extensions to process (default: .py)')
@click.option('--verbose/--no-verbose', '-v/', default=False, help='Verbose output')
def fix(paths, message, max_attempts, template, extensions, verbose):
    """Apply security fixes to specified files or directories"""
    try:
        if not paths:
            print_cyber_status("No paths specified", "error")
            sys.exit(1)

        # Collect all files from provided paths
        all_files = []
        for path in paths:
            if os.path.isfile(path):
                if os.path.splitext(path)[1] in extensions:
                    all_files.append(path)
            else:  # Directory
                for root, _, files in os.walk(path):
                    for file in files:
                        if os.path.splitext(file)[1] in extensions:
                            all_files.append(os.path.join(root, file))

        if not all_files:
            print_cyber_status(f"No matching files found in specified paths. Looking for extensions: {', '.join(extensions)}", "error")
            sys.exit(1)

        print_cyber_status(f"Found {len(all_files)} files to process:", "info")
        for file in all_files:
            print_cyber_status(f"  - {file}", "info")

        # Template messages
        templates = {
            'sql': "Review and fix any SQL injection vulnerabilities. Ensure all database queries are properly parameterized.",
            'xss': "Fix cross-site scripting (XSS) vulnerabilities. Ensure all user input is properly escaped before output.",
            'injection': "Fix command injection vulnerabilities. Validate and sanitize all inputs used in system commands.",
            'general': "Review this code for security issues and propose fixes following security best practices."
        }

        # Use template message if specified, otherwise use custom message
        fix_message = templates.get(template) if template else message
        if not fix_message:
            fix_message = templates['general']

        print_cyber_status(f"Initiating fix cycle for {len(all_files)} files...", "info")
        print_cyber_status(f"Using fix message: {fix_message}", "info")

        fixer = FixCycle(
            files=all_files,
            message=fix_message,
            max_attempts=max_attempts,
            verbose=verbose
        )

        success = fixer.run_fix_cycle()
        
        if success:
            print_cyber_status("Fix cycle completed successfully", "success")
            sys.exit(0)
        else:
            print_cyber_status("Fix cycle failed", "error")
            sys.exit(1)

    except Exception as e:
        print_cyber_status(f"Error during fix cycle: {str(e)}", "error")
        sys.exit(1)

@cli.command()
@click.argument('report_path', type=click.Path(exists=True))
@click.option('--min-severity', type=click.Choice(['low', 'medium', 'high']), 
              help='Minimum severity level to process')
@click.option('--max-attempts', default=3, type=int, help='Maximum fix attempts')
def fix_from_report(report_path, min_severity, max_attempts):
    """Apply fixes based on a security report"""
    try:
        print_cyber_status(f"Processing security report: {report_path}", "info")
        
        fixer = FixCycle(
            report_path=report_path,
            max_attempts=max_attempts
        )

        success = fixer.run_fix_cycle(min_severity=min_severity)
        
        if success:
            print_cyber_status("Successfully applied fixes from report", "success")
            sys.exit(0)
        else:
            print_cyber_status("Failed to apply some fixes from report", "error")
            sys.exit(1)

    except Exception as e:
        print_cyber_status(f"Error processing security report: {str(e)}", "error")
        sys.exit(1)

@cli.command()
@click.option('--path', '-p', multiple=True, required=True, help='Paths to review')
@click.option('--config', '-c', default='config.yml', help='Path to configuration file')
@click.option('--output', '-o', default=None, help='Output markdown report path')
@click.option('--verbose/--no-verbose', '-v/', default=False, help='Verbose output')
def review(path: tuple, config: str, output: Optional[str], verbose: bool):
    """Review paths for security issues and generate a report"""
    try:
        print(CYBER_BANNER)
        print_cyber_status("Initializing security review...", "info")
        pipeline = SecurityPipeline(config)

        results = pipeline.review_paths(list(path), verbose=verbose)

        if output:
            pipeline.generate_review_report(results, output)
            print_cyber_status(f"Security review report generated: {output}", "success")
        else:
            print_cyber_status("Security Review", "info")
            pipeline.print_review_results(results, verbose=verbose)

        sys.exit(0)

    except Exception as e:
        print_cyber_status(f"Error during review: {str(e)}", "error")
        sys.exit(1)


if __name__ == '__main__':
    cli()
