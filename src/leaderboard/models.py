from datetime import datetime

from pydantic import BaseModel, Field


class ReactionSummary(BaseModel):
    reaction_type: str
    count: int


class Submission(BaseModel):
    message_id: str
    author_name: str
    author_id: str
    content: str
    created_at: datetime
    reactions: list[ReactionSummary] = Field(default_factory=list)

    @property
    def reaction_count(self) -> int:
        return sum(r.count for r in self.reactions)

    @property
    def score(self) -> int:
        return self.reaction_count


class Team(BaseModel):
    team_id: str
    display_name: str


class Channel(BaseModel):
    channel_id: str
    display_name: str
