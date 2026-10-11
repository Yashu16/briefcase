from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class Topic(str, Enum):
    company = "company"
    role_fit = "role_fit"
    interview = "interview"
    comp = "comp"
    sponsorship = "sponsorship"


class JobPosting(BaseModel):
    company: str
    title: str
    location: str = ""
    requirements: list[str] = Field(default_factory=list)
    raw_url: Optional[str] = None
    source_text: str = ""
    company_domain: Optional[str] = None


class ResearchQuestion(BaseModel):
    id: str
    topic: Topic
    prompt: str


class Evidence(BaseModel):
    claim: str
    source_url: str
    source_name: str
    snippet: str
    credibility: float = Field(ge=0.0, le=1.0, description="Prior by source type")
    question_id: str = ""


class Verdict(BaseModel):
    claim: str
    verdict: str
    confidence: float = Field(ge=0.0, le=1.0)
    rationale: str
    sources: list[str] = Field(default_factory=list)
    dissent: Optional[str] = None
    topic: Optional[Topic] = None


class UnverifiedClaim(BaseModel):
    claim: str
    source_url: str
    reason: str


class Brief(BaseModel):
    markdown: str
    verdicts: list[Verdict] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    unverified_claims: list[UnverifiedClaim] = Field(default_factory=list)


class PipelineState(BaseModel):
    run_id: str
    posting: Optional[JobPosting] = None
    questions: list[ResearchQuestion] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    verdicts: list[Verdict] = Field(default_factory=list)
    brief: Optional[Brief] = None
    use_priors: bool = True
    recovered_from: list[str] = Field(default_factory=list)
