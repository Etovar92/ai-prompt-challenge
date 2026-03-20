import asyncio
import logging
import sys
from typing import Any

from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

from .auth import get_access_token
from .graph import GraphClient
from .models import Submission
from .settings import Settings

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)
console = Console()


async def _select_team(client: GraphClient, team_id: str) -> str:
    if team_id:
        return team_id
    teams = await client.get_joined_teams()
    console.print("\n[bold]📋 Select your Team:[/bold]")
    for i, t in enumerate(teams, 1):
        console.print(f"  [cyan]{i}.[/cyan] {t.display_name}")
    choice = int(Prompt.ask("Enter number")) - 1
    return teams[choice].team_id


async def _select_channel(
    client: GraphClient, team_id: str, channel_id: str
) -> str:
    if channel_id:
        return channel_id
    channels = await client.get_channels(team_id)
    console.print("\n[bold]📋 Select the Channel:[/bold]")
    for i, c in enumerate(channels, 1):
        console.print(f"  [cyan]{i}.[/cyan] {c.display_name}")
    choice = int(Prompt.ask("Enter number")) - 1
    return channels[choice].channel_id


async def _select_challenge_post(
    client: GraphClient, team_id: str, channel_id: str, message_id: str
) -> str:
    if message_id:
        return message_id
    messages = await client.get_messages(team_id, channel_id, limit=15)
    console.print("\n[bold]📋 Select the Challenge Post:[/bold]")
    for i, m in enumerate(messages[:10], 1):
        from_user: dict[str, Any] = (m.get("from") or {}).get("user") or {}
        author = from_user.get("displayName", "Unknown")
        preview = _strip_body(m.get("body", {}).get("content", ""), 70)
        console.print(f"  [cyan]{i}.[/cyan] [[dim]{author}[/dim]] {preview}")
    choice = int(Prompt.ask("Enter number")) - 1
    selected_id: str = messages[choice]["id"]
    console.print(
        f"\n[dim]💡 Tip: Add CHALLENGE_MESSAGE_ID={selected_id} to your .env to skip this step next time.[/dim]"
    )
    return selected_id


def _display_leaderboard(submissions: list[Submission]) -> None:
    table = Table(
        title="🏆  AI Prompt Challenge — Live Leaderboard",
        show_lines=True,
        header_style="bold magenta",
    )
    table.add_column("Rank", style="bold yellow", justify="center", width=6)
    table.add_column("Author", style="cyan", width=22)
    table.add_column("Prompt Preview", style="white", width=55)
    table.add_column("Reactions", justify="center", width=11)
    table.add_column("Score", style="bold green", justify="center", width=7)

    medals = {1: "🥇", 2: "🥈", 3: "🥉"}

    for i, sub in enumerate(submissions, 1):
        rank_label = medals.get(i, str(i))
        preview = sub.content[:60] + "…" if len(sub.content) > 60 else sub.content

        # Build reaction breakdown string e.g. "👍3  ❤️2"
        reaction_detail = "  ".join(
            f"{r.reaction_type} ×{r.count}" for r in sub.reactions
        ) or "—"

        table.add_row(
            rank_label,
            sub.author_name,
            preview,
            reaction_detail,
            str(sub.score),
        )

    console.print()
    console.print(table)
    console.print(
        f"[dim]  Total submissions: {len(submissions)}  |  "
        f"Score = total emoji reactions on your submission[/dim]\n"
    )


async def main() -> None:
    settings = Settings()

    console.rule("[bold green]🤖  AI Prompt Challenge Leaderboard[/bold green]")

    token = get_access_token(settings.azure_client_id, settings.azure_tenant_id)
    client = GraphClient(token)

    team_id = await _select_team(client, settings.teams_team_id)
    channel_id = await _select_channel(client, team_id, settings.teams_channel_id)
    message_id = await _select_challenge_post(
        client, team_id, channel_id, settings.challenge_message_id
    )

    console.print("\n[dim]⏳ Fetching submissions and reactions…[/dim]")
    submissions = await client.get_submissions(team_id, channel_id, message_id)

    if not submissions:
        console.print("[yellow]⚠️  No replies found on that post yet.[/yellow]")
        return

    _display_leaderboard(submissions)


def _strip_body(content: str, max_len: int) -> str:
    import re

    text = re.sub(r"<[^>]+>", "", content).strip().replace("\n", " ")
    return text[:max_len] + "…" if len(text) > max_len else text


def run() -> None:
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[dim]Cancelled.[/dim]")
        sys.exit(0)


if __name__ == "__main__":
    run()
