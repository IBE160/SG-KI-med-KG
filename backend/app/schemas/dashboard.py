"""Dashboard data schemas for role-specific metrics and cards."""

from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID


class DashboardCard(BaseModel):
    """Single card data for Action-Oriented Hub dashboard.

    Represents a modular dashboard card displaying a key metric
    with an actionable link for the user to drill down.
    """
    card_id: str = Field(..., description="Unique identifier for the card type")
    title: str = Field(..., description="Display title for the card")
    metric: int = Field(..., description="Primary numeric metric to display")
    metric_label: str = Field(..., description="Label for the metric (e.g., 'items', 'risks')")
    icon: str = Field(..., description="Icon identifier for frontend rendering")
    action_link: str = Field(..., description="URL for the card's CTA button")
    status: Optional[str] = Field(None, description="Optional status indicator (e.g., 'urgent', 'normal')")

    class Config:
        json_schema_extra = {
            "example": {
                "card_id": "pending_reviews",
                "title": "Pending Reviews",
                "metric": 5,
                "metric_label": "items",
                "icon": "clipboard-check",
                "action_link": "/dashboard/bpo/reviews",
                "status": "urgent"
            }
        }


class DashboardMetrics(BaseModel):
    """Complete dashboard data feed for a specific user role.

    Contains all cards that should be displayed on the user's
    personalized Action-Oriented Hub dashboard.
    """
    user_role: str = Field(..., description="User's role (admin, bpo, executive, general)")
    cards: List[DashboardCard] = Field(..., description="List of dashboard cards for this role")

    class Config:
        json_schema_extra = {
            "example": {
                "user_role": "bpo",
                "cards": [
                    {
                        "card_id": "pending_reviews",
                        "title": "Pending Reviews",
                        "metric": 5,
                        "metric_label": "items",
                        "icon": "clipboard-check",
                        "action_link": "/dashboard/bpo/reviews"
                    },
                    {
                        "card_id": "my_controls",
                        "title": "My Controls",
                        "metric": 12,
                        "metric_label": "controls",
                        "icon": "shield",
                        "action_link": "/dashboard/controls"
                    }
                ]
            }
        }


class OverviewControl(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    type: Optional[str] = None

class OverviewRisk(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    category: Optional[str] = None

class OverviewProcess(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    controls: List[OverviewControl] = []
    risks: List[OverviewRisk] = []

class OverviewResponse(BaseModel):
    processes: List[OverviewProcess]