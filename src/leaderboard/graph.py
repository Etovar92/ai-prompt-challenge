import logging
import re
from datetime import datetime
from typing import Any

import httpx

from .models import Channel, ReactionSummary, Submission, Team

logger = logging.getLogger(__name__)

BASE_URL = "https://graph.microsoft.com/v1.0"
_TIMEOUT = 30.0


class GraphClient:
    def __init__(self, token: str) -> None:
        self._headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    async def get_joined_teams(self) -> list[Team]:
        data = await self._get("/me/joinedTeams")
        return [
            Team(team_id=t["id"], display_name=t["displayName"])
            for t in data.get("value", [])
        ]

    async def get_channels(self, team_id: str) -> list[Channel]:
        data = await self._get(f"/teams/{team_id}/channels")
        return [
            Channel(channel_id=c["id"], display_name=c["displayName"])
            for c in data.get("value", [])
        ]

    async def get_messages(
        self, team_id: str, channel_id: str, limit: int = 25
    ) -> list[dict[str, Any]]:
        data = await self._get(
            f"/teams/{team_id}/channels/{channel_id}/messages",
            params={"$top": limit},
        )
        return data.get("value", [])

    async def get_replies(
        self, team_id: str, channel_id: str, message_id: str
    ) -> list[dict[str, Any]]:
        data = await self._get(
            f"/teams/{team_id}/channels/{channel_id}/messages/{message_id}/replies"
        )
        return data.get("value", [])

    async def get_submissions(
        self, team_id: str, channel_id: str, challenge_message_id: str
    ) -> list[Submission]:
        """Fetch all replies to the challenge post and rank them by reactions."""
        logger.info(
            "Fetching replies for message %s in channel %s",
            challenge_message_id,
            channel_id,
        )
        replies = await self.get_replies(team_id, channel_id, challenge_message_id)
        submissions = [self._parse_submission(r) for r in replies]
        submissions.sort(key=lambda s: s.score, reverse=True)
        return submissions

    def _parse_submission(self, msg: dict[str, Any]) -> Submission:
        reaction_map: dict[str, int] = {}
        for r in msg.get("reactions", []):
            rtype = r.get("reactionType", "unknown")
            reaction_map[rtype] = reaction_map.get(rtype, 0) + 1

        reactions = [
            ReactionSummary(reaction_type=k, count=v)
            for k, v in reaction_map.items()
        ]

        from_user = (msg.get("from") or {}).get("user") or {}

        return Submission(
            message_id=msg["id"],
            author_name=from_user.get("displayName", "Unknown"),
            author_id=from_user.get("id", ""),
            content=_strip_html(msg.get("body", {}).get("content", "")),
            created_at=datetime.fromisoformat(
                msg["createdDateTime"].replace("Z", "+00:00")
            ),
            reactions=reactions,
        )

    async def _get(
        self, path: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        url = f"{BASE_URL}{path}"
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            response = await client.get(url, headers=self._headers, params=params)
            response.raise_for_status()
            result: dict[str, Any] = response.json()
            return result


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text).strip()
