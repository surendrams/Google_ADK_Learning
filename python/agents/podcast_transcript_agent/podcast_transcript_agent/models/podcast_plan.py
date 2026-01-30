from typing import List
from pydantic import BaseModel
from podcast_transcript_agent.models.podcast_transcript import PodcastSpeaker


class Segment(BaseModel):
    """A model for a 'main_segment', which includes a title."""

    title: str
    script_points: List[str]


class PodcastEpisodePlan(BaseModel):
    """Represents the entire episode, containing a title and a list of segments."""

    episode_title: str
    speakers: List[PodcastSpeaker]
    segments: List[Segment]
