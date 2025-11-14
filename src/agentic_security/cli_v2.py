"""
Agentic Security v2.0 CLI Commands

Enhanced CLI with learning, AI protection, and multi-agent features.
"""

import click
import asyncio
import logging
from rich.console import Console
from rich.table import Table
from pathlib import Path

from .v2 import (
    SecurityPipelineV2,
    AIDefenceClient,
    AgentDBClient,
    MultiAgentCoordinator
)

console = Console()
logger = logging.getLogger(__name__)


@click.group(name='v2')
def v2_cli():
    """Agentic Security v2.0 commands"""
    pass


@v2_cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--learn', is_flag=True, help='Enable learning mode')
@click.option('--auto-fix', is_flag=True, help='Automatically apply fixes')
@click.option('--config', default='config.yml', help='Configuration file')
def analyze(path, learn, auto_fix, config):
    """Analyze code with v2.0 learning capabilities"""
    async def _analyze():
        console.print(f"\n[cyan]🔍 Agentic Security v2.0 Analysis[/cyan]\n")

        # Initialize pipeline
        pipeline = SecurityPipelineV2(config_file=config)
        await pipeline.initialize()

        try:
            # Run scan
            results = await pipeline.scan_with_learning(
                target=path,
                use_history=learn,
                auto_fix=auto_fix
            )

            # Display results
            console.print(f"\n[bold]Scan Results:[/bold]")
            console.print(f"  Vulnerabilities: {len(results.get('vulnerabilities', []))}")
            console.print(f"  Fixes Applied: {len(results.get('fixes', []))}")
            console.print(f"  Learning Reward: {results.get('reward', 0):.2f}")
            console.print(f"  Duration: {results.get('duration', 0):.1f}s")

            if learn:
                console.print(f"\n[green]✓[/green] Episode stored for learning")

        finally:
            await pipeline.shutdown()

    asyncio.run(_analyze())


@v2_cli.group()
def learn():
    """Learning and memory commands"""
    pass


@learn.command(name='query')
@click.argument('query')
@click.option('--k', default=5, help='Number of results')
@click.option('--db', default='./agentdb.db', help='Database path')
def learn_query(query, k, db):
    """Query past experiences"""
    async def _query():
        agentdb = AgentDBClient(db)

        console.print(f"\n[cyan]🔍 Querying: {query}[/cyan]\n")

        results = await agentdb.semantic_query(
            query=query,
            k=k,
            synthesize_context=True
        )

        # Display results
        episodes = results.get('episodes', [])
        console.print(f"[bold]Found {len(episodes)} relevant experiences:[/bold]\n")

        for i, episode in enumerate(episodes[:5], 1):
            console.print(f"{i}. Task: {episode.get('task')}")
            console.print(f"   Reward: {episode.get('reward', 0):.2f}")
            console.print(f"   Success: {'✓' if episode.get('success') else '✗'}")
            console.print()

        if results.get('synthesized_context'):
            console.print(f"[bold]Context Summary:[/bold]")
            console.print(results['synthesized_context'])

    asyncio.run(_query())


@learn.command(name='stats')
@click.option('--db', default='./agentdb.db', help='Database path')
def learn_stats(db):
    """Show learning statistics"""
    async def _stats():
        agentdb = AgentDBClient(db)
        stats = await agentdb.get_stats()

        console.print("\n[bold cyan]Learning Statistics[/bold cyan]\n")

        table = Table()
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        for key, value in stats.items():
            table.add_row(key, str(value))

        console.print(table)

    asyncio.run(_stats())


@v2_cli.group()
def protect():
    """AIDefence protection commands"""
    pass


@protect.command(name='start')
@click.option('--port', default=3000, help='Server port')
@click.option('--host', default='0.0.0.0', help='Server host')
def protect_start(port, host):
    """Start AIDefence gateway server"""
    async def _start():
        aidefence = AIDefenceClient()

        console.print(f"\n[cyan]🛡️  Starting AIDefence Gateway[/cyan]\n")

        info = await aidefence.start_server(port=port, host=host)

        console.print(f"[green]✓[/green] Server started")
        console.print(f"  URL: {info['url']}")
        console.print(f"  PID: {info['pid']}")
        console.print("\nPress Ctrl+C to stop...\n")

        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            await aidefence.stop_server()
            console.print("\n[yellow]Server stopped[/yellow]")

    asyncio.run(_start())


@protect.command(name='check')
@click.argument('text')
@click.option('--deep', is_flag=True, help='Deep analysis')
def protect_check(text, deep):
    """Check text for threats"""
    async def _check():
        aidefence = AIDefenceClient()

        if deep:
            result = await aidefence.analyze(text, deep=True)
        else:
            result = await aidefence.detect(text)

        console.print(f"\n{result}")

        if result.is_threat:
            console.print(f"\n[red]⚠  Threat Details:[/red]")
            console.print(f"  Type: {result.threat_type}")
            console.print(f"  Confidence: {result.confidence:.1%}")
            if result.patterns_matched:
                console.print(f"  Patterns: {', '.join(result.patterns_matched)}")

    asyncio.run(_check())


