import logging
from pathlib import Path

import msal
from rich.console import Console

logger = logging.getLogger(__name__)
console = Console()

SCOPES = [
    "https://graph.microsoft.com/ChannelMessage.Read.All",
    "https://graph.microsoft.com/Team.ReadBasic.All",
    "https://graph.microsoft.com/Channel.ReadBasic.All",
]

_CACHE_FILE = Path(".token_cache.json")


def _load_cache() -> msal.SerializableTokenCache:
    cache = msal.SerializableTokenCache()
    if _CACHE_FILE.exists():
        cache.deserialize(_CACHE_FILE.read_text(encoding="utf-8"))
    return cache


def _save_cache(cache: msal.SerializableTokenCache) -> None:
    if cache.has_state_changed:
        _CACHE_FILE.write_text(cache.serialize(), encoding="utf-8")


def get_access_token(client_id: str, tenant_id: str) -> str:
    """Authenticate via device code flow and return a Graph API access token."""
    cache = _load_cache()
    app = msal.PublicClientApplication(
        client_id,
        authority=f"https://login.microsoftonline.com/{tenant_id}",
        token_cache=cache,
    )

    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
        if result and "access_token" in result:
            logger.info("Using cached token for %s", accounts[0]["username"])
            _save_cache(cache)
            return result["access_token"]

    flow = app.initiate_device_flow(scopes=SCOPES)
    if "user_code" not in flow:
        raise RuntimeError(
            f"Failed to start device flow: {flow.get('error_description')}"
        )

    console.print("\n[bold cyan]🔐 Authentication required[/bold cyan]")
    console.print(f"   Visit: [bold underline]{flow['verification_uri']}[/bold underline]")
    console.print(
        f"   Enter code: [bold yellow]{flow['user_code']}[/bold yellow]\n"
    )
    console.print("[dim]Waiting for sign-in...[/dim]")

    result = app.acquire_token_by_device_flow(flow)
    if "access_token" not in result:
        raise RuntimeError(
            f"Authentication failed: {result.get('error_description', result.get('error'))}"
        )

    _save_cache(cache)
    logger.info("Authentication successful")
    return result["access_token"]
