"""Knowledge Agent schema definitions."""

from typing import List, Optional

from pydantic import BaseModel, Field


class KnowledgeResult(BaseModel):
    """Result of a knowledge query."""

    query: str = Field(description="Original user query")
    answer: str = Field(description="Generated answer based on retrieved knowledge")
    sources: List[dict] = Field(default=[], description="Source documents used")
