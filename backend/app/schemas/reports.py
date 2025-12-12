from uuid import UUID
from typing import List
from pydantic import BaseModel


class UnmappedRequirement(BaseModel):
    """
    Represents a regulatory requirement that has no mapped controls.
    """
    requirement_id: UUID
    requirement_name: str
    requirement_description: str | None = None
    framework_name: str


class GapAnalysisReport(BaseModel):
    """
    Structured gap analysis report for a regulatory framework.
    """
    framework_id: UUID
    framework_name: str
    total_requirements: int
    mapped_requirements: int
    unmapped_requirements: int
    coverage_percentage: float
    gaps: List[UnmappedRequirement]