@v2_cli.group()
def skills():
    """Skill library management"""
    pass


@skills.command(name='list')
@click.option('--db', default='./agentdb.db', help='Database path')
def skills_list(db):
    """List all skills"""
    async def _list():
        agentdb = AgentDBClient(db)

        # Search for all skills
        skills = await agentdb.search_skills("", k=100)

        console.print(f"\n[bold]Skill Library ({len(skills)} skills):[/bold]\n")

        table = Table()
        table.add_column("#", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Description")
        table.add_column("Usage", justify="right")

        for i, skill in enumerate(skills, 1):
            table.add_row(
                str(i),
                skill.get('name', 'Unknown'),
                skill.get('description', '')[:50] + '...',
                str(skill.get('usage_count', 0))
            )

        console.print(table)

    asyncio.run(_list())


@skills.command(name='search')
@click.argument('query')
@click.option('--k', default=5, help='Number of results')
@click.option('--db', default='./agentdb.db', help='Database path')
def skills_search(query, k, db):
    """Search for skills"""
    async def _search():
        agentdb = AgentDBClient(db)

        console.print(f"\n[cyan]🔍 Searching skills: {query}[/cyan]\n")

        skills = await agentdb.search_skills(query, k=k)

        for i, skill in enumerate(skills, 1):
            console.print(f"{i}. [bold]{skill.get('name')}[/bold]")
            console.print(f"   {skill.get('description')}")
            console.print(f"   Success Rate: {skill.get('success_rate', 0):.1%}")
            console.print(f"   Times Used: {skill.get('usage_count', 0)}")
            console.print()

    asyncio.run(_search())


@skills.command(name='consolidate')
@click.option('--min-attempts', default=3, help='Minimum attempts')
@click.option('--min-reward', default=0.7, help='Minimum reward')
@click.option('--db', default='./agentdb.db', help='Database path')
def skills_consolidate(min_attempts, min_reward, db):
    """Consolidate successful episodes into skills"""
    async def _consolidate():
        agentdb = AgentDBClient(db)

        console.print(f"\n[cyan]🔧 Consolidating skills...[/cyan]\n")

        results = await agentdb.consolidate_skills(
            min_attempts=min_attempts,
            min_reward=min_reward,
            extract_patterns=True
        )

        skills_created = len(results.get('skills', []))
        console.print(f"[green]✓[/green] Created {skills_created} new skills")

    asyncio.run(_consolidate())


@v2_cli.group()
def sync():
    """Multi-agent synchronization"""
    pass


@sync.command(name='start')
@click.option('--port', default=4433, help='Server port')
def sync_start(port):
    """Start sync server"""
    async def _start():
        coordinator = MultiAgentCoordinator()

        console.print(f"\n[cyan]🔄 Starting Sync Server[/cyan]\n")

        info = await coordinator.start_sync_server(port=port)

        console.print(f"[green]✓[/green] Sync server started on port {port}")
        console.print("\nPress Ctrl+C to stop...\n")

        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            await coordinator.stop_sync_server()
            console.print("\n[yellow]Server stopped[/yellow]")

    asyncio.run(_start())


@sync.command(name='push')
@click.option('--server', required=True, help='Server address (host:port)')
@click.option('--incremental', is_flag=True, default=True, help='Incremental sync')
def sync_push(server, incremental):
    """Push changes to sync server"""
    async def _push():
        coordinator = MultiAgentCoordinator()

        console.print(f"\n[cyan]⬆️  Pushing to {server}[/cyan]\n")

        success = await coordinator.sync_push(server, incremental=incremental)

        if success:
            console.print(f"[green]✓[/green] Successfully pushed changes")
        else:
            console.print(f"[red]✗[/red] Push failed")

    asyncio.run(_push())


@sync.command(name='pull')
@click.option('--server', required=True, help='Server address (host:port)')
@click.option('--incremental', is_flag=True, default=True, help='Incremental sync')
def sync_pull(server, incremental):
    """Pull changes from sync server"""
    async def _pull():
        coordinator = MultiAgentCoordinator()

        console.print(f"\n[cyan]⬇️  Pulling from {server}[/cyan]\n")

        success = await coordinator.sync_pull(server, incremental=incremental)

        if success:
            console.print(f"[green]✓[/green] Successfully pulled changes")
        else:
            console.print(f"[red]✗[/red] Pull failed")

    asyncio.run(_pull())


# Add v2 commands to main CLI
def register_v2_commands(main_cli):
    """Register v2 commands with main CLI"""
    main_cli.add_command(v2_cli)
