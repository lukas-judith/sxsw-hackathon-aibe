from pydantic import BaseModel


class Responsibility(BaseModel):
    name: str
    description: str


class ExtractResponsibilitiesOutput(BaseModel):
    responsibilities: list[Responsibility]


class ExtractResponsibilitiesRequest(BaseModel):
    text: str


class ExtractResponsibilitiesResponse(BaseModel):
    responsibilities: list[Responsibility]
    reasoning: str
