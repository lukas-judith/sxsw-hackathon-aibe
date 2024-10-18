import uuid
from pydantic import BaseModel, Field

from typing import List, Union, Optional


class Responsibility(BaseModel):
    id: str = Field(
        ...,
        default_factory=lambda: str(uuid.uuid4()),
        description="The random unique identifier for the responsibility.",
    )
    name: str
    description: str


class ExtractResponsibilitiesOutput(BaseModel):
    responsibilities: list[Responsibility]


class ExtractResponsibilitiesRequest(BaseModel):
    text: str


class ExtractResponsibilitiesResponse(BaseModel):
    responsibilities: list[Responsibility]
    reasoning: str


class ResponsibilitiesFullfilledStatus(BaseModel):
    id: str
    name_responsibility: str
    fulfilled: Union[bool, None]
    comment: str


class CheckResponsibilitiesRequest(BaseModel):
    transcript: str
    all_responsibilities: list[Responsibility]


class CheckResponsibilitiesResponse(BaseModel):
    responsibilities_fulfilled: list[ResponsibilitiesFullfilledStatus]
    reasoning: str
