"""Explicit demo contracts. None means unknown, never zero."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class CaseInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    patient_name: str = Field(max_length=100)
    dob: str = Field(max_length=20)
    member_id: str = Field(max_length=100)
    group_number: str = Field(max_length=100)
    procedure: str = Field(max_length=100)
    notes: str = Field(default="", max_length=2000)


class BenefitField(BaseModel):
    name: str
    value: str | None = None
    status: Literal["reported", "not_returned", "conflicting", "source_error"] = "not_returned"
    scope: str = "dental"
    evidence: list[str] = Field(default_factory=list)


class Guidance(BaseModel):
    source_id: str
    title: str
    text: str
    version: str


class Review(BaseModel):
    case: CaseInput
    source: str
    source_status: Literal["ok", "error", "not_supplied"]
    source_errors: list[str] = Field(default_factory=list)
    missing_fields: list[str]
    fields: list[BenefitField]
    questions: list[str]
    guidance: list[Guidance]
    review_status: Literal["Needs review", "Reviewed fictional example"] = "Needs review"
    provider: str = "Offline rules"
    model: str | None = None
    prompt_version: str = "review-v1"
    ai_status: str = "Not requested"
    selected_tool: str | None = None
    usage: dict = Field(default_factory=dict)
    latency_ms: int | None = None


class AIPriorities(BaseModel):
    """Only existing IDs/indices; model output cannot overwrite benefits."""
    model_config = ConfigDict(extra="forbid")
    guidance_ids: list[str]
    question_indices: list[int]
